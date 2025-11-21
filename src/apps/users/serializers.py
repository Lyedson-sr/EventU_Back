from rest_framework.serializers import ModelSerializer
from .models import User


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "role",
            "preferred_calendar_view",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class UserRetrieveSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "role",
            "preferred_calendar_view",
            "is_active",
        ]


class UserPatchSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "preferred_calendar_view",
        ]
        