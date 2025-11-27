from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GroupViewSet, GroupMemberViewSet


router = DefaultRouter()
router.register(r"", GroupViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("<int:group_pk>/members/", GroupMemberViewSet.as_view({
        "get": "list",
        "post": "create"
    }), name="group-members-list"),
    path("<int:group_pk>/members/<int:pk>/", GroupMemberViewSet.as_view({
        "delete": "destroy"
    }), name="group-member-detail"),
]
