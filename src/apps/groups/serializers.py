from rest_framework.serializers import ModelSerializer, EmailField, ValidationError
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


class GroupMemberCreateSerializer(ModelSerializer):
    email = EmailField(write_only=True)

    class Meta:
        model = GroupMember
        fields = [
            "id",
            "user",
            "email",
            "joined_at"
        ]
        read_only_fields = ["id", "joined_at", "user"]

    def validate(self, attrs):
        from apps.users.models import User
        
        email = attrs.pop('email', None)
        group_pk = self.context['view'].kwargs.get('group_pk')
        
        if email:
            try:
                user = User.objects.get(email=email)
                attrs['user'] = user
            except User.DoesNotExist:
                raise ValidationError("Usuário não encontrado.")
        
        # Verifica se usuário já é membro do grupo
        if GroupMember.objects.filter(group_id=group_pk, user=attrs['user']).exists():
            raise ValidationError("Este usuário já é membro do grupo.")
        
        return attrs

    def create(self, validated_data):
        return super().create(validated_data)
    

class GroupMemberListSerializer(ModelSerializer):
    class Meta:
        model = GroupMember
        fields = [
            "id",
            "user",
            "joined_at"
        ]
