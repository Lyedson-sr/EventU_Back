from drf_spectacular.utils import extend_schema, extend_schema_view
from .serializers import UserSerializer, UserRetrieveSerializer, UserPatchSerializer


user_admin_actions_schema = extend_schema_view(
    list=extend_schema(
        summary="(ADMIN) Lista todos os usuários",
        description="Lista todos os usuários cadastrados",
        responses={
            200: UserSerializer,
        },
    ),
    retrieve=extend_schema(
        summary="(ADMIN) Lista os dados de um usuário específico",
        description="Lista os dados de um usuário específico pelo ID",
        responses={
            200: UserRetrieveSerializer,
        },
    ),
    partial_update=extend_schema(
        summary="(ADMIN) Atualiza os dados de um usuário",
        description="Atualiza os dados de um usuário específico pelo ID",
        responses={
            200: UserPatchSerializer
        },
    ),
)


user_actions_schema = extend_schema_view(
    get=extend_schema(
        summary="Lista os dados do usuário autenticado",
        description="Retorna os dados do usuário autenticado",
        responses={
            200: UserRetrieveSerializer,
        }
    ),
    patch=extend_schema(
        summary="Atualiza os dados do usuário autenticado",
        description="Atualiza os dados solicitados do usuário autenticado",
        responses={
            200: UserPatchSerializer,
        }
    ),
)
