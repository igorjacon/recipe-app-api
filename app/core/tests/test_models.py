from django.test import TestCase

from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test@gmail.com', password='Password01'):
    """Create sample user to be used in tests"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email(self):
        """Test that user was successfully created with email"""
        email = 'test@gmail.com'
        password = 'password123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(email, user.email)
        self.assertTrue(user.check_password(password))

    def test_normalize_user_email(self):
        """Test that user email is normalized"""
        email = 'test@GMAIL.com'
        user = get_user_model().objects.create_user(email, 'pass123')

        self.assertEqual(user.email, email.lower())

    def test_email_validation(self):
        """Test that user contains an email, if not then raise error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'Pass2324')

    def test_create_super_user(self):
        """Test creating a super user"""
        user = get_user_model().objects.create_superuser(
            'igor@gmail.com',
            'Password'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test that the tag string represantion returns the tag name"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegetarian'
        )

        self.assertEqual(str(tag), tag.name)
