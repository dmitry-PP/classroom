from django.contrib.auth import login, logout
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response

from .serializers import LoginUserSerializer, UserProfileSerializer

from django.utils import timezone
from .models import CustomUser, VerifiedCodesModel


class LoginView(generics.GenericAPIView):
    serializer_class = LoginUserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        login(request, user)

        return Response({
            'user': UserProfileSerializer(user).data,
            'message': 'Успешный вход',
            'requires_verification': not user.is_verified  
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
    
    try:
        verification_code = VerifiedCodesModel.objects.get(user=user, code=code)
    except VerifiedCodesModel.DoesNotExist:
        return Response(
            {'error': 'Неверный код верификации'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if verification_code.is_expired():
        verification_code.delete()
        return Response(
            {'error': 'Срок действия кода истек'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user.is_verified = True
    user.save()
    verification_code.delete() 
    
    return Response(
        {'message': 'Email успешно верифицирован'},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def request_verification_code(request):
    from .services import send_verification_email
    
    email = request.data.get('email')
    
    if not email:
        return Response(
            {'error': 'Email обязателен'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return Response(
            {'error': 'Пользователь не найден'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if not user.is_verified:
        send_verification_email(user)
        return Response(
            {'message': 'Код верификации отправлен на email'},
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            {'message': 'Пользователь уже верифицирован'},
            status=status.HTTP_200_OK
        )