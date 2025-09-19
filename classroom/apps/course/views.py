from django.db.models import Q
from rest_framework.decorators import api_view, action
from rest_framework import generics
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import CoursePreviewSerializer, CourseProfileSerializer
from .models import Courses




class CourseViewSet(viewsets.ModelViewSet):
    queryset = Courses.objects.select_related("creator")
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "course_id_base"
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['title', 'section', 'theme', 'is_archive']

    def get_serializer_class(self):
        if self.action in ['list', 'get_own_courses']:
            return CoursePreviewSerializer
        return CourseProfileSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if self.action == "get_own_courses":
            return queryset.filter(creator_id=user.pk)
        if self.action in ['list', 'retrieve']:
            queryset = queryset.prefetch_related('teachers', 'students')

        if user.is_admin:
            return queryset
        elif user.is_student:
            return queryset.filter(
                student_invites__student=user,
                student_invites__status='accepted'
            )
        elif user.is_teacher:
            print('here')
            return queryset.filter(
                Q(teacher_invites__teacher=user) & Q(teacher_invites__status='accepted') | Q(creator=user),
            )
        return queryset.none()

    @action(detail=False, methods=["get"])
    def get_own_courses(self, request):
        return Response({
            "courses": CoursePreviewSerializer(self.get_queryset(), many=True).data
        })

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.has_user_on_course(request.user):
            raise PermissionDenied()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_destroy(self, instance):
        if not instance.can_user_delete(self.request.user):
            raise PermissionDenied()
        super().perform_destroy(instance)