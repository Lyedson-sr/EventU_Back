from rest_framework.serializers import ModelSerializer, CharField, ValidationError
from .models import CustomUser


class UserRegistrationSerializer(ModelSerializer):
    password = CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = ["email", "name", "role", "password"]
        extra_kwargs = {"role": {"required": True}}

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise ValidationError("Erro ao cadastrar com esse email.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "name",
            "role",
            "preferred_calendar_view",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
