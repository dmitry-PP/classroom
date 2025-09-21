from django.urls import path

from .views import LoginView, logout_view, verify_email


urlpatterns = [
    path('login/', LoginView.as_view(), name="login"),
    path('logout/', logout_view, name="logout"),
    path('verify-email/', verify_email, name="verify-email"),
]