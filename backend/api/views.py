import os.path

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, IsAuthenticated)
from rest_framework.response import Response
from .filters import IngredientSearchFilter, RecipeFilter
from .paginations import PageNumberPaginationLimit
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnlyPermission
from .serializers import (CustomUserSerializer, FollowUserSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeSerializer, RecipeShortSerializer,
                          TagSerializer)
from .utils import create_obj, delete_obj
from foodgram.settings import MEDIA_ROOT
from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            ShoppingList,
                            Tag)
from users.models import Follow

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Получение списка пользователей, профиль пользователя,
    текущего пользователя.
    Подписки пользователя, подписаться на пользователя, удалить подписку
    """

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPaginationLimit

    @action(
        url_path='subscriptions',
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def get_subscriptions(self, response):
        """Подписки пользователя."""
        limit = self.request.query_params.get('recipes_limit')
        pages = self.paginate_queryset(
            User.objects.filter(author__user=self.request.user)
        )
        serializer = FollowUserSerializer(pages, many=True)
        if limit:
            for user in serializer.data:
                if user.get('recipes'):
                    user['recipes'] = user.get('recipes')[:int(limit)]

        return self.get_paginated_response(serializer.data)

    @action(
        url_path='subscribe',
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def get_subscribe(self, request, id):
        """Подписаться на автора, удалить подписку."""
        attrs = {
            'user': request.user,
            'author': get_object_or_404(User, pk=id)
        }

        if request.method == 'POST':
            if attrs.get('user') == attrs.get('author'):
                return Response(
                    {'errors': 'Нельзя подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return create_obj(attrs, Follow, FollowUserSerializer)
        if request.method == 'DELETE':
            return delete_obj(attrs, Follow)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Список тегов, получение тега по id."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    """Получение списка рецептов, одного рецепта.
    Создание рецепта, обновление и удаление.
    """

    permission_classes = (IsAuthorOrReadOnlyPermission,)
    pagination_class = PageNumberPaginationLimit
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        user = self.request.user
        if self.request.query_params.get('is_favorited'):
            return Recipe.objects.filter(favorites__user=user)
        if self.request.query_params.get('is_in_shopping_list'):
            return Recipe.objects.filter(shoppinglists__user=user)
        return Recipe.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeCreateSerializer

    @action(
        url_path='download_shopping_list',
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def get_download_shopping_list(self, request):
        """Создает список ингредиентов на основе рецептов,
        добавленных в список покупок.
        """
        user = self.request.user
        queryset_shopping_list = ShoppingList.objects.filter(
            user=user
        ).select_related(
            'recipe'
        ).values_list(
            'recipe__recipeingredients__ingredient__name',
            'recipe__recipeingredients__ingredient__measurement_unit'
        ).annotate(
            amount=Sum('recipe__recipeingredients__amount')
        )

        shopping_cart_list = f'Список покупок пользователя {user.username}:\n'
        for ingredient in queryset_shopping_list:
            shopping_cart_list += (
                f'{ingredient[0]}: {ingredient[2]} {ingredient[1]}\n'
            )

        response = HttpResponse(
            shopping_cart_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = (
            'attachment; filename=shopping_cart_list.txt'
        )
        return response

    @action(
        url_path='shopping_list',
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def get_shopping_cart(self, request, pk):
        """Добавление и удаление рецепта из списка покупок пользователя."""
        attrs = {
            'user': request.user,
            'recipe': get_object_or_404(Recipe, pk=pk)
        }

        if request.method == 'POST':
            return create_obj(attrs, ShoppingList, RecipeShortSerializer)
        if request.method == 'DELETE':
            return delete_obj(attrs, ShoppingList)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        url_path='favorite',
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def get_favorite(self, request, pk):
        """Добавление и удаление рецептов из избранного."""
        attrs = {
            'user': request.user,
            'recipe': get_object_or_404(Recipe, pk=pk)
        }

        if request.method == 'POST':
            return create_obj(attrs, FavoriteRecipe, RecipeShortSerializer)
        if request.method == 'DELETE':
            return delete_obj(attrs, FavoriteRecipe)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def perform_destroy(self, instance):
        image_path = os.path.join(MEDIA_ROOT, str(instance.image))
        os.remove(image_path)
        instance.delete()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)
