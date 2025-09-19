# apps/authorization/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Поля для отображения в списке
    list_display = [
        'email',
        'get_fullname',
        'role_id',
        'is_verified',
        'is_active',
        'created_at'
    ]

    # Поля для фильтрации
    list_filter = [
        'role_id',
        'is_verified',
        'is_active',
        'created_at'
    ]

    # Поля для поиска
    search_fields = [
        'email',
        'first_name',
        'second_name',
        'last_name'
    ]

    # Порядок сортировки
    ordering = ['-created_at']

    # Поля только для чтения
    readonly_fields = ['created_at', 'updated_at']

    # Группировка полей в форме редактирования
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {
            'fields': (
                'first_name',
                'second_name',
                'last_name',
                'avatar'
            )
        }),
        (_('Permissions'), {
            'fields': (
                'role_id',
                'is_verified',
                'is_active',
                'groups',
                'user_permissions',
            ),
        }),
        (_('Important dates'), {
            'fields': (
                'created_at',
                'updated_at'
            )
        }),
    )

    # Поля при создании пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'first_name',
                'second_name',
                'last_name',
                'role_id',
                'is_verified',
                'is_active'
            ),
        }),
    )

    # Действия в админке
    actions = ['verify_users', 'unverify_users', 'activate_users', 'deactivate_users']

    def verify_users(self, request, queryset):
        """Верифицировать выбранных пользователей"""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f"{updated} пользователей верифицировано.")

    verify_users.short_description = _("Verify selected users")

    def unverify_users(self, request, queryset):
        """Снять верификацию с выбранных пользователей"""
        updated = queryset.update(is_verified=False)
        self.message_user(request, f"Верификация снята с {updated} пользователей.")

    unverify_users.short_description = _("Unverify selected users")

    def activate_users(self, request, queryset):
        """Активировать выбранных пользователей"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} пользователей активировано.")

    activate_users.short_description = _("Activate selected users")

    def deactivate_users(self, request, queryset):
        """Деактивировать выбранных пользователей"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} пользователей деактивировано.")

    deactivate_users.short_description = _("Deactivate selected users")

    # Кастомные методы для отображения
    def get_fullname(self, obj):
        return obj.get_fullname()

    get_fullname.short_description = _('Full Name')

    # Настройка отображения роли
    def get_role_display(self, obj):
        return obj.get_role_display()

    get_role_display.short_description = _('Role')