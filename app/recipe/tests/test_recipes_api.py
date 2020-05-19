from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe
from recipe import RecipeSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def sample_recipe(user, **params):
    """Helper function to create and return a sample recipe"""
    defauls = {
        'title': 'Sample Recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(**params)

    return Recipe.objects.create(user, **defaults)


def sample_user(email='test@gmail.com', password='TestPass123'):
    """Helper function that creates and returns a test user"""
    return get_user_model().objects.create_user(email, password)


class PublicRecipesApiTests(TestCase):
    """Test public recipe api"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test public access to the recipe list api endpoint"""
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class PrivateRecipeApiTests(self):
    """Test the private recipe api endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(self.user)

    def test_retrieving_recipe_list(self):
        """Test retrieving the recipe list for authenticated user"""
        sample_recipe(self.user)
        sample_recipe(self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all()
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieving_recipe_list_for_user(self):
        """Test retrieving the list of recipes for authenticated user only"""
        user2 = sample_user('test2@gmail.com', 'Password123')
        sample_recipe(user2)
        sample_recipe(self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)
