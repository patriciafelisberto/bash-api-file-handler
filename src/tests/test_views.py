import os

from django.urls import reverse
from django.test import TestCase
from django.conf import settings

from rest_framework import status
from rest_framework.test import APIClient

from unittest.mock import patch

from core.models import StoredFile


class UploadFileViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.upload_url = reverse('upload-file-upload-file')
        self.test_dir = settings.UPLOAD_DIR

        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        for filename in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, filename))

    def test_upload_valid_file(self):
        response = self.client.put(
            f'{self.upload_url}?filename=test_file.txt',
            data=b"File content",
            content_type='application/octet-stream'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "test_file.txt")))
        self.assertTrue(StoredFile.objects.filter(filename="test_file.txt").exists())

    def test_replace_existing_file(self):
        file_path = os.path.join(self.test_dir, "test_file.txt")
        with open(file_path, "w") as f:
            f.write("Old content")
        StoredFile.objects.create(filename="test_file.txt")

        response = self.client.put(
            f'{self.upload_url}?filename=test_file.txt',
            data=b"New content",
            content_type='application/octet-stream'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with open(file_path, "r") as f:
            self.assertEqual(f.read(), "New content")

    def test_upload_invalid_filename(self):
        response = self.client.put(
            f'{self.upload_url}?filename=invalid@file.txt',
            data=b"File content",
            content_type='application/octet-stream'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_filename_param(self):
        response = self.client.put(
            self.upload_url,
            data=b"File content",
            content_type='application/octet-stream'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ListFilesViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.list_url = reverse('list-files-list')
        StoredFile.objects.create(filename="file1.txt")
        StoredFile.objects.create(filename="file2.txt")

    def test_list_files(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        filenames = [file["filename"] for file in response.data]
        self.assertIn("file1.txt", filenames)
        self.assertIn("file2.txt", filenames)


class MaxMinSizeViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.max_min_url = reverse('max-min-size-list')

        self.file_path = os.path.join(settings.UPLOAD_DIR, "test_file.txt")
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        with open(self.file_path, "w") as f:
            f.write("user1 inbox 50 size 1000\n")
            f.write("user2 inbox 10 size 500\n")
        StoredFile.objects.create(filename="test_file.txt")

    def tearDown(self):
        os.remove(self.file_path)

    @patch('core.scripts_runner.run_script')
    def test_get_max_size(self, mock_run_script):
        mock_run_script.return_value = ("user1 inbox 50 size 1000", None)
        response = self.client.get(self.max_min_url, {"filename": "test_file.txt"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "user1")
        self.assertEqual(response.data["size"], 1000)


    @patch('core.scripts_runner.run_script')
    def test_get_min_size(self, mock_run_script):
        mock_run_script.return_value = ("user2 inbox 10 size 500", None)
        response = self.client.get(self.max_min_url, {"filename": "test_file.txt", "min": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "user2")
        self.assertEqual(response.data["size"], 500)


class OrderByUsernameViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.order_url = reverse('order-by-username-list')

        self.file_path = os.path.join(settings.UPLOAD_DIR, "test_file.txt")
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        with open(self.file_path, "w") as f:
            f.write("user2 inbox 10 size 500\n")
            f.write("user1 inbox 50 size 1000\n")
        StoredFile.objects.create(filename="test_file.txt")

    def tearDown(self):
        os.remove(self.file_path)

    @patch('core.scripts_runner.run_script')
    def test_order_by_username_asc(self, mock_run_script):
        mock_run_script.return_value = (
            "user1 inbox 50 size 1000\nuser2 inbox 10 size 500", None
        )
        response = self.client.get(self.order_url, {"filename": "test_file.txt"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [user["username"] for user in response.data]
        self.assertEqual(usernames, ["user1", "user2"])

    @patch('core.scripts_runner.run_script')
    def test_order_by_username_desc(self, mock_run_script):
        mock_run_script.return_value = (
            "user2 inbox 10 size 500\nuser1 inbox 50 size 1000", None
        )
        response = self.client.get(self.order_url, {"filename": "test_file.txt", "desc": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [user["username"] for user in response.data]
        self.assertEqual(usernames, ["user2", "user1"])


class BetweenMsgsViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.between_msgs_url = reverse('between-msgs-list')

        self.file_path = os.path.join(settings.UPLOAD_DIR, "test_file.txt")
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        with open(self.file_path, "w") as f:
            f.write("user1 inbox 50 size 1000\n")
            f.write("user2 inbox 100 size 2000\n")
            f.write("user3 inbox 200 size 3000\n")
        StoredFile.objects.create(filename="test_file.txt")

    def tearDown(self):
        os.remove(self.file_path)

    @patch('core.scripts_runner.run_script')
    def test_between_msgs(self, mock_run_script):
        mock_run_script.return_value = (
            "user1 inbox 50 size 1000\nuser2 inbox 100 size 2000", None
        )
        response = self.client.get(
            self.between_msgs_url, {"filename": "test_file.txt", "low": 50, "high": 150}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [user["username"] for user in response.data]
        self.assertEqual(usernames, ["user1", "user2"])