from rest_framework import permissions


class AuthorOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)


class IsAuthorOnly(permissions.BasePermission):
    """Класс для предоставления прав внесения изменений автору объекта."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class IsAuthorOnlyPermission(permissions.IsAuthenticatedOrReadOnly,
                             IsAuthorOnly):
    """Класс, предосталяющий права неавторизованному пользователю на просмотр,
    а на действия, связанные с изменением состояния объекта, только автору."""
    pass