from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiResponse,
)
from .serializers import (
    RegisterResponseSerializer,
    AuthResponseSerializer,
    MessageResponseSerializer,
)


auth_schema = extend_schema_view(
    register=extend_schema(
        summary="Registra um usuário no sistema",
        description="Registra um usuário e gera os tokens de autenticação",
        tags=["auth"],
        responses={
            201: RegisterResponseSerializer,
        }
    ),
    activate_account=extend_schema(
        summary="Ativa a conta de um usuário",
        description="Registra o campo is_active como True",
        tags=["auth"],
        responses={
            200: AuthResponseSerializer,
        }
    ),
    login=extend_schema(
        summary="Autentica o usuário",
        description="Realiza o login do usuário e fornece o token para salvar",
        tags=["auth"],
        responses={
            200: AuthResponseSerializer,
        }
    ),
    forgot_password=extend_schema(
        summary="Solicita código para redefinição de senha",
        description="Recebe um pedido de reset de senha e envia código para o email do usuário",
        tags=["auth"],
        responses={
            200: MessageResponseSerializer,
        }
    ),
    reset_password=extend_schema(
        summary="Solicita código para redefinição de senha",
        description="Recebe um pedido de reset de senha e envia código para o email do usuário",
        tags=["auth"],
        responses={
            200: MessageResponseSerializer,
        }
    ),
)
