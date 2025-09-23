from django.urls import path

from .views import LoginView, logout_view, verify_email, request_verification_code

urlpatterns = [
    path('login/', LoginView.as_view(), name="login"),
    path('logout/', logout_view, name="logout"),
    path('verify-email/', verify_email, name="verify-email"),
    path('request-verification-code/', request_verification_code, name="request-verification-code"),
]