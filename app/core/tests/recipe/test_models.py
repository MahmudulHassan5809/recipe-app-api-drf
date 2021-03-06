from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from recipe.models import Tag,Ingredient,Recipe,recipe_image_file_path

def sample_user(email="test@gmail.com",password="testpass"):
    return get_user_model().objects.create_user(email,password)


class ModelTests(TestCase):
    """Test all models of recipe app"""

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = Tag.objects.create(user = sample_user(),name = 'Vegan')
        self.assertEqual(str(tag), tag.name)
    
    def test_ingredient_str(self):
        """Test the Ingredient string representation"""
        ingredient = Ingredient.objects.create(user = sample_user(),name = 'Cucumber')
        self.assertEqual(str(ingredient), ingredient.name)
    

    def test_recipe_str(self):
        """Test the Recipe string representation"""
        recipe = Recipe.objects.create(
            user = sample_user(),
            title = 'Steak and mashroo sauce',
            time_minutes = 5,
            price = 5.00
        )
        self.assertEqual(str(recipe), recipe.title)
    
    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self,mock_uuid):
        """Test that image is saved in the correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = recipe_image_file_path(None,'my image.jpeg')

        exp_path = f'uploads/recipe/{uuid}.jpeg'
        self.assertEqual(file_path,exp_path)