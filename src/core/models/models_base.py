from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    """
    A custom QuerySet that implements soft delete.
    """
    def delete(self):
        """
        Soft delete: Sets 'deleted_at' to the current date and time.
        """
        return super().update(deleted_at=timezone.now())

    def hard_delete(self):
        """
        Hard delete: Permanently removes records from the database.
        """
        return super().delete()

    def alive(self):
        """
        Returns undeleted records (deleted_at is null).
        """
        return self.filter(deleted_at__isnull=True)

    def dead(self):
        """
        Returns deleted records (deleted_at is not null).
        """
        return self.filter(deleted_at__isnull=False)


class BaseModel(models.Model):
    """
    An abstract base model with soft delete support.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteQuerySet.as_manager()

    def delete(self):
        """
        Soft delete: Marks the record as deleted.
        """
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self):
        """
        Hard delete: Permanently removes the record from the database.
        """
        super().delete()

    def restore(self):
        """
        Restores a deleted record (soft delete).
        """
        self.deleted_at = None
        self.save()

    class Meta:
        abstract = True
