from datetime import datetime as dt
from urllib.parse import unquote
from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
#from rest_framework import permissions
#import from .permissions import IsAuthorOrReadOnlyPermission

from djoser.views import UserViewSet as DjoserUserViewSet

from recipes.models import AmountIngredient, Ingredient, Recipe, Tag, Favorite, Cart

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from . import conf
from .mixins import AddDelViewMixin
from .paginators import PageLimitPagination
from .permissions import AdminOrReadOnly, AuthorStaffOrReadOnly, IsAuthenticated
from .serializers import (IngredientSerializer, RecipeSerializer,
                          ShortRecipeSerializer, TagSerializer,
                          UserSubscribeSerializer)
from .services import incorrect_layout

User = get_user_model()


class UserViewSet(DjoserUserViewSet, AddDelViewMixin):
    """Работает с пользователями.

    ViewSet для работы с пользователми - вывод таковых,
    регистрация.
    Для авторизованных пользователей —
    возможность подписаться на автора рецепта.
    """
    pagination_class = PageLimitPagination
    add_serializer = UserSubscribeSerializer
    permission_classes = (AuthorStaffOrReadOnly,)

    @action(
        methods=conf.ACTION_METHODS,
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        """Создаёт/удалет связь между пользователями.

        Вызов метода через url: */user/<int:id>/subscribe/.

        Args:
            request (Request): Не используется.
            id (int, str):
                id пользователя, на которого желает подписаться
                или отписаться запрашивающий пользователь.

        Returns:
            Responce: Статус подтверждающий/отклоняющий действие.
        """
        user = self.request.user
        author = get_object_or_404(self.queryset, id=id)
        serializer = self.add_serializer(
            author, context={'request': self.request}
        )
        subscribe_exist = user.subscribe.filter(id=id).exists()

        if (self.request.method in conf.ADD_METHODS) and not subscribe_exist:
            user.subscribe.add(author)
            return Response(serializer.data, status=HTTP_201_CREATED)

        if (self.request.method in conf.DEL_METHODS) and subscribe_exist:
            user.subscribe.remove(author)
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(status=HTTP_400_BAD_REQUEST)

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        """Список подписок пользоваетеля.

        Вызов метода через url: */user/<int:id>/subscribtions/.

        Args:
            request (Request): Не используется.

        Returns:
            Responce:
                401 - для неавторизованного пользователя.
                Список подписок для авторизованного пользователя.
        """
        user = self.request.user
        authors = user.subscribe.all()
        pages = self.paginate_queryset(authors)
        serializer = UserSubscribeSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    """Работает с тэгами.

    Изменение и создание тэгов разрешено только админам.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)


class IngredientViewSet(ReadOnlyModelViewSet):
    """Работет с игридиентами.

    Изменение и создание ингридиентов разрешено только админам.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)

    def get_queryset(self):
        """Получает queryset в соответствии с параметрами запроса.

        Реализован поиск объектов по совпадению в начале названия,
        также добавляются результаты по совпадению в середине.
        При наборе названия в неправильной раскладке - латинские символы
        преобразуются в кириллицу (для стандартной раскладки).
        Также прописные буквы преобразуются в строчные,
        так как все ингридиенты в базе записаны в нижнем регистре.

        Returns:
            QuerySet: Список запрошенных объектов.

        TODO: `exclude` in queryset.
        """
        name = self.request.query_params.get(conf.SEARCH_ING_NAME)
        queryset = self.queryset
        if name:
            if name[0] == '%':
                name = unquote(name)
            else:
                name = name.translate(incorrect_layout)
            name = name.lower()
            stw_queryset = list(queryset.filter(name__istartswith=name))
            cnt_queryset = queryset.filter(name__icontains=name)
            stw_queryset.extend(
                [i for i in cnt_queryset if i not in stw_queryset]
            )
            queryset = stw_queryset
        return queryset


