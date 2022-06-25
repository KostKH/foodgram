from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers as s
from rest_framework.relations import SlugRelatedField

from recipes.models import (FavouriteRecipes, Ingredient, IngredientsForRecipe,
                            Recipe, ShopList, Tag)
from users.models import Subscriptions, User


class ModifiedUserSerializer(UserSerializer):
    is_subscribed = s.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return Subscriptions.objects.filter(user=user, author=obj).exists()


class RecipeMiniSerializer(s.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(s.ModelSerializer):
    email = s.ReadOnlyField(source='author.email')
    id = s.ReadOnlyField(source='author.id')
    username = s.ReadOnlyField(source='author.username')
    first_name = s.ReadOnlyField(source='author.first_name')
    last_name = s.ReadOnlyField(source='author.last_name')
    is_subscribed = s.SerializerMethodField()
    recipes = s.SerializerMethodField()
    recipes_count = s.IntegerField(source='author.recipes.count')

    class Meta:
        model = Subscriptions
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return Subscriptions.objects.filter(
            user=user,
            author=obj.author
        ).exists()

    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj.author)
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        try:
            if recipes_limit and int(recipes_limit) > 0:
                queryset = queryset[:int(recipes_limit)]
        except (ValueError, TypeError):
            raise s.ValidationError(
                'recipes_limit должен быть целым положительным числом'
            )
        return RecipeMiniSerializer(queryset, read_only=True, many=True).data


class SubscribeSerializer(s.ModelSerializer):

    class Meta:
        model = Subscriptions
        fields = ('user', 'author')
        validators = [
            s.UniqueTogetherValidator(
                queryset=Subscriptions.objects.all(),
                fields=('user', 'author')
            )
        ]

    def to_representation(self, instance):
        serializer = SubscriptionsSerializer(
            instance,
            context=self.context
        )
        return serializer.data

    def validate(self, data):
        request = self.context.get('request')
        if request.user == data.get('author'):
            raise s.ValidationError(
                'Вы пытаетесь подписаться на себя')
        return data


class TagSerializer(s.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class TagFieldSerializer(SlugRelatedField):

    def to_representation(self, obj):
        serializer = TagSerializer(obj, context=self.context)
        return serializer.data


class IngredientSerializer(s.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientForRecipeSerializer(s.ModelSerializer):
    id = s.ReadOnlyField(source='ingredient.id')
    name = s.ReadOnlyField(source='ingredient.name')
    measurement_unit = s.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientsForRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AddIngredientForRecipeSerializer(s.ModelSerializer):
    id = s.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientsForRecipe
        fields = ('id', 'amount')

    def validate_amount(self, value):
        if value < 1:
            raise s.ValidationError(
                'Убедитесь, что это значение больше либо равно 1.'
            )
        return value


class RecipeSerializer(s.ModelSerializer):
    tags = TagFieldSerializer(
        slug_field='id',
        queryset=Tag.objects.all(),
        many=True
    )
    author = ModifiedUserSerializer(read_only=True)
    ingredients = IngredientForRecipeSerializer(
        source='ingredients_used',
        many=True
    )
    is_favorited = s.SerializerMethodField()
    is_in_shopping_cart = s.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return FavouriteRecipes.objects.filter(
            fan_user=user,
            fav_recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return ShopList.objects.filter(
            shopper=user,
            recipe_to_shop=obj
        ).exists()


class AddRecipeSerializer(s.ModelSerializer):

    tags = TagFieldSerializer(
        slug_field='id',
        queryset=Tag.objects.all(),
        many=True
    )
    author = ModifiedUserSerializer(read_only=True)
    ingredients = AddIngredientForRecipeSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance, context=self.context)
        return serializer.data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredient_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        IngredientsForRecipe.objects.bulk_create(
            [
                IngredientsForRecipe(
                    recipe=recipe,
                    ingredient=item['id'],
                    amount=item['amount']
                )
                for item in ingredient_data
            ]
        )
        return recipe

    def update(self, instance, validated_data):
        if validated_data.get('tags'):
            tags = validated_data.pop('tags')
            instance.tags.clear()
            instance.tags.set(tags)

        if not validated_data.get('ingredients'):
            return super().update(instance, validated_data)

        ingredient_data = validated_data.pop('ingredients')
        old_ingredients = (
            IngredientsForRecipe.objects.filter(recipe=instance)
        )
        for item in old_ingredients:
            item.delete()
        IngredientsForRecipe.objects.bulk_create(
            [
                IngredientsForRecipe(
                    recipe=instance,
                    ingredient=item['id'],
                    amount=item['amount']
                )
                for item in ingredient_data
            ]
        )
        return super().update(instance, validated_data)

    def validate_cooking_time(self, value):
        if value < 1:
            raise s.ValidationError(
                'Убедитесь, что это значение больше либо равно 1.'
            )
        return value

    def validate(self, data):
        all_ingredients = data.get('ingredients')

        if all_ingredients is None:
            return data

        unique_ids = set(item['id'] for item in all_ingredients)
        if len(unique_ids) != len(all_ingredients):
            raise s.ValidationError(
                'Ингредиенты в рецепте не должны повторяться'
            )
        return data


class FavouriteRecipeSerializer(s.ModelSerializer):

    class Meta:
        model = FavouriteRecipes
        fields = (
            'fav_recipe',
            'fan_user',
        )
        validators = [
            s.UniqueTogetherValidator(
                queryset=FavouriteRecipes.objects.all(),
                fields=('fav_recipe', 'fan_user'),
                message=('Вы пытаетесь добавить рецепт,'
                         'который уже есть в избранном')
            )
        ]

    def to_representation(self, instance):
        recipe = Recipe.objects.get(id=instance.fav_recipe.id)
        serializer = RecipeMiniSerializer(recipe)
        return serializer.data


class ShopListSerializer(s.ModelSerializer):

    class Meta:
        model = ShopList
        fields = (
            'shopper',
            'recipe_to_shop',
        )
        validators = [
            s.UniqueTogetherValidator(
                queryset=ShopList.objects.all(),
                fields=('shopper', 'recipe_to_shop'),
                message=('Вы пытаетесь добавить рецепт,'
                         'который уже есть в списке покупок')
            )
        ]

    def to_representation(self, instance):
        recipe = Recipe.objects.get(id=instance.recipe_to_shop.id)
        serializer = RecipeMiniSerializer(recipe)
        return serializer.data
