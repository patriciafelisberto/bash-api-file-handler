from django.test import TestCase
from core.models import StoredFile
from django.utils import timezone


class BaseModelTestCase(TestCase):
    """
    Test case for the BaseModel functionality, which is inherited by StoredFile.
    """

    def setUp(self):
        self.file = StoredFile.objects.create(filename="testfile.txt")

    def test_creation(self):
        """
        Test that an object is created successfully.
        """
        self.assertIsNotNone(self.file.id)
        self.assertIsNotNone(self.file.created_at)
        self.assertIsNone(self.file.deleted_at)

    def test_soft_delete(self):
        """
        Test the soft delete functionality.
        """
        self.file.delete()
        self.file.refresh_from_db()
        self.assertIsNotNone(self.file.deleted_at)
        self.assertFalse(StoredFile.objects.alive().filter(id=self.file.id).exists())
        self.assertTrue(StoredFile.objects.dead().filter(id=self.file.id).exists())

    def test_restore(self):
        """
        Test that a soft-deleted object can be restored.
        """
        self.file.delete()
        self.file.restore()
        self.file.refresh_from_db()
        self.assertIsNone(self.file.deleted_at)
        self.assertTrue(StoredFile.objects.alive().filter(id=self.file.id).exists())

    def test_hard_delete(self):
        """
        Test that a hard delete permanently removes the object from the database.
        """
        self.file.hard_delete()
        self.assertFalse(StoredFile.objects.filter(id=self.file.id).exists())


class StoredFileTestCase(TestCase):
    """
    Test case for the StoredFile model.
    """

    def test_create_stored_file(self):
        """
        Test the creation of a StoredFile object.
        """
        file = StoredFile.objects.create(filename="example.txt")
        self.assertEqual(file.filename, "example.txt")
        self.assertIsNotNone(file.upload_date)

    def test_unique_filename(self):
        """
        Test that filenames must be unique.
        """
        StoredFile.objects.create(filename="unique.txt")
        with self.assertRaises(Exception):
            StoredFile.objects.create(filename="unique.txt")