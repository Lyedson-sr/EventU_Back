from django.urls import path
from .views import AuthViewSet


urlpatterns = [
    path("register/", AuthViewSet.as_view({"post": "register"}), name="user_register"),
]