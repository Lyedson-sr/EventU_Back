from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    EmailField,
    CharField,
    ValidationError,
)
from .models import CustomUser
from .services.activation_services import ActivationService


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


class UserActivationSerializer(Serializer):
    email = EmailField()
    code = CharField(max_length=4, min_length=4)

    def validate(self, attrs):
        email = attrs.get("email")
        code = attrs.get("code")

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise ValidationError("Usuário não encontrado.")

        if user.is_active:
            raise ValidationError("Esta conta já está ativa.")

        if not ActivationService.verify_activation_code(user.id, code):
            raise ValidationError("Código de ativação inválido ou expirado.")

        attrs["user"] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data["user"]
        user.is_active = True
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
