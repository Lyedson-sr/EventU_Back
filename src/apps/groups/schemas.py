from drf_spectacular.utils import extend_schema, extend_schema_view


group_schemas = extend_schema_view(
    list=extend_schema(
        summary="Lista todos os grupos dos quais o usuário participa",
        description="Lista todos os grupos que o usuário é o criador ou membro comum",
    ),
    create=extend_schema(
        summary="Cria um grupo",
        description="Cria um grupo e coloca o usuário logado como creator",
    ),
    retrieve=extend_schema(
        summary="Lista os dados de um grupo específico",
        description="Lista os dados do grupo especificado pelo ID (apenas grupos que o usuário é membro)",
    ),
    partial_update=extend_schema(
        summary="Atualiza os dados de um grupo específico",
        description="Atualiza os dados do grupo especificado pelo ID (apenas o dono do grupo pode fazer isso)"
    ),
    destroy=extend_schema(
        summary="Deleta um grupo específico",
        description="Deleta o grupo especificado pelo ID (apenas o criador do grupo pode fazer isso)"
    )
)