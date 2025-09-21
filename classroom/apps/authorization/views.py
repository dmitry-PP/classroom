from django.contrib.auth import login, logout
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response

from .serializers import LoginUserSerializer, UserProfileSerializer

from django.utils import timezone
from apps.utils import is_verification_code_expired
from .services import send_verification_email


class LoginView(generics.GenericAPIView):
    serializer_class = LoginUserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        if not user.is_verified:
            print(f"Отправляем код верификации для {user.email}")
            send_verification_email(user)

        login(request, user)

        return Response({
            'user': UserProfileSerializer(user).data,
            'message': 'Код верификации отправлен на email' if not user.is_verified else 'Успешный вход'
        }, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({
        "message": "Logout successful"
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_email(request):
    """Подтверждение email с помощью кода верификации"""
    email = request.data.get('email')
    code = request.data.get('code')
    
    if not email or not code:
        return Response(
            {'error': 'Email и код обязательны'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return Response(
            {'error': 'Пользователь не найден'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if not user.verification_code or user.verification_code != code:
        return Response(
            {'error': 'Неверный код верификации'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if is_verification_code_expired(user.verification_code_sent_at):
        return Response(
            {'error': 'Срок действия кода истек'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user.is_verified = True
    user.verification_code = None 
    user.verification_code_sent_at = None
    user.save()
    
    return Response(
        {'message': 'Email успешно верифицирован'},
        status=status.HTTP_200_OK
    )