class RecipeViewSet(ModelViewSet, AddDelViewMixin):
    """Работает с рецептами.

    Вывод, создание, редактирование, добавление/удаление
    в избранное и список покупок.
    Отправка текстового файла со списком покупок.
    Для авторизованных пользователей — возможность добавить
    рецепт в избранное и в список покупок.
    Изменять рецепт может только автор или админы.
    """
    queryset = Recipe.objects.select_related('author')
    serializer_class = RecipeSerializer
    permission_classes = (AuthorStaffOrReadOnly,)
    pagination_class = PageLimitPagination
    add_serializer = ShortRecipeSerializer

    def get_queryset(self):
        """Получает queryset в соответствии с параметрами запроса.

        Returns:
            QuerySet: Список запрошенных объектов.
        """
        queryset = self.queryset

        tags = self.request.query_params.getlist(conf.TAGS)
        if tags:
            queryset = queryset.filter(
                tags__slug__in=tags).distinct()

        author = self.request.query_params.get(conf.AUTHOR)
        if author:
            queryset = queryset.filter(author=author)

        # Следующие фильтры только для авторизованного пользователя
        user = self.request.user
        if user.is_anonymous:
            return queryset

        is_in_shopping = self.request.query_params.get(conf.SHOP_CART)
        if is_in_shopping in conf.SYMBOL_TRUE_SEARCH:
            queryset = queryset.filter(cart__user=user.id)
        elif is_in_shopping in conf.SYMBOL_FALSE_SEARCH:
            queryset = queryset.exclude(cart__user=user.id)

        is_favorited = self.request.query_params.get(conf.FAVORITE)
        if is_favorited in conf.SYMBOL_TRUE_SEARCH:
            queryset = queryset.filter(favorite__user=user.id)
        if is_favorited in conf.SYMBOL_FALSE_SEARCH:
            queryset = queryset.exclude(favorite__user=user.id)

        return queryset

    @action(
        methods=conf.ACTION_METHODS,
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        """Добавляет/удалет рецепт в `избранное`.

        Вызов метода через url: */recipe/<int:pk>/favorite/.

        Args:
            request (Request): Не используется.
            pk (int, str):
                id рецепта, который нужно добавить/удалить из `избранного`.

        Returns:
            Responce: Статус подтверждающий/отклоняющий действие.
        """
        return self.add_del_obj(recipe_id=pk, m2m_model=Favorite)


    @action(
        methods=conf.ACTION_METHODS,
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        """Добавляет/удалет рецепт в `список покупок`.

        Вызов метода через url: *//recipe/<int:pk>/shopping_cart/.

        Args:
            request (Request): Не используется.
            pk (int, str):
                id рецепта, который нужно добавить/удалить в `корзину покупок`.

        Returns:
            Responce: Статус подтверждающий/отклоняющий действие.
        """
        return self.add_del_obj(recipe_id=pk, m2m_model=Cart)

    @action(methods=('get',), detail=False)
    def download_shopping_cart(self, request):
        """Загружает файл *.txt со списком покупок.

        Считает сумму ингредиентов в рецептах выбранных для покупки.
        Возвращает текстовый файл со списком ингредиентов.
        Вызов метода через url:  */recipe/<int:id>/download_shopping_cart/.

        Args:
            request (Request): Не используется.

        Returns:
            Responce: Ответ с текстовым файлом.
        """
        user = self.request.user
        if not user.carts.exists():
            return Response(status=HTTP_400_BAD_REQUEST)
        ingredients = AmountIngredient.objects.filter(
            recipe__in=(user.carts.values('id'))
        ).values(
            ingredient=F('ingredients__name'),
            measure=F('ingredients__measurement_unit')
        ).annotate(amount=Sum('amount'))

        filename = f'{user.username}_shopping_list.txt'
        shopping_list = (
            f'Список покупок для:\n\n{user.first_name}\n\n'
            f'{dt.now().strftime(conf.DATE_TIME_FORMAT)}\n\n'
        )
        for ing in ingredients:
            shopping_list += (
                f'{ing["ingredient"]}: {ing["amount"]} {ing["measure"]}\n'
            )

        shopping_list += '\n\nПосчитано в Foodgram'

        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
