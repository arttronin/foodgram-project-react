from django.contrib import admin
from django.contrib.admin import display

from .models import (FavoriteRecipe, Ingredient, QuantityIngredient, Recipe,
                     ShoppingList, Tag)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Отображение модели рецептов в интерфейсе админки"""
    list_display = ('name', 'id', 'author')
    readonly_fields = ('added_in_favorites',)
    list_filter = ('author', 'name', 'tag',)
    empty_value_display = '-пусто-'

    @display(description='Количество в избранных')
    def added_in_favorites(self, obj):
        return obj.favorites.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Отображение модели ингредиентов в админке"""
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Отображение модели тегов в админке"""
    list_display = ('name', 'color', 'slug',)
    search_fields = ('name', 'color', 'slug')
    list_filter = ('name', 'color', 'slug')


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    """Отображение модели списка покупок в админке"""
    list_display = ('user', 'recipe',)
    search_fields = ('user', 'recipe',)


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    """Отображение модели избранных рецептов в админке"""
    list_display = ('user', 'recipe',)
    search_fields = ('user', 'recipe',)


@admin.register(QuantityIngredient)
class QuantityIngredientAdmin(admin.ModelAdmin):
    """Отображение модели кол-ва ингредиентов в админке"""
    list_display = ('recipe', 'ingredient', 'amount',)
    search_fields = ('recipe', 'ingredient')
    list_filter = ('recipe', 'ingredient')
