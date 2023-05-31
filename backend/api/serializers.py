from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .fields import Base64ImageField
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.validators import UniqueValidator

from recipes.models import Ingredient, Tag, QuantityIngredient, Recipe

User = get_user_model()


class TagSerializer(ModelSerializer):
    """Сериализатор для вывода тэгов."""
    class Meta:
        model = Tag
        fields = ('name', 'color', 'slug')


class IngredientSerializer(ModelSerializer):
    """Сериализатор для вывода ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')


class CustomUserSerializer(UserSerializer):
    """Сериализатор для модели User."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """Вычисление значения поля is_subscribed."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.follower.filter(author=obj.id).exists()


class QuantityIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения количества ингредиентов."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = QuantityIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра рецептов"""
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = QuantityIngredientSerializer(
        many=True, source='recipeingredients', read_only=True
    )
    image = Base64ImageField()
    is_in_shopping_list = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_list',
            'name', 'image', 'text', 'cooking_time',
        )

    def get_is_favorited(self, obj):
        """Вычисление значения поля is_favorited."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(favorites__user=user, id=obj.id).exists()

    def get_is_in_shopping_list(self, obj):
        """Вычисление значения поля is_in_shopping_list."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shoppinglists.filter(recipe=obj.id).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор модели User для создания пользователя."""
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="Пользователь с таким email уже существует!"
            )
        ]
    )

    class Meta:
        model = User
        lookup_field = 'username'
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class RecipeIngredientWriteSerializer(ModelSerializer):
    id = serializers.IntegerField(write_only=True)

    class Meta:
        model = QuantityIngredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    ingredients = RecipeIngredientWriteSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time',
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients(instance, ingredients)
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data

    def validate_ingredients(self, value):
        ingredients = value
        if not ingredients:
            raise serializers.ValidationError(
                'Нужен хотя бы один ингредиент!'
            )
        ingredients_list = []
        for item in ingredients:
            ingredient = get_object_or_404(Ingredient, id=item["id"])
            if ingredient in ingredients_list:
                raise serializers.ValidationError(
                    'Ингридиенты не могут повторяться!'
                )
            if int(item["amount"]) <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше 0!'
                )
            ingredients_list.append(ingredient)
        return value

    def validate_tags(self, tags):
        if tags is None:
            raise serializers.ValidationError(
                'Список тегов отсутствует.'
            )
        if len(tags) == 0:
            raise serializers.ValidationError(
                'Не выбрано ни одного тега.'
            )
        return tags


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов на странице подписок"""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FollowUserSerializer(serializers.ModelSerializer):
    """Сериализация модели User для подписок."""
    recipes = RecipeShortSerializer(read_only=True, many=True)
    recipe_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipe_count',
        )
        read_only_fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipe_count',
        )

    def get_recipe_count(self, obj):
        """Вычисляем количество рецептов автора."""
        return Recipe.objects.filter(author=obj).count()

    def get_is_subscribed(self, obj):
        """Авторы в списке подписок всегда имеют признак is_subscribed=True."""
        return True
