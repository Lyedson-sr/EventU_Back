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
)
from .schemas import auth_schema
from .services.activation_services import ActivationService


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
