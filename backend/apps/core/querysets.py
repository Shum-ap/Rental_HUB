from django.db import models


class SoftDeleteQuerySet(models.QuerySet):
    """
    Custom QuerySet that supports soft delete functionality.
    Provides helper methods for filtering and managing soft-deleted records.
    """

    def delete(self):
        """Soft deletes all objects in the queryset by setting 'is_deleted=True'."""
        try:
            return super().update(is_deleted=True)
        except Exception as e:
            raise RuntimeError(f"Failed to soft delete objects: {e}")

    def hard_delete(self):
        """Permanently deletes all objects from the database."""
        try:
            return super().delete()
        except Exception as e:
            raise RuntimeError(f"Failed to hard delete objects: {e}")

    def restore(self):
        """Restores all soft-deleted objects in the queryset."""
        return self.update(is_deleted=False, deleted_at=None)

    def alive(self):
        """Returns only active (non-deleted) objects."""
        return self.filter(is_deleted=False)

    def deleted(self):
        """Returns only soft-deleted objects."""
        return self.filter(is_deleted=True)

    def with_deleted(self):
        """Returns all objects, including soft-deleted ones."""
        return self.all()


class SoftDeleteManager(models.Manager):
    """
    Custom manager that uses SoftDeleteQuerySet as its base.
    By default, returns only non-deleted (alive) records.
    """

    def get_queryset(self):
        """Return only alive (non-deleted) objects by default."""
        return SoftDeleteQuerySet(self.model, using=self._db).alive()

    def with_deleted(self):
        """Include deleted records in queryset."""
        return SoftDeleteQuerySet(self.model, using=self._db).with_deleted()

    def deleted(self):
        """Return only deleted records."""
        return SoftDeleteQuerySet(self.model, using=self._db).deleted()
