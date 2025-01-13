from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from .models import EncryptedFile
from rest_framework.authtoken.models import Token
import base64
import time

User = get_user_model()

class FileOperationsTests(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Create token for authentication
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        # Create test file
        self.test_file_content = b"Test file content"
        self.test_file = SimpleUploadedFile(
            "test_file.txt",
            self.test_file_content,
            content_type="text/plain"
        )

    def test_file_upload_success(self):
        """Test successful file upload"""
        url = reverse('file_upload')
        response = self.client.post(url, {'file': self.test_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('name', response.data)
        self.assertEqual(response.data['name'], 'test_file.txt')
        self.assertTrue(EncryptedFile.objects.filter(name='test_file.txt').exists())

    def test_file_upload_no_file(self):
        """Test file upload without file"""
        url = reverse('file_upload')
        response = self.client.post(url, {}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'No file provided.')

    def test_file_upload_unauthorized(self):
        """Test file upload without authentication"""
        self.client.credentials()  # Remove authentication
        url = reverse('file_upload')
        response = self.client.post(url, {'file': self.test_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_file_download_success(self):
        """Test successful file download"""
        # First upload a file
        upload_url = reverse('file_upload')
        upload_response = self.client.post(upload_url, {'file': self.test_file}, format='multipart')
        file_id = upload_response.data['id']

        # Then try to download it
        download_url = reverse('file_download', kwargs={'file_id': file_id})
        response = self.client.get(download_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Disposition'], f'attachment; filename=test_file.txt')

    def test_file_download_not_found(self):
        """Test download of non-existent file"""
        url = reverse('file_download', kwargs={'file_id': 99999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_generate_secure_link(self):
        """Test generating secure download link"""
        # First upload a file
        upload_url = reverse('file_upload')
        upload_response = self.client.post(upload_url, {'file': self.test_file}, format='multipart')
        file_id = upload_response.data['id']

        # Generate secure link
        url = reverse('generate_secure_link', kwargs={'file_id': file_id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('secure_link', response.data)
        self.assertIn('expires_at', response.data)

    def test_generate_secure_link_unauthorized(self):
        """Test generating secure link without authentication"""
        self.client.credentials()  # Remove authentication
        url = reverse('generate_secure_link', kwargs={'file_id': 1})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_secure_file_download(self):
        """Test downloading file with secure link"""
        # First upload a file
        upload_url = reverse('file_upload')
        upload_response = self.client.post(upload_url, {'file': self.test_file}, format='multipart')
        file_id = upload_response.data['id']

        # Generate secure link
        generate_url = reverse('generate_secure_link', kwargs={'file_id': file_id})
        generate_response = self.client.get(generate_url)
        secure_link = generate_response.data['secure_link']

        # Extract token from secure link
        token = secure_link.split('/')[-2]

        # Try to download using secure link
        download_url = reverse('secure_file_download', kwargs={'token': token})
        response = self.client.get(download_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Disposition'], f'attachment; filename="test_file.txt"')

    def test_secure_file_download_invalid_token(self):
        """Test downloading file with invalid secure link"""
        url = reverse('secure_file_download', kwargs={'token': 'invalid_token'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_file_list(self):
        """Test listing user's files"""
        # Upload a couple of files first
        upload_url = reverse('file_upload')
        self.client.post(upload_url, {'file': self.test_file}, format='multipart')
        self.test_file.seek(0)  # Reset file pointer
        self.client.post(upload_url, {'file': self.test_file}, format='multipart')

        # Get file list
        url = reverse('user-file-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should have 2 files
        self.assertTrue(all(file['name'] == 'test_file.txt' for file in response.data))

    def test_user_file_list_unauthorized(self):
        """Test listing files without authentication"""
        self.client.credentials()  # Remove authentication
        url = reverse('user-file-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_file_list_empty(self):
        """Test listing files when user has no files"""
        url = reverse('user-file-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)