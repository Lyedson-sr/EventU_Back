from django.urls import path
from rest_framework import routers
from .views import (
    UserAdminViewSet,
    UserViewSet
)

router = routers.DefaultRouter()
router.register(r"", UserAdminViewSet)

urlpatterns = [
    path("me/", UserViewSet.as_view()),
] + router.urls
