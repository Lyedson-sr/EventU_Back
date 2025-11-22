from rest_framework.serializers import ModelSerializer
from .models import Group, GroupMember


class GroupCreateSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = [
            "id",
            "name",
            "description",
            "color",
            "created_at"
        ]
        read_only_fields = ["id", "created_at"]


class GroupRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = [
            "id",
            "creator",
            "name",
            "description",
            "color",
            "created_at",
        ]


class GroupPatchSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = [
            "id",
            "name",
            "description",
            "color",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
        
