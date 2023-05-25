from rest_framework import status
from rest_framework.response import Response
from recipes.models import FavoriteRecipe, ShoppingList
from users.models import Follow


def create_obj(attrs, model, serializer):
    """Создание записей в таблицах FavoriteRecipe, Follow, ShoppingList."""
    model_attr = {
        Follow: 'author',
        FavoriteRecipe: 'recipe',
        ShoppingList: 'recipe'
    }

    if model.objects.filter(**attrs).exists():
        return Response(
            {'errors': 'Запись уже существует.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    model.objects.create(**attrs)
    return Response(
        serializer(attrs.get(model_attr[model])).data,
        status=status.HTTP_201_CREATED
    )


def delete_obj(attrs, model):
    """Удаление записей из таблиц FavoriteRecipe, Follow, ShoppingList."""
    if not model.objects.filter(**attrs):
        return Response(
            {'errors': 'Запись отсутствует.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    model.objects.get(**attrs).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
