# Generated by Django 3.2.2 on 2021-05-15 11:48

from django.db import migrations, models
import recipe.models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0003_recipe'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='image',
            field=models.ImageField(null=True, upload_to=recipe.models.recipe_image_file_path),
        ),
    ]
