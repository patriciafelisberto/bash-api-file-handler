from django.contrib import admin
from django.utils import timezone
from core.models import StoredFile


class StoredFileAdmin(admin.ModelAdmin):
    """
    Custom configuration for the StoredFile model in Django Admin.
    """
    list_display = ('filename', 'upload_date', 'created_at', 'updated_at', 'deleted_at', 'is_deleted')
    list_filter = ('deleted_at', 'upload_date', 'created_at')
    search_fields = ('filename',)
    readonly_fields = ('upload_date', 'created_at', 'updated_at')
    actions = ['soft_delete', 'restore', 'hard_delete']

    def is_deleted(self, obj):
        """
        Returns True if the record is marked as deleted (soft delete).
        """
        return obj.deleted_at is not None
    is_deleted.boolean = True  # Displays as an icon in the admin
    is_deleted.short_description = 'Deleted'

    def soft_delete(self, request, queryset):
        """
        Custom action to perform a soft delete on the selected records.
        """
        queryset.update(deleted_at=timezone.now())
        self.message_user(request, f"{queryset.count()} records marked as deleted.")

    def restore(self, request, queryset):
        """
        Custom action to restore soft-deleted records.
        """
        queryset.update(deleted_at=None)
        self.message_user(request, f"{queryset.count()} records restored.")

    def hard_delete(self, request, queryset):
        """
        Custom action to permanently delete the selected records.
        """
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count} records permanently deleted.")


# Registers the StoredFile model with the custom configuration in Django Admin
admin.site.register(StoredFile, StoredFileAdmin)
