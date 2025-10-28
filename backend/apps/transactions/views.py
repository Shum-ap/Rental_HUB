import logging
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from apps.transactions.models import Transaction
from apps.transactions.serializers import TransactionSerializer

logger = logging.getLogger("log_views")


class TransactionViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing transactions.
    - Admins can view all transactions.
    - Regular users can only view and create their own transactions.
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Restrict queryset based on user type:
        - Admin/staff users see all transactions.
        - Regular users see only their own.
        """
        try:
            user = self.request.user
            if user.is_staff:
                logger.info("Admin %s retrieved all transactions.", user)
                return Transaction.objects.all()

            logger.info("User %s retrieved their own transactions.", user)
            return Transaction.objects.filter(user=user)

        except Exception as e:
            logger.error("Error retrieving transactions queryset: %s", e, exc_info=True)
            return Transaction.objects.none()

    def perform_create(self, serializer):
        """
        Automatically attach the current user to a newly created payment.
        """
        try:
            payment = serializer.save(user=self.request.user)
            logger.info(
                "Transaction created successfully (ID=%s) by user %s", payment.id, self.request.user
            )
        except Exception as e:
            logger.error("Error creating payment by user %s: %s", self.request.user, e, exc_info=True)
            raise

    def create(self, request, *args, **kwargs):
        """Handle POST /api/v1/transactions/ with error handling and logging."""
        try:
            response = super().create(request, *args, **kwargs)
            logger.info("Transaction created via API by user %s", request.user)
            return response
        except Exception as e:
            logger.error("Error during payment creation: %s", e, exc_info=True)
            return Response({"detail": "Error creating payment."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        """Handle DELETE /api/v1/transactions/<id>/ — with logging."""
        try:
            payment = self.get_object()
            response = super().destroy(request, *args, **kwargs)
            logger.warning("Transaction ID %s deleted by user %s", payment.id, request.user)
            return response
        except Exception as e:
            logger.error("Error deleting payment: %s", e, exc_info=True)
            return Response({"detail": "Error deleting payment."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
