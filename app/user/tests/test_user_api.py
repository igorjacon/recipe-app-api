from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ACCOUNT_URL = reverse('user:account')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):
    """Create tests for public users."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_successfully(self):
        """Test that the user was created successfully"""
        payload = {
            'email': 'igor.jacon@peterandclark.com',
            'password': 'Testpass123',
            'name': 'Igor'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_create_duplicate_user_fails(self):
        """Test that when creating a user that already exists fails"""
        payload = {
            'email': 'ijacon@intimesit.com',
            'password': 'TestPass123',
            'name': 'Igor'
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertTrue(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_strenght(self):
        """
        Test that the user password contains at least 8 characters and at
        least 1 uppercase and at least 1 number
        """
        payload = {
            'email': 'igorjacon90@gmail.com',
            'password': 'passtest',
            'name': 'Igor'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token was created for a valid user"""
        payload = {'email': 'test@gmail.com', 'password': 'testPass123'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_request_token_for_invalid_credentials(self):
        """Test that a token is not created for invalid user credentials"""
        payload = {'email': 'test@gmail.com', 'password': 'test'}
        create_user(email='test@gmail.com', password='testPass123')
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_request_token_for_invalid_user(self):
        """Test that a token is not created for an invalid user"""
        payload = {'email': 'test@gmail.com', 'password': 'test'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_request_token_with_missing_field(self):
        """Test that email and password are required"""
        res = self.client.post(TOKEN_URL, {
            'email': 'test@gmail.com',
            'password': ''
        })

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""
        res = self.client.get(ACCOUNT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test for authenticated user"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@gmail.com',
            password='testPass123',
            name='Test User'
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_authenticated_user(self):
        """Test the GET endpoint on the user profile url"""
        res = self.client.get(ACCOUNT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': self.user.email,
            'name': self.user.name
        })

    def test_post_profile_not_allowed(self):
        """Test that the post method is not allowed on the profile url"""
        res = self.client.post(ACCOUNT_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test that we can update an authenticated user"""
        payload = {'name': 'New Name', 'password': 'newPass123'}
        res = self.client.patch(ACCOUNT_URL, payload)

        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
