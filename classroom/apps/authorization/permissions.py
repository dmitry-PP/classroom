from rest_framework import permissions
from django.utils.translation import gettext_lazy as _
from .services import send_verification_email

class IsVerified(permissions.BasePermission):
    message = _("Пользователь не верифицирован. Доступ запрещен.")
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if request.user.is_verified:
            return True
            
        if not request.user.is_verified:
            send_verification_email(request.user)
            
        return False
        