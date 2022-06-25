from djoser.serializers import UserSerializer
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        ReadOnlyField, SerializerMethodField,
                                        UniqueTogetherValidator,
                                        ValidationError)

from recipes.models import Recipe

from .models import Subscriptions, User


class ModifiedUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField()

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


# код продублирован, так как при попытке импорта модели из reсipes
# возникает конфликт импортов
class RecipeMiniSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(ModelSerializer):
    email = ReadOnlyField(source='author.email')
    id = ReadOnlyField(source='author.id')
    username = ReadOnlyField(source='author.username')
    first_name = ReadOnlyField(source='author.first_name')
    last_name = ReadOnlyField(source='author.last_name')
    is_subscribed = SerializerMethodField()
    recipes = SerializerMethodField()
    recipes_count = IntegerField(source='author.recipes.count')

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
            raise ValidationError(
                'recipes_limit должен быть целым положительным числом'
            )
        return RecipeMiniSerializer(queryset, read_only=True, many=True).data


class SubscribeSerializer(ModelSerializer):

    class Meta:
        model = Subscriptions
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
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
            raise ValidationError(
                'Вы пытаетесь подписаться на себя')
        return data
