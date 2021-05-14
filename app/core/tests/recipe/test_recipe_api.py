from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from recipe.models import Recipe,Tag,Ingredient

from recipe.serializers import RecipeSerializer,RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    """Return recipe detail url """
    return reverse('recipe:recipe-detail',args=[recipe_id])

def create_user(**params):
    return get_user_model().objects.create_user(**params)

def sample_tag(user,name='Main Course'):
    """Create and return a sample tag """
    return Tag.objects.create(user=user,name=name)


def sample_ingredient(user,name='Main Course'):
    """Create and return a sample ingredient """
    return Ingredient.objects.create(user=user,name=name)

def sample_recipe(user,**params):
    """Create and return a recipe"""
    defaults = {
       'title' : 'Sample Recipe',
       'time_minutes' : 10,
       'price' : 5.00 
    }
    defaults.update(params)

    return Recipe.objects.create(user=user,**defaults)


class PublicIngredientsApiTest(TestCase):
    """Test the publicly available recipe api"""

    def setUp(self):
        self.client = APIClient()
    
    def test_login_required(self):
        """Test that login is required for retrieving recipe"""
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test the authorized user recipe API"""

    def setUp(self):
        self.user = create_user(
            email = "test@gmail.com",
            password="testpass",
            name="Test Name"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_retrieve_recipes(self):
        """Test retrieving recipes"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes,many = True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
    
    def test_retrieve_user_ingredients_only(self):
        """Test that recipes returned are for the authenticated user"""
        user2 = create_user(
            email = "other@gmail.com",
            password="testpass",
            name="Other Name"
        )

        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes,many = True)
        
        
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data, serializer.data)
    
    def test_view_recipe_detail(self):
        """test viewing a recipe detail"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)

        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)
    

    def test_create_basic_recipe(self):
        """Test creating basic recipe"""
        payload = {
            'title' : 'Chocolate cheesecake',
            'time_minutes' : 30,
            'price' : 5.00
        }

        res = self.client.post(RECIPES_URL,payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id = res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe,key))
    
    def test_create_recipe_with_tags(self):
        """Test create a recipe with tags"""
        tag1 = sample_tag(user = self.user, name = 'Vegan')
        tag2 = sample_tag(user = self.user, name = 'Dessert')

        payload = {
            'title' : 'Chocolate cheesecake',
            'tags'  : [tag1.id,tag2.id],
            'time_minutes' : 30,
            'price' : 5.00
        }

        res = self.client.post(RECIPES_URL,payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id = res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1,tags)
        self.assertIn(tag2,tags)

    
    def test_create_recipe_with_ingredients(self):
        """Test create a recipe with ingredients"""
        ingredient1 = sample_ingredient(user = self.user, name = 'Prawns')
        ingredient2 = sample_ingredient(user = self.user, name = 'Prawns2')

        payload = {
            'title' : 'Chocolate cheesecake',
            'ingredients'  : [ingredient1.id,ingredient2.id],
            'time_minutes' : 30,
            'price' : 5.00
        }

        res = self.client.post(RECIPES_URL,payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id = res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1,ingredients)
        self.assertIn(ingredient2,ingredients)
    

    def test_partial_update_recipe(self):
        """test updating a recipe with patch """
        recipe = sample_recipe(user = self.user)
        recipe.tags.add(sample_tag(user = self.user))
        new_tag = sample_tag(user = self.user , name = "Curry")

        payload = {
            'title' : 'Chicken tikka',
            'tags'  : [new_tag.id]
        }

        url = detail_url(recipe.id)
        self.client.patch(url,payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag,tags)
    
    def test_full_update_recipe(self):
        """test updating a recipe with put """
        recipe = sample_recipe(user = self.user)
        recipe.tags.add(sample_tag(user = self.user))

        payload = {
            'title' : 'Chicken tikka',
            'time_minutes' : 25,
            'price' : 5.00,
        }

        url = detail_url(recipe.id)
        self.client.put(url,payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])

        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)