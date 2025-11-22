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
        description="Atualiza os dados do grupo especificado pelo ID (apenas o dono do grupo pode fazer isso)",
    ),
    destroy=extend_schema(
        summary="Deleta um grupo específico",
        description="Deleta o grupo especificado pelo ID (apenas o criador do grupo pode fazer isso)",
    )
)


group_members_schemas = extend_schema_view(
    list=extend_schema(
        summary="Lista todos os membros de um grupo",
        description="Lista todos os membros do grupo especificado pelo ID (apenas membros e criadores conseguem fazer isso)",
    ),
    create=extend_schema(
        summary="Adiciona um membro a um grupo",
        description="Adiciona um membro (pelo email dele) a um grupo especificado pelo ID",
    ),
    destroy=extend_schema(
        summary="Deleta um membro de um grupo",
        description="Deleta um membro (pelo id do group_member) de um grupo especificado pelo ID",
    ),
)
