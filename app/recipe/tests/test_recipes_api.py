from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Ingredient, Tag
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Create and return detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='dessert'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='cinammon'):
    """Create and return a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **params):
    """Helper function to create and return a sample recipe"""
    defaults = {
        'title': 'Sample Recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


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

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test the private recipe api endpoint"""

    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(self.user)

    def test_retrieving_recipe_list(self):
        """Test retrieving the recipe list for authenticated user"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user, title='New Recipe')

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
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

    def test_recipe_detail_view(self):
        """Test retrieving the details of a recipe"""
        recipe = sample_recipe(self.user, title='Cinammon Bun')
        recipe.tags.add(sample_tag(self.user))
        recipe.ingredients.add(sample_ingredient(self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """Test creating a recipe"""
        payload = {
            'title': 'Test Recipe',
            'time_minutes': 15,
            'price': 5.00
        }

        res = self.client.post(RECIPE_URL, payload)
        recipe = Recipe.objects.get(id=res.data['id'])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test creting recipe with tags"""
        tag1 = sample_tag(user=self.user, name='Italian')
        tag2 = sample_tag(user=self.user, name='Vegetarian')
        payload = {
            'title': 'Margharita Pizza',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 20,
            'price': 10.00
        }

        res = self.client.post(RECIPE_URL, payload)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test creating a recipe with ingredients"""
        ingredient1 = sample_ingredient(user=self.user, name='tomato')
        ingredient2 = sample_ingredient(user=self.user, name='cheese')
        payload = {
            'title': 'Macaronni and cheese',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 30,
            'price': 20.00
        }

        res = self.client.post(RECIPE_URL, payload)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """Test updating a recipe with patch"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='new tag')

        payload = {'title': 'New Recipe', 'tags': [new_tag.id]}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        tags = recipe.tags.all()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_recipe_update(self):
        """Test updating a recipe with put"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))

        payload = {
            'title': 'Chicken mayo sandwich',
            'time_minutes': 5,
            'price': 5.00
        }

        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)
