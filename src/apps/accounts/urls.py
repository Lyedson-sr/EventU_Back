from django.urls import path
from .views import AuthViewSet


urlpatterns = [
    path("register/", AuthViewSet.as_view({"post": "register"}), name="user_register"),
    path("activate-account/", AuthViewSet.as_view({"post": "activate_account"}), name="activate_account"),
    path("login/", AuthViewSet.as_view({"post": "login"}), name="login"),
    path("forgot-password", AuthViewSet.as_view({"post": "forgot_password"}), name="forgot_password"),
    path("reset-password", AuthViewSet.as_view({"post": "reset_password"}), name="reset_password"),
]