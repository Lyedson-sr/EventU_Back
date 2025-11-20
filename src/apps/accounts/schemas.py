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
            400: OpenApiResponse(description="Dados inválidos"),
            500: OpenApiResponse(description="Erro interno do servidor"),
        }
    ),
    activate_account=extend_schema(
        summary="Ativa a conta de um usuário",
        description="Registra o campo is_active como True",
        tags=["auth"],
        responses={
            200: AuthResponseSerializer,
            400: OpenApiResponse(description="Código inválido ou conta já ativa"),
            404: OpenApiResponse(description="Usuário não encontrado"),
        }
    ),
    login=extend_schema(
        summary="Autentica o usuário",
        description="Realiza o login do usuário e fornece o token para salvar",
        tags=["auth"],
        responses={
            200: AuthResponseSerializer,
            401: OpenApiResponse(description="Credenciais inválidas"),
        }
    ),
    forgot_password=extend_schema(
        summary="Solicita código para redefinição de senha",
        description="Recebe um pedido de reset de senha e envia código para o email do usuário",
        tags=["auth"],
        responses={
            200: MessageResponseSerializer,
            400: OpenApiResponse(description="Erro ao solicitar reset de senha."),
        }
    ),
    reset_password=extend_schema(
        summary="Solicita código para redefinição de senha",
        description="Recebe um pedido de reset de senha e envia código para o email do usuário",
        tags=["auth"],
        responses={
            200: MessageResponseSerializer,
            400: OpenApiResponse(description="Erro ao processar reset de senha."),
        }
    ),
)
