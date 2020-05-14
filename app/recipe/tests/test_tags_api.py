from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


def test_user(email='test@gmail.com', password='Password01'):
    """Helper function to create a test user"""
    return get_user_model().objects.create_user(email, password)


class PublicTagsAPITests(TestCase):
    """Test public tags api"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that a user is authenticated to access tags api"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(TestCase):
    """Test tags api when user is authenticated"""

    def setUp(self):
        self.client = APIClient()
        self.user = test_user()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_list_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Pizza')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrive_tags_for_authenticated_user(self):
        """Test retrieve tags pertaining to authenticated user"""
        user2 = test_user('test2@gmail.com', 'Password123')
        Tag.objects.create(user=user2, name='Dessert')
        tag = Tag.objects.create(user=self.user, name='Fast Food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag(self):
        """Test create tag successful"""
        payload = {'name': 'Test tag'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_tag_with_error(self):
        """Test that a validation error is returned when tag is invalid"""
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
