"""Модуль содержит дополнительные классы
для настройки основных классов приложения.
"""

from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED)

from . import conf


class AddDelViewMixin:
    """
    Добавляет во Viewset дополнительные методы.

    Содержит метод добавляющий/удаляющий объект связи
    Many-to-Many между моделями.
    Требует определения атрибута `add_serializer`.

    Example:
        class ExampleViewSet(ModelViewSet, AddDelViewMixin)
            ...
            add_serializer = ExamplSerializer

            def example_func(self, request, **kwargs):
                ...
                obj_id = ...
                return self.add_del_obj(obj_id, meneger.M2M)
    """

    add_serializer = None

    def add_del_obj(self, recipe_id, m2m_model):
        """Добавляет/удаляет связи M2M между пользователеми и рецептами.

        Args:
            recipe_id (int):
                id рецепта, с которым требуется создать/удалить связь.
            m2m_model (Model):
                М2M модель управляющая требуемой связью.

        Returns:
            Responce: Статус подтверждающий/отклоняющий действие.
        """
        assert self.add_serializer is not None, (
            f'{self.__class__.__name__} should include '
            'an `add_serializer` attribute.'
        )

        user = self.request.user
        if user.is_anonymous:
            return Response(status=HTTP_401_UNAUTHORIZED)

        recipe = get_object_or_404(self.queryset, id=recipe_id)

        serializer = self.add_serializer(
            recipe, context={'request': self.request}
        )
        m2m_instance = m2m_model.objects.filter(recipe=recipe_id, user=user)

        if (self.request.method in conf.ADD_METHODS) and not m2m_instance:
            m2m_model(recipe=recipe, user=user).save()
            return Response(serializer.data, status=HTTP_201_CREATED)

        if (self.request.method in conf.DEL_METHODS) and m2m_instance:
            m2m_instance[0].delete()
            return Response(status=HTTP_204_NO_CONTENT)
        return Response(status=HTTP_400_BAD_REQUEST)
