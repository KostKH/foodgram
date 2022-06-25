from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api import serializers as s
from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsOwnerOrReadOnly
from api.utils import convert_to_txt
from recipes.models import (FavouriteRecipes, Ingredient, IngredientsForRecipe,
                            Recipe, ShopList, Tag)
from users.models import Subscriptions, User


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = s.TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = s.IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = s.RecipeSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return s.RecipeSerializer
        return s.AddRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_recipe(self, pk):
        try:
            return Recipe.objects.get(pk=pk)

        except Recipe.DoesNotExist:
            raise ValidationError(
                {'errors': 'Рецепта с таким номером не существует'}
            )

    def get_object_deleted(self, data, model):
        try:
            instance = model.objects.get(**data)

        except Recipe.DoesNotExist:
            raise ValidationError(
                {'errors': 'Рецепта с таким номером не существует'}
            )
        except FavouriteRecipes.DoesNotExist:
            raise ValidationError(
                {'errors': 'Рецепт отсутствует в избранном'}
            )
        except ShopList.DoesNotExist:
            raise ValidationError(
                {'errors': 'Рецепт отсутствует в списке покупок'}
            )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_object_posted(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            data = {
                'fav_recipe': pk,
                'fan_user': request.user.id
            }
            serializer = s.FavouriteRecipeSerializer(data=data)
            return self.get_object_posted(serializer=serializer)

        recipe = self.get_recipe(pk=pk)
        data = {
            'fan_user': request.user,
            'fav_recipe': recipe
        }
        model = FavouriteRecipes
        return self.get_object_deleted(data=data, model=model)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated, )
    )
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            data = {
                'recipe_to_shop': pk,
                'shopper': request.user.id
            }
            serializer = s.ShopListSerializer(data=data)
            return self.get_object_posted(serializer=serializer)

        recipe = self.get_recipe(pk=pk)
        data = {
            'shopper': request.user,
            'recipe_to_shop': recipe
        }
        model = ShopList
        return self.get_object_deleted(data=data, model=model)

    @action(
        methods=['get', ],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        shoplist = IngredientsForRecipe.objects.filter(
            recipe__shoppers__shopper=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by(
            'ingredient__name'
        ).annotate(ingredient_total=Sum('amount'))
        return convert_to_txt(shoplist)


class SubsriptionsView(ListAPIView):

    serializer_class = s.SubscriptionsSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return user.followed_authors.all().order_by('-id')


class SubscribeView(APIView):
    pagination_class = None
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, id):
        author = get_object_or_404(User, id=id)
        user = self.request.user
        data = {'user': user.id, 'author': author.id}
        serializer = s.SubscribeSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        author = get_object_or_404(User, id=id)
        user = self.request.user
        subscription = get_object_or_404(
            Subscriptions, user=user, author=author
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
