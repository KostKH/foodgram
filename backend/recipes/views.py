from django.conf import settings
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.filters import IngredientFilter, RecipeFilter
from recipes.permissions import IsOwnerOrReadOnly

from . import serializers as s
from .models import (FavouriteRecipes, Ingredient, IngredientsForRecipe,
                     Recipe, ShopList, Tag)


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
            serializer.is_valid()

            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        elif request.method == 'DELETE':
            try:
                instance = FavouriteRecipes.objects.get(
                    fan_user=request.user,
                    fav_recipe=Recipe.objects.get(pk=pk)
                )

            except Recipe.DoesNotExist:
                return Response(
                    {'errors': 'Рецепта с таким номером не существует'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            except FavouriteRecipes.DoesNotExist:
                return Response(
                    {'errors': 'Рецепт отсутствует в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'errors': 'метод не в списке разрешенных методов'},
            status=status.HTTP_400_BAD_REQUEST
        )

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

            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        elif request.method == 'DELETE':
            try:
                instance = ShopList.objects.get(
                    shopper=request.user,
                    recipe_to_shop=Recipe.objects.get(pk=pk)
                )

            except Recipe.DoesNotExist:
                return Response(
                    {'errors': 'Рецепта с таким номером не существует'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            except ShopList.DoesNotExist:
                return Response(
                    {'errors': 'Рецепт отсутствует в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'errors': 'метод не в списке разрешенных методов'},
            status=status.HTTP_400_BAD_REQUEST
        )

    def convert_to_txt(self, shoplist):
        file_name = settings.SHOPLIST_FILE_NAME
        lines = []
        for item in shoplist:
            name = item['ingredient__name']
            measurement_unit = item['ingredient__measurement_unit']
            amount = item['ingredient_total']
            lines.append(f'{name} - {amount} {measurement_unit}')
        lines.append('\nПриятного аппетита! Ваш FoodGram')
        content = '\n'.join(lines)
        content_type = 'text/plain,charset=utf8'
        response = HttpResponse(content, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        return response

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
        return self.convert_to_txt(shoplist)
