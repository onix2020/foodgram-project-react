"""Модуль вспомогательных функций.
"""

from string import hexdigits

from recipes.models import AmountIngredient
from rest_framework.serializers import ValidationError


def recipe_amount_ingredients_set(recipe, ingredients):
    """Записывает ингредиенты вложенные в рецепт.

    Создаёт объект AmountIngredient связывающий объекты Recipe и
    Ingredient с указанием количества(`amount`) конкретного ингридиента.

    Args:
        recipe (Recipe):
            Рецепт, в который нужно добавить игридиенты.
        ingridients (list):
            Список ингридентов и количества сих.
    """
    for ingredient in ingredients:
        AmountIngredient.objects.get_or_create(
            recipe=recipe,
            ingredients=ingredient['ingredient'],
            amount=ingredient['amount']
        )


def check_value_validate(value, klass=None, minimum=None, maximum=None):
    """Проверяет корректность переданного значения.

    Если передан класс, проверяет существует ли объект с переданным obj_id.
    При нахождении объекта создаётся Queryset[],
    для дальнейшей работы возвращается первое (и единственное) значение.
    Если указаны аргументы `minimum` или `maximum`,
    то переданное значение должно быть приводимым к типу `int`.

    Args:
        value (int, str):
            Значение, переданное для проверки.
        klass (class):
            Если значение передано, проверяет наличие объекта с id=value.
        minimum (int):
            Минимально допустимое значение.
        maximum (int):
            Максимально допустимое значение.

    Returns:
        None:
            Если переданно только корректно значение.
        obj:
            Объект переданного класса, если дополнительно указан класс.

    Raises:
        ValidationError:
            Переданное значение не является числом.
        ValidationError:
            Объекта с указанным id не существует.
        ValidationError:
            Слишком маленькое значение.
        ValidationError:
            Слишком большое значение.

    """
    if not str(value).isdecimal():
        raise ValidationError(
            f'{value} должно содержать цифру'
        )
    if minimum is not None and int(value) < minimum:
        raise ValidationError(
            f'Слишком маленькое значение: {value}'
        )
    if maximum is not None and int(value) > maximum:
        raise ValidationError(
            f'Слишком большое значение: {value}'
        )
    if klass:
        obj = klass.objects.filter(id=value)
        if not obj:
            raise ValidationError(
                f'{value} не существует'
            )
        return obj[0]


def is_hex_color(value):
    """Проверяет - может ли значение быть шестнадцатеричным цветом.

    Args:
        value (str):
            Значение переданное для проверки.

    Raises:
        ValidationError:
            Переданное значение не корректной длины.
        ValidationError:
            Символы значения выходят за пределы 16-ричной системы.
    """
    if len(value) not in (3, 6):
        raise ValidationError(
            f'{value} не правильной длины ({len(value)}).'
        )
    if not set(value).issubset(hexdigits):
        raise ValidationError(
            f'{value} не шестнадцатиричное.'
        )


# Словарь для сопостановления латинской и русской стандартных раскладок.
incorrect_layout = str.maketrans(
    'qwertyuiop[]asdfghjkl;\'zxcvbnm,./',
    'йцукенгшщзхъфывапролджэячсмитьбю.'
)
