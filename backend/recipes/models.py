from django.contrib.auth import get_user_model
from django.core.validators import (MinValueValidator)
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()

MIN_INGREDIENT = 1
MAX_INGREDIENT = 50


class Ingredient(models.Model):
    """Класс модели ингредиентов"""
    name = models.CharField(
        verbose_name="Имя",
        max_length=200)
    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=200,)

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ("-id",)


class Tag(models.Model):
    """Класс тега рецептов"""
    name = models.CharField(
        verbose_name="Имя",
        max_length=200,
        unique=True)
    color = models.CharField(
        verbose_name="Цвет",
        max_length=7,
        unique=True)
    slug = models.SlugField(
        verbose_name="Уникальный индификатор",
        max_length=100,
        unique=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Класс модели рецептов"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор"
        )
    name = models.TextField('Название', max_length=72)
    image = models.ImageField(
        verbose_name="Изображение рецепта",
        upload_to=None,
        blank=True,
        null=True,
    )
    text = models.TextField(
        verbose_name="Описание рецепта"
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name="Ингредиенты блюда по рецепту",
        related_name="recipes")
    tag = models.ManyToManyField(
        Tag, verbose_name='Теги', related_name='recipes'
        )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления рецепта"
        )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-id",)

    def __str__(self):
        return self.name


class QuantityIngredient(models.Model):
    """Класс модели описывает количество ингредиентов"""
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        on_delete=models.CASCADE,
        related_name="ingredient_list",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name="Ингредиент",
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        "Количество",
        validators=[
            MinValueValidator(
                MIN_INGREDIENT,
                message='Количество ингредиента должно быть больше 0!'
            ),
        ],
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Количество ингредиентов"
        ordering = ("recipe",)


class ShoppingList(models.Model):
    """Класс модели для списка покупок."""
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="shopping_list",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_list",
        verbose_name="Покупка",
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Список покупок"
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shoping_list'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Список покупок'


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorite_recipe",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorite_recipe",
        verbose_name="Избранный рецепт",
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Избранное'
