from rest_framework import permissions

class IsVerified(permissions.BasePermission):
    """
    Разрешение, которое проверяет что пользователь верифицирован (is_verified=True)
    """
    message = "Пользователь не верифицирован. Доступ запрещен."

    def has_permission(self, request, view):
        # Проверяем что пользователь аутентифицирован и верифицирован
        return bool(request.user and request.user.is_authenticated and request.user.is_verified)

    def has_object_permission(self, request, view, obj):
        # Для объектных разрешений
        return self.has_permission(request, view)
        