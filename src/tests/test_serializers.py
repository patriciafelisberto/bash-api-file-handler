from django.test import TestCase
from core.models import StoredFile
from core.serializers import StoredFileSerializer, UserDataSerializer


class StoredFileSerializerTestCase(TestCase):
    """
    Test case for the StoredFileSerializer.
    """

    def setUp(self):
        # Create a sample StoredFile object
        self.stored_file = StoredFile.objects.create(filename="example.txt")

    def test_serialization(self):
        """
        Test that the serializer correctly serializes a StoredFile instance.
        """
        serializer = StoredFileSerializer(instance=self.stored_file)
        expected_data = {
            "filename": self.stored_file.filename,
            "upload_date": self.stored_file.upload_date.isoformat(),
        }
        self.assertEqual(serializer.data, expected_data)

    def test_deserialization_valid_data(self):
        """
        Test that the serializer correctly validates and deserializes valid data.
        """
        data = {"filename": "new_file.txt", "upload_date": "2024-12-11T10:00:00Z"}
        serializer = StoredFileSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["filename"], "new_file.txt")
        self.assertEqual(serializer.validated_data["upload_date"], "2024-12-11T10:00:00Z")

    def test_deserialization_invalid_data(self):
        """
        Test that the serializer detects invalid data.
        """
        data = {"filename": "", "upload_date": "invalid-date"}
        serializer = StoredFileSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("filename", serializer.errors)
        self.assertIn("upload_date", serializer.errors)


class UserDataSerializerTestCase(TestCase):
    """
    Test case for the UserDataSerializer.
    """

    def test_serialization(self):
        """
        Test that the serializer correctly serializes a dictionary to JSON.
        """
        data = {
            "username": "example_user",
            "folder": "inbox",
            "numberMessages": 123,
            "size": 4567,
        }
        serializer = UserDataSerializer(data)
        expected_data = {
            "username": "example_user",
            "folder": "inbox",
            "numberMessages": 123,
            "size": 4567,
        }
        self.assertEqual(serializer.data, expected_data)

    def test_deserialization_valid_data(self):
        """
        Test that the serializer correctly validates and deserializes valid data.
        """
        data = {
            "username": "example_user",
            "folder": "inbox",
            "numberMessages": 123,
            "size": 4567,
        }
        serializer = UserDataSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["username"], "example_user")
        self.assertEqual(serializer.validated_data["folder"], "inbox")
        self.assertEqual(serializer.validated_data["numberMessages"], 123)
        self.assertEqual(serializer.validated_data["size"], 4567)

    def test_deserialization_invalid_data(self):
        """
        Test that the serializer detects invalid data.
        """
        data = {
            "username": "",
            "folder": "inbox",
            "numberMessages": "not-a-number",
            "size": -1,
        }
        serializer = UserDataSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)
        self.assertIn("numberMessages", serializer.errors)
        self.assertIn("size", serializer.errors)
