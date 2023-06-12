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
    pagination_class = PageNumberPaginationLimit

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        page = self.paginate_queryset(queryset)
        serializer = FollowUserSerializer(
            page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            if user.id == author.id:
                return Response({'detail': 'Нельзя подписаться на себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            if Follow.objects.filter(author=author, user=user).exists():
                return Response({'detail': 'Вы уже подписаны!'},
                                status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.create(user=user, author=author)
            serializer = FollowUserSerializer(author,
                                              context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not Follow.objects.filter(user=user, author=author).exists():
                return Response({'errors': 'Вы не подписаны'},
                                status=status.HTTP_400_BAD_REQUEST)
            subscription = get_object_or_404(Follow,
                                             user=user,
                                             author=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
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
