from rest_framework.permissions import (BasePermission,
IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)


class AuthorStaffOrReadOnly(BasePermission):# IsAuthenticatedOrReadOnly):
    """
    Разрешение на изменение только для служебного персонала и автора.
    Остальным только чтение объекта.
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.method in ('GET',)
            or request.user.is_authenticated
            and request.user.active
            and (
                request.user == obj.author
                or request.user.is_staff
            )
        )


class AdminOrReadOnly(BasePermission):
    """
    Разрешение на создание и изменение только для админов.
    Остальным только чтение объекта.
    """
    def has_permission(self, request, view):
        return (
            request.method in ('GET',)
            or request.user.is_authenticated
            and request.user.active
            and request.user.is_admin
        )


class AdminOwnerUserOrReadOnly(IsAuthenticatedOrReadOnly):
    """
    Разрешение на изменение только для админа и пользователя.
    Остальным только чтение объекта.
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.method in ('GET',)
            or (
                request.user.is_authenticated
                and request.user.active
                and (
                    request.user == obj
                    or request.user.is_admin
                )
            )
        )
