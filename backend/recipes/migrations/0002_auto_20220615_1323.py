# Generated by Django 2.2.19 on 2022-06-15 06:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('recipes', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='shoplist',
            name='shopper',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes_to_shop', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(through='recipes.IngredientsForRecipe', to='recipes.Ingredient'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(related_name='recipes', to='recipes.Tag'),
        ),
        migrations.AddField(
            model_name='ingredientsforrecipe',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.Ingredient'),
        ),
        migrations.AddField(
            model_name='ingredientsforrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.Recipe'),
        ),
        migrations.AddField(
            model_name='favouriterecipes',
            name='fan_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favourite_recipes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='favouriterecipes',
            name='fav_recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fan_user', to='recipes.Recipe'),
        ),
        migrations.AddConstraint(
            model_name='shoplist',
            constraint=models.UniqueConstraint(fields=('shopper', 'recipe_to_shop'), name='unique_shopper_recipe'),
        ),
        migrations.AddConstraint(
            model_name='ingredientsforrecipe',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredient'), name='unique_recipe_ingredient'),
        ),
        migrations.AddConstraint(
            model_name='favouriterecipes',
            constraint=models.UniqueConstraint(fields=('fan_user', 'fav_recipe'), name='unique_fanuser_recipe'),
        ),
    ]
