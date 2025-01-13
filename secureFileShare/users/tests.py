from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.core import mail
from rest_framework import status
from .models import User
from rest_framework.authtoken.models import Token
from django.utils.timezone import now, timedelta
from unittest.mock import patch

class AuthenticationTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register_user')
        self.login_url = reverse('login')
        self.verify_otp_url = reverse('verify_otp')
        self.logout_url = reverse('logout')
        
        # Test user data
        self.user_data = {
            'email': 'destthat930@gmail.com',
            'username': 'testuser',
            'password': 'testpass123',
            'role': 'ADMIN'
        }

    def test_register_success(self):
        """Test successful user registration"""
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'OTP sent to your email.')
        self.assertEqual(len(mail.outbox), 1)  # Check if email was sent
        self.assertTrue(User.objects.filter(email=self.user_data['email']).exists())

    def test_register_duplicate_email(self):
        """Test registration with existing email"""
        # Create user first
        User.objects.create_user(
            email=self.user_data['email'],
            username=self.user_data['username'],
            password=self.user_data['password']
        )
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Check for either format of error message
        error_message_exists = (
            'error' in response.data and response.data['error'] == 'Email already exists.' or
            'email' in response.data and 'already exists' in str(response.data['email'][0]).lower()
        )
        self.assertTrue(error_message_exists, f"Unexpected response format: {response.data}")

    # def test_login_success(self):
    #     """Test successful login"""
    #     # Create user first
    #     User.objects.create_user(
    #         email=self.user_data['email'],
    #         username=self.user_data['username'],
    #         password=self.user_data['password']
    #     )
        
    #     # Try to login
    #     response = self.client.post(self.login_url, {
    #         'email': self.user_data['email'],
    #         'password': self.user_data['password']
    #     })
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['message'], 'OTP sent to your email.')
    #     self.assertEqual(len(mail.outbox), 1)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        # Create user
        User.objects.create_user(
            email=self.user_data['email'],
            username=self.user_data['username'],
            password=self.user_data['password']
        )
        
        # Try to login with wrong password
        response = self.client.post(self.login_url, {
            'email': self.user_data['email'],
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_verify_otp_success(self):
        """Test successful OTP verification"""
        # Create user with OTP
        user = User.objects.create_user(
            email=self.user_data['email'],
            username=self.user_data['username'],
            password=self.user_data['password']
        )
        user.otp = '123456'
        user.otp_expiry = now() + timedelta(minutes=5)
        user.save()
        
        # Verify OTP
        response = self.client.post(self.verify_otp_url, {
            'email': self.user_data['email'],
            'otp': '123456'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_verify_otp_expired(self):
        """Test expired OTP verification"""
        # Create user with expired OTP
        user = User.objects.create_user(
            email=self.user_data['email'],
            username=self.user_data['username'],
            password=self.user_data['password']
        )
        user.otp = '123456'
        user.otp_expiry = now() - timedelta(minutes=6)  # Expired
        user.save()
        
        # Try to verify expired OTP
        response = self.client.post(self.verify_otp_url, {
            'email': self.user_data['email'],
            'otp': '123456'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid or expired OTP.')

    @patch('rest_framework_simplejwt.tokens.RefreshToken.blacklist')
    def test_logout_success(self, mock_blacklist):
        """Test successful logout"""
        # Create and authenticate user
        user = User.objects.create_user(
            email=self.user_data['email'],
            username=self.user_data['username'],
            password=self.user_data['password']
        )
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        # Logout
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Logged out successfully.')

    def test_register_missing_fields(self):
        """Test registration with missing required fields"""
        incomplete_data = {
            'email': 'test@example.com'
            # missing password and username
        }
        response = self.client.post(self.register_url, incomplete_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_nonexistent_user(self):
        """Test login with non-existent user"""
        response = self.client.post(self.login_url, {
            'email': 'nonexistent@example.com',
            'password': 'somepassword'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_verify_otp_wrong_otp(self):
        """Test OTP verification with incorrect OTP"""
        user = User.objects.create_user(
            email=self.user_data['email'],
            username=self.user_data['username'],
            password=self.user_data['password']
        )
        user.otp = '123456'
        user.otp_expiry = now() + timedelta(minutes=5)
        user.save()
        
        response = self.client.post(self.verify_otp_url, {
            'email': self.user_data['email'],
            'otp': '999999'  # Wrong OTP
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)