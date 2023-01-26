from rest_framework import permissions


class AuthorStaffOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """
    Разрешение на изменение только для служебного персонала и автора.
    Остальным только чтение объекта.
    """
    def has_object_permission(self, request, view, obj):
        return bool(request.user == obj.author or request.user.is_staff)


class AdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение на создание и изменение только для админов.
    Остальным только чтение объекта.
    """
    def has_permission(self, request, view):
        return (
                request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                or request.user.is_admin
            )


class OwnerUserOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """
    Разрешение на изменение только для админа и пользователя.
    Остальным только чтение объекта.
    """
    def has_object_permission(self, request, view, obj):
        return bool(obj.owner == request.user or request.user.is_admin)

