from django.contrib import admin

from recipes.models import (FavouriteRecipes, Ingredient, IngredientsForRecipe,
                            Recipe, ShopList, Tag)


class TagAdmin(admin.ModelAdmin):
    '''Класс для вывода на странице админа
    информации по тегам.'''

    list_display = ('id', 'name', 'color', 'slug')
    list_filter = ('name', 'slug')
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    '''Класс для вывода на странице админа
    информации об ингредиентах.'''

    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class RecipeIngredInline(admin.TabularInline):

    model = IngredientsForRecipe


class RecipeAdmin(admin.ModelAdmin):
    '''Класс для вывода на странице админа
    информации о рецептах.'''
    inlines = [RecipeIngredInline, ]
    list_display = ('id', 'name', 'author', 'pub_date')
    list_filter = ('name', 'author', 'tags',)
    search_fields = ('name', 'author__username')
    empty_value_display = '-пусто-'
    readonly_fields = ('fan_user_amount',)
    filter_horizontal = ('tags',)

    def fan_user_amount(self, obj):
        return obj.followers_number()
    fan_user_amount.short_description = 'Кол-во подписчиков'


class IngredientsForRecipeAdmin(admin.ModelAdmin):
    '''Класс для вывода на странице админа
    информации по ингредиентам в рецепте.'''

    list_display = ('id', 'recipe', 'ingredient', 'amount')
    search_fields = ('recipe', 'ingredient')
    list_filter = ('recipe', 'ingredient')
    empty_value_display = '-пусто-'


class FavouriteRecipesAdmin(admin.ModelAdmin):
    '''Класс для вывода на странице админа
    информации избранным рецептам.'''

    list_display = ('id', 'fan_user', 'fav_recipe')
    list_filter = ('fan_user', 'fav_recipe')


class ShopListAdmin(admin.ModelAdmin):
    '''Класс для вывода на странице админа
    информации по рецептам в списке покупок.'''

    list_display = ('id', 'shopper', 'recipe_to_shop')
    list_filter = ('shopper', 'recipe_to_shop')


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientsForRecipe, IngredientsForRecipeAdmin)
admin.site.register(FavouriteRecipes, FavouriteRecipesAdmin)
admin.site.register(ShopList, ShopListAdmin)
