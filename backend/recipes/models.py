from colorfield.fields import ColorField
from django.db import models

from users.models import User


class Tag(models.Model):
    '''Класс Tag создает БД SQL для хранения информации о тегах.'''

    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='имя тега',
        db_index=True,
    )
    color = ColorField(unique=True, verbose_name='цвет')
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    '''Класс Ingredient создает БД SQL для
    хранения информации об ингредиентах.'''

    name = models.CharField(
        max_length=200,
        verbose_name='Наименование',
        db_index=True,
    )
    measurement_unit = models.CharField(
        max_length=20,
        verbose_name='Ед.измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    '''Класс Recipe создает БД SQL для хранения информации о рецептах.'''

    name = models.CharField(max_length=200, verbose_name='Имя рецепта')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientsForRecipe',
        verbose_name='Ингредиент',
        help_text='Введите ингредиент'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тег',
        help_text='Выберите теги'
    )
    image = models.ImageField(
        upload_to='media/',
        verbose_name='Изображение',
        help_text='Загрузите изображение рецепта'
    )
    text = models.TextField(
        verbose_name='Текст рецепта',
        help_text='Напишите здесь ваш рецепт'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        help_text='Укажите время приготовления рецепта в минутах'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикаци',
        db_index=True,
    )

    class Meta:
        ordering = ['-pub_date', ]
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name

    def followers_number(self):
        return self.fan_user.count()


class IngredientsForRecipe(models.Model):
    '''Класс создает БД SQL для хранения информации
    об использованных в каждом рецепте ингредиентах.'''

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_used',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(verbose_name='Количество')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return f'{self.recipe.name} - {self.ingredient.name}'


class FavouriteRecipes(models.Model):
    '''Класс FavouriteRecipes создает БД SQL для хранения
    информации о рецептах, добавленных в избранное.'''

    fan_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favourite_recipes',
        verbose_name='Подписчик рецепта'
    )
    fav_recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='fan_user',
        verbose_name='Избранный рецепт'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['fan_user', 'fav_recipe'],
                name='unique_fanuser_recipe'
            )
        ]
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class ShopList(models.Model):
    '''Класс ShopList создает БД SQL для хранения
    информации о рецептах, добавленных в корзину для покупки.'''

    shopper = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes_to_shop',
        verbose_name='Покупатель'
    )
    recipe_to_shop = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppers',
        verbose_name='Рецепт в списке покупок'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['shopper', 'recipe_to_shop'],
                name='unique_shopper_recipe'
            )
        ]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
