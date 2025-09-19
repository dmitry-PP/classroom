import os
from functools import partial


from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.utils import generate_random_string, file_upload_path
from classroom.settings import AUTH_USER_MODEL


class Courses(models.Model):

    MAX_ATTEMPTS_GENERATE_COURSE_ID = 5

    class ConfigPermissions(models.IntegerChoices):
        STUDENTS_ONLY_COMMENTS = 1, _("Students can only comment")
        TEACHERS_ONLY_PUBLISHED = 2, _("Only teachers can publish")
        ALL = 3, _("All permissions")

    class DeletePermission(models.IntegerChoices):
        CREATOR_ONLY = 0, _('Creator only')
        ALL_TEACHERS = 1, _('All teachers')
        NOT_DELETE = 2, _('Not delete')

    title = models.CharField(_("title"), max_length=100)
    description = models.TextField(_("description"))
    section = models.CharField(_("section"), max_length=50)
    room = models.CharField(_("room"), max_length=50)
    theme = models.CharField(_("theme"), max_length=50)
    inv_code = models.CharField(_("invite code"), max_length=8)
    course_id_base = models.CharField(_("course id"), unique=True, max_length=32)
    config_permission = models.PositiveSmallIntegerField(
        _("config perm"),
        choices=ConfigPermissions,
        default=ConfigPermissions.ALL
    )
    delete_permission = models.PositiveSmallIntegerField(
        _("delete perm"),
        choices=DeletePermission,
        default=DeletePermission.CREATOR_ONLY
    )

    creator = models.ForeignKey(
        AUTH_USER_MODEL,
        related_name="own_courses",
        verbose_name=_("creator"),
        on_delete=models.CASCADE
    )
    image = models.ImageField(
        _("course image"),
        upload_to=partial(file_upload_path, "course", directory="courses")
    )
    created_at = models.DateTimeField(_("created_at"), auto_now_add=True)
    is_archive = models.BooleanField(_("archive"), default=False)

    teachers = models.ManyToManyField(
        AUTH_USER_MODEL,
        through="CourseTeachersThrough",
        verbose_name=_("teachers"),
        related_name="teaching_courses"
    )
    students = models.ManyToManyField(
        AUTH_USER_MODEL,
        through="CourseStudentsThrough",
        verbose_name=_("students"),
        related_name="enrolled_courses"
    )

    def has_user_on_course(self, user):
        if user.is_admin or self.creator_id == user.pk:
            return True
        return (
            self.teacher_invites.filter(teacher=user, status='accepted').exists() or
            self.student_invites.filter(student=user, status='accepted').exists()
        )

    def can_user_delete(self, user):
        if user.is_admin:
            return True

        if self.delete_permission == self.DeletePermission.CREATOR_ONLY:
            return user.pk == self.creator_id
        elif self.delete_permission == self.DeletePermission.ALL_TEACHERS:
            return user.is_teacher and self.teachers.filter(pk=user.pk).exists()
        elif self.delete_permission == self.DeletePermission.NOT_DELETE:
            return False

    def can_user_comment(self, user):
        if user.is_admin:
            return True

        if self.config_permission == self.ConfigPermissions.ALL:
            return True
        elif self.config_permission == self.ConfigPermissions.STUDENTS_ONLY_COMMENTS:
            return True
        elif self.config_permission == self.ConfigPermissions.TEACHERS_ONLY_PUBLISHED:
            return user.is_teacher and self.teachers.filter(pk=user.pk).exists()

    def can_user_publish(self, user):
        if user.is_admin:
            return True

        if self.config_permission == self.ConfigPermissions.ALL:
            return True
        elif self.config_permission == self.ConfigPermissions.STUDENTS_ONLY_COMMENTS:
            return user.is_teacher and self.teachers.filter(pk=user.pk).exists()
        elif self.config_permission == self.ConfigPermissions.TEACHERS_ONLY_PUBLISHED:
            return user.is_teacher and self.teachers.filter(pk=user.pk).exists()

    def save(self, *args, **kwargs):
        # Генерируем поля только для новых объектов
        if self.pk == None:
            self.inv_code = generate_random_string(
                self._meta.get_field('inv_code').max_length,
                use_upper_case=False
            )

            for attempt in range(self.MAX_ATTEMPTS_GENERATE_COURSE_ID):

                self.course_id_base = generate_random_string(
                    self._meta.get_field('course_id_base').max_length
                )
                if self.__class__.objects.filter(course_id_base=self.course_id_base).exists():
                    self.course_id_base = None
                    continue
                break

            if self.course_id_base == None:
                raise ValueError("Something went wrong, please try again.")

        return super().save(*args, **kwargs)



class Status(models.TextChoices):
    PENDING = "pending", _("Pending")
    ACCEPTED = "accepted", _("Accepted")
    REJECTED = "rejected", _("Rejected")

class ActionMixin:

    def accept(self):
        self.accepted_at = timezone.now()
        self.status = self.Status.ACCEPTED
        self.save()

    def reject(self):
        self.status = self.Status.REJECTED
        self.save()

class CourseTeachersThrough(ActionMixin, models.Model):
    Status = Status

    teacher = models.ForeignKey(
        AUTH_USER_MODEL,
        related_name="teacher_course_invites",
        verbose_name=_("teacher"),
        on_delete=models.CASCADE
    )
    course = models.ForeignKey(
        "Courses",
        related_name="teacher_invites",
        verbose_name=_("course"),
        on_delete=models.CASCADE
    )

    invited_at = models.DateTimeField(_("invited_at"), auto_now_add=True)
    accepted_at = models.DateTimeField(_("accepted_at"), default=None)
    status = models.CharField(_("status"), choices=Status, default=Status.PENDING, max_length=20)

    class Meta:
        unique_together = ("teacher", "course")

class CourseStudentsThrough(ActionMixin, models.Model):
    Status = Status

    student = models.ForeignKey(
        AUTH_USER_MODEL,
        related_name="course_invites",
        verbose_name=_("student"),
        on_delete=models.CASCADE
    )
    course = models.ForeignKey(
        "Courses",
        related_name="student_invites",
        verbose_name=_("course"),
        on_delete=models.CASCADE
    )

    invited_at = models.DateTimeField(_("invited_at"), auto_now_add=True)
    accepted_at = models.DateTimeField(_("accepted_at"), default=None)
    status = models.CharField(_("status"), choices=Status, default=Status.PENDING, max_length=20)

    class Meta:
        unique_together = ("student", "course")