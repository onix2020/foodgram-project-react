from rest_framework import permissions


class AuthorStaffOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """
    Разрешение на изменение только для служебного персонала и автора.
    Остальным только чтение объекта.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return bool (request.user == obj.author or request.user.is_staff)



class AdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение на создание и изменение только для админов.
    Остальным только чтение объекта.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return bool(request.user and request.user.is_staff)


class OwnerUserOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """
    Разрешение на изменение только для админа и пользователя.
    Остальным только чтение объекта.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return bool(obj.owner == request.user or obj.owner == request.user.is_staff)

