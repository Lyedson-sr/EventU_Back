from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
)
from .serializers import (
    RegisterResponseSerializer,
    AuthResponseSerializer,
)
from utils.serializers import MessageResponseSerializer


register_schema = extend_schema_view(
    post=extend_schema(
        summary="Registra um usuário no sistema",
        description="Registra um usuário e gera os tokens de autenticação JWT",
        responses={
            201: RegisterResponseSerializer,
        },
    )
)


activate_account_schema = extend_schema_view(
    post=extend_schema(
        summary="Ativa a conta de um usuário",
        description="Marca o campo is_active como True para tornar a conta do usuário ativa",
        responses={
            200: AuthResponseSerializer,
        },
    )
)


forgot_password_schema = extend_schema_view(
    post=extend_schema(
        summary="Envia email de reset de senha para o usuário",
        description="Recebe o email do usuário e envia um código para ele por email",
        responses={
            200: MessageResponseSerializer,
        },
    )
)


# reset_password_schema = extend_schema_view(
#     post=extend_schema(
#         summary="Recebe "
#     )
# )


login_schema = extend_schema_view(
    post=extend_schema(
        summary="Autentica o usuário no sistema",
        description="Faz a autenticação do usuário e devolve os tokens",
        responses={
            200: AuthResponseSerializer,
        },
    )
)


logout_schema = extend_schema_view(
    post=extend_schema(
        summary="Faz o logout seguro do usuário no sistema",
        description="Realiza o logout do usuário colocando o token na blacklist",
        responses={
            200: MessageResponseSerializer,
        },
    )
)
