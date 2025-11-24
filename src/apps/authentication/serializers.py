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
from django.contrib.auth import authenticate
from django.core.cache import cache


class UserRegistrationSerializer(ModelSerializer):
    password = CharField(write_only=True, min_length=8)

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


class UserLoginSerializer(Serializer):
    email = EmailField()
    password = CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(username=email, password=password)

        if not user:
            raise ValidationError("Credenciais inválidas")

        if not user.is_active:
            raise ValidationError("Conta inativa ou não verificada.")
        
        attrs["user"] = user
        return attrs
    

class UserLogoutSerializer(Serializer):
    refresh_token = CharField(required=True)
    

class PasswordResetRequestSerializer(Serializer):
    email = EmailField()


class InformCodeSerializer(Serializer):
    email = EmailField()  # ← Adicionei email aqui também
    code = CharField(max_length=4, min_length=4)

    def validate(self, attrs):
        email = attrs.get("email")
        code = attrs.get("code")

        # Verifica se o código é válido
        if not PasswordResetService.verify_code(email, code):
            raise ValidationError("Código inválido ou expirado.")

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
            raise ValidationError("Email inválido.")

        # Verifica se há um código válido no cache (usuário já validou o código)
        if not cache.get(f"password_reset_{user.id}"):
            raise ValidationError("Código não validado ou expirado.")

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
