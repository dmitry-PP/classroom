from django.contrib.auth import login, logout
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response

from .serializers import LoginUserSerializer, UserProfileSerializer


class LoginView(generics.GenericAPIView):
    serializer_class = LoginUserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        login(request, user)

        return Response({
            'user': UserProfileSerializer(user).data
        }, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({
        "message": "Logout successful"
    }, status=status.HTTP_200_OK)