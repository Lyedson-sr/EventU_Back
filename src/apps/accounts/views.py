from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    UserActivationSerializer,
    UserLoginSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from .schemas import auth_schema
from .services.activation_services import ActivationService
from .services.password_reset_services import PasswordResetService


@auth_schema
class AuthViewSet(ModelViewSet):
    queryset = CustomUser.objects.none()
    permission_classes = [AllowAny]
    http_method_names = ["post"]

    def get_serializer_class(self):
        if self.action == "register":
            return UserRegistrationSerializer
        elif self.action == "activate_account":
            return UserActivationSerializer
        elif self.action == "login":
            return UserLoginSerializer
        elif self.action == "forgot_password":
            return PasswordResetRequestSerializer
        elif self.action == "reset_password":
            return PasswordResetConfirmSerializer
        return UserSerializer

    @action(detail=False, methods=["post"])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        activation_code = ActivationService.generate_activation_code(user.id)
        ActivationService.send_activation_email(user, activation_code)

        return Response(
            {
                "message": "Conta criada com sucesso. Verifique seu email para o código de ativação",
                "data": {"email": user.email, "user_id": user.id},
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"])
    def activate_account(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Conta ativada com sucesso.",
                "data": UserSerializer(user).data,
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            }
        )
    
    @action(detail=False, methods=["post"])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Login realizado com sucesso.",
                "data": UserSerializer(user).data,
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                }
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"])
    def forgot_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = CustomUser.objects.get(email=serializer.validated_data["email"])
            PasswordResetService.send_reset_email(user)
        except CustomUser.DoesNotExist:
            pass

        return Response(
            {
                "message": "Se o email existir, você receberá um código para redefinir a senha."
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=["post"])
    def reset_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            PasswordResetService.reset_password(
                email=serializer.validated_data["email"],
                code=serializer.validated_data["code"],
                new_password=serializer.validated_data["new_password"],
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(
            {"message": "Senha redefinida com sucesso."},
            status=status.HTTP_200_OK
        )
