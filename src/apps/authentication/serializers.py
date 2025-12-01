from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    EmailField,
    CharField,
    ValidationError,
    IntegerField,
)
from apps.users.models import User
from apps.users.serializers import UserSerializer
from .services.activation_services import ActivationService
from .services.password_reset_services import PasswordResetService
from utils.validators import validate_unique_email
from django.contrib.auth import authenticate
from django.core.cache import cache


class UserRegistrationSerializer(ModelSerializer):
    password = CharField(write_only=True, min_length=8)
    email = EmailField(validators=[validate_unique_email])

    class Meta:
        model = User
        fields = ["email", "name", "role", "password"]
        extra_kwargs = {"role": {"required": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserActivationSerializer(Serializer):
    email = EmailField()
    code = CharField(max_length=4, min_length=4)

    def validate(self, attrs):
        email = attrs.get("email")
        code = attrs.get("code")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError(
                detail="Usuário não encontrado.",
                code="invalid"
            )

        if user.is_active:
            raise ValidationError(
                detail="Esta conta já está ativa.",
                code="invalid"
            )

        if not ActivationService.verify_activation_code(user.id, code):
            raise ValidationError(
                detail="Código de ativação inválido ou expirado.",
                code="invalid"
            )

        attrs["user"] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data["user"]
        user.is_active = True
        user.save()
        return user


class UserLoginSerializer(Serializer):
    email = EmailField()
    password = CharField(write_only=True)
    role = CharField(required=True, write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        requested_role = attrs.get("role") 

        user = authenticate(username=email, password=password)

        if not user:
            raise ValidationError(
                detail="Credenciais inválidas.",
                code="invalid"
            )

        if not user.is_active:
            raise ValidationError(
                detail="Conta inativa ou não verificada.",
                code="invalid"
            )
        
        if requested_role and user.role != requested_role:
            raise ValidationError(
                detail="Erro ao fazer login.",
                code="invalid"
            )
        
        attrs["user"] = user
        return attrs
    

class UserLogoutSerializer(Serializer):
    refresh_token = CharField(required=True)
    

class PasswordResetRequestSerializer(Serializer):
    email = EmailField()


class InformCodeSerializer(Serializer):
    email = EmailField()
    code = CharField(max_length=4, min_length=4)

    def validate(self, attrs):
        email = attrs.get("email")
        code = attrs.get("code")

        # Verifica se o código é válido
        if not PasswordResetService.verify_code(email, code):
            raise ValidationError(
                detail="Código inválido ou expirado.",
                code="invalid"
            )

        return attrs


class PasswordResetConfirmSerializer(Serializer):
    email = EmailField()
    new_password = CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        email = attrs.get("email")

        # Verifica se o usuário existe
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError(
                detail="Email inválido.",
                code="invalid"
            )

        if not cache.get(f"password_reset_{user.id}"):
            raise ValidationError(
                detail="Código não validado ou expirado.",
                code="invalid"
            )

        return attrs

    def save(self, **kwargs):
        email = self.validated_data["email"]
        new_password = self.validated_data["new_password"]
        
        user = PasswordResetService.reset_password(email, new_password)
        return user


class TokenResponseSerializer(Serializer):
    access = CharField()
    refresh = CharField()


class UserRegisterResponseSerializer(Serializer):
    email = EmailField()
    user_id = IntegerField()


class RegisterResponseSerializer(Serializer):
    message = CharField()
    data = UserRegisterResponseSerializer()


class AuthResponseSerializer(Serializer):
    message = CharField()
    data = UserSerializer()
    tokens = TokenResponseSerializer()
