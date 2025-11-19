from drf_spectacular.utils import extend_schema_view, extend_schema


auth_schema = extend_schema_view(
    register=extend_schema(
        summary="Registra um usuário no sistema",
        description="Registra um usuário e gera os tokens de autenticação",
    )
)