import logging
from decimal import Decimal
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from apps.reservations.models import Reservation
from apps.core.models import SoftDeleteModel
from apps.core.querysets import SoftDeleteManager

User = get_user_model()
logger = logging.getLogger("log_views")


class TransactionStatus(models.TextChoices):
    """Available transaction statuses."""
    PENDING = "pending", _("Pending")
    SUCCESS = "success", _("Successful")
    FAILED = "failed", _("Failed")
    REFUNDED = "refunded", _("Refunded")


class Transaction(SoftDeleteModel):
    """
    Represents a user's transaction for a reservation.
    Handles automatic amount calculation, soft delete, validation, and logging.
    """

    reservation = models.OneToOneField(
        Reservation,
        on_delete=models.CASCADE,
        related_name="transaction",
        verbose_name=_("Reservation"),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name=_("User"),
    )
    amount_eur = models.DecimalField(
        _("Amount (€)"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[],
        help_text=_("Total amount of the transaction in euros."),
    )
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=TransactionStatus.choices,
        default=TransactionStatus.PENDING,
    )
    transaction_id = models.CharField(_("Transaction ID"), max_length=100, blank=True, null=True)
    payment_method = models.CharField(_("Transaction Method"), max_length=50, blank=True, null=True)
    paid_at = models.DateTimeField(_("Paid At"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SoftDeleteManager()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Transaction {self.id or 'N/A'} — {self.user.email} — {self.status}"

    # === Validation ===
    def clean(self):
        """Ensure transaction integrity."""
        if not self.reservation:
            raise ValidationError(_("Transaction must be linked to a reservation."))

        if self.reservation.user != self.user:
            raise ValidationError(_("Reservation and transaction must belong to the same user."))

        if self.amount_eur <= 0:
            raise ValidationError(_("Transaction amount must be positive."))

    # === Helpers ===
    def calculate_amount(self):
        """Automatically derive the payment amount from the related reservation."""
        if self.reservation and self.reservation.total_price_eur > 0:
            return Decimal(self.reservation.total_price_eur)
        return Decimal("0.00")

    # === Save ===
    def save(self, *args, **kwargs):
        """Validate, calculate, and log transaction save operations."""
        try:
            self.full_clean()

            if not self.amount_eur or self.amount_eur <= 0:
                self.amount_eur = self.calculate_amount()

            if self.status == TransactionStatus.SUCCESS and not self.paid_at:
                self.paid_at = timezone.now()

            super().save(*args, **kwargs)

            logger.info(
                "Transaction saved: user=%s reservation=%s status=%s amount=%.2f€",
                self.user.email,
                self.reservation.id,
                self.status,
                self.amount_eur,
            )

        except Exception as exc:
            logger.error("Error saving transaction (user=%s): %s", self.user.email, exc)
            raise

    # === Actions ===
    @transaction.atomic
    def mark_as_success(self, transaction_id=None):
        """Mark the transaction as successfully paid."""
        if self.status == TransactionStatus.SUCCESS:
            logger.warning("Transaction already marked as paid: %s", self)
            raise ValidationError(_("Transaction already completed."))

        self.status = TransactionStatus.SUCCESS
        self.transaction_id = transaction_id or f"TXN-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        self.paid_at = timezone.now()
        self.save(update_fields=["status", "transaction_id", "paid_at", "updated_at"])

        # Automatically mark reservation as completed if confirmed
        if hasattr(self.reservation, "mark_as_completed"):
            self.reservation.mark_as_completed()

        logger.info("Transaction marked as paid: %s", self)

    def mark_as_failed(self, reason=None):
        """Mark transaction as failed."""
        self.status = TransactionStatus.FAILED
        self.save(update_fields=["status", "updated_at"])
        logger.warning("Transaction failed (%s): %s", reason or "unknown", self)

    def refund(self, reason=None):
        """Mark transaction as refunded."""
        if self.status != TransactionStatus.SUCCESS:
            raise ValidationError(_("Only successful transactions can be refunded."))

        self.status = TransactionStatus.REFUNDED
        self.save(update_fields=["status", "updated_at"])
        logger.info("Transaction refunded (%s): %s", reason or "manual refund", self)

    def delete(self, *args, **kwargs):
        """Soft delete with logging."""
        try:
            super().delete(*args, **kwargs)
            logger.warning("Transaction deleted: %s", self)
        except Exception as exc:
            logger.error("Error deleting transaction (%s): %s", self, exc)
            raise
