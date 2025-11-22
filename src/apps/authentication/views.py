from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    UserRegistrationSerializer,
    UserActivationSerializer,
    UserLoginSerializer,
    UserLogoutSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    UserSerializer,
)
from .services.activation_services import ActivationService
from .services.password_reset_services import PasswordResetService
from .schemas import (
    register_schema,
    activate_account_schema,
    forgot_password_schema,
    # reset_password_schema,
    login_schema,
    logout_schema,
)
from apps.users.models import User


@register_schema
class RegistrationView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        activation_code = ActivationService.generate_activation_code(user)
        ActivationService.send_activation_email(user, activation_code)

        return Response(
            {
                "message": _(
                    "Conta criada com sucesso. Verifique seu email para ativação."
                ),
                "data": {"email": user.email, "user_id": user.id},
            },
            status=201,
        )


@activate_account_schema
class ActivateAccountView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserActivationSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": _("Conta ativada com sucesso."),
                "data": UserSerializer(user).data,
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
            status=200,
        )


@forgot_password_schema
class ForgotPasswordView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()

        if user:
            PasswordResetService.send_reset_email(user)

        return Response(
            {"message": _("Se o email existir, enviaremos um código de redefinição.")},
            status=200,
        )


# @reset_password_schema
class ResetPasswordView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            PasswordResetService.reset_password(
                email=serializer.validated_data["email"],
                code=serializer.validated_data["code"],
                new_password=serializer.validated_data["new_password"],
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)

        return Response(
            {"message": _("Senha redefinida com sucesso.")},
            status=200,
        )


@login_schema
class LoginView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        if not user.is_active:
            return Response({"detail": _("Conta não ativada.")}, status=400)

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": _("Login realizado com sucesso."),
                "data": UserSerializer(user).data,
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
            status=200,
        )


@logout_schema
class LogoutView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserLogoutSerializer

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response({"detail": "Refresh token é obrigatório."}, status=400)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Logout realizado com sucesso."}, status=200)
        except Exception:
            return Response({"detail": "Token inválido."}, status=400)
