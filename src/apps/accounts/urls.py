from django.urls import path
from .views import AuthViewSet


urlpatterns = [
    path("register/", AuthViewSet.as_view({"post": "register"}), name="user_register"),
    path("activate-account/", AuthViewSet.as_view({"post": "activate_account"}), name="activate_account"),
]