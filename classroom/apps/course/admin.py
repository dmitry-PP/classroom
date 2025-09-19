from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Courses, CourseTeachersThrough, CourseStudentsThrough

# Инлайн для преподавателей
class CourseTeachersThroughInline(admin.TabularInline):
    model = CourseTeachersThrough
    extra = 1  # Количество пустых форм для добавления новых преподавателей
    verbose_name = _("Teacher")
    verbose_name_plural = _("Teachers")
    fields = ('teacher', 'status', 'invited_at', 'accepted_at')
    readonly_fields = ('invited_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('teacher')

# Инлайн для студентов
class CourseStudentsThroughInline(admin.TabularInline):
    model = CourseStudentsThrough
    extra = 1  # Количество пустых форм для добавления новых студентов
    verbose_name = _("Student")
    verbose_name_plural = _("Students")
    fields = ('student', 'status', 'invited_at', 'accepted_at')
    readonly_fields = ('invited_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student')

@admin.register(Courses)
class CoursesAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'room', 'creator', 'config_permission', 'delete_permission', 'is_archive', 'created_at')
    list_filter = ('is_archive', 'config_permission', 'delete_permission', 'created_at')
    search_fields = ('title', 'section', 'room', 'theme', 'inv_code', 'course_id_base', 'creator__username')
    readonly_fields = ('created_at', 'inv_code', 'course_id_base')
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'section', 'room', 'theme', 'image')
        }),
        (_('Permissions'), {
            'fields': ('config_permission', 'delete_permission')
        }),
        (_('Metadata'), {
            'fields': ('creator', 'inv_code', 'course_id_base', 'created_at', 'is_archive')
        }),
    )
    inlines = [CourseTeachersThroughInline, CourseStudentsThroughInline]  # Добавляем инлайн-админки

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('creator').prefetch_related('teachers', 'students')

@admin.register(CourseTeachersThrough)
class CourseTeachersThroughAdmin(admin.ModelAdmin):
    list_display = ('course', 'teacher', 'status', 'invited_at', 'accepted_at')
    list_filter = ('status', 'invited_at')
    search_fields = ('course__title', 'teacher__username')
    readonly_fields = ('invited_at',)
    fieldsets = (
        (None, {
            'fields': ('course', 'teacher', 'status')
        }),
        (_('Timestamps'), {
            'fields': ('invited_at', 'accepted_at')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('course', 'teacher')

@admin.register(CourseStudentsThrough)
class CourseStudentsThroughAdmin(admin.ModelAdmin):
    list_display = ('course', 'student', 'status', 'invited_at', 'accepted_at')
    list_filter = ('status', 'invited_at')
    search_fields = ('course__title', 'student__username')
    readonly_fields = ('invited_at',)
    fieldsets = (
        (None, {
            'fields': ('course', 'student', 'status')
        }),
        (_('Timestamps'), {
            'fields': ('invited_at', 'accepted_at')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('course', 'student')