from django.utils.timezone import now
from django.contrib.admin.sites import AdminSite
from django.test import TestCase, RequestFactory

from core.models import StoredFile
from core.admin import StoredFileAdmin


class MockRequest:
    """Mock request for admin actions."""
    def __init__(self, user):
        self.user = user

class StoredFileAdminTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = StoredFileAdmin(StoredFile, self.site)

        self.file1 = StoredFile.objects.create(filename="file1.txt", upload_date=now())
        self.file2 = StoredFile.objects.create(filename="file2.txt", upload_date=now(), deleted_at=now())
        
        self.request = RequestFactory().get('/')

    def test_is_deleted(self):
        """Test the is_deleted method."""
        self.assertFalse(self.admin.is_deleted(self.file1))
        self.assertTrue(self.admin.is_deleted(self.file2))

    def test_list_display(self):
        """Test the list_display configuration."""
        expected_display = ('filename', 'upload_date', 'created_at', 'updated_at', 'deleted_at', 'is_deleted')
        self.assertEqual(self.admin.list_display, expected_display)

    def test_list_filter(self):
        """Test the list_filter configuration."""
        expected_filters = ('deleted_at', 'upload_date', 'created_at')
        self.assertEqual(self.admin.list_filter, expected_filters)

    def test_search_fields(self):
        """Test the search_fields configuration."""
        expected_search_fields = ('filename',)
        self.assertEqual(self.admin.search_fields, expected_search_fields)

    def test_readonly_fields(self):
        """Test the readonly_fields configuration."""
        expected_readonly_fields = ('upload_date', 'created_at', 'updated_at')
        self.assertEqual(self.admin.readonly_fields, expected_readonly_fields)
