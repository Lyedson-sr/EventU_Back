from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


event_schema = extend_schema_view(
    list=extend_schema(
        summary="Lista os eventos do usuário autenticado",
        description="Lista os eventos que o usuário autenticado é criador, participante ou eventos institucionais",
    ),
    retrieve=extend_schema(
        summary="Recupera os detalhes de um evento específico",
        description="Recupera os detalhes completos de um evento específico pelo seu ID",
    ),
    create=extend_schema(
        summary="Cria um novo evento",
        description="Cria um novo evento com os dados fornecidos pelo usuário autenticado",
    ),
    partial_update=extend_schema(
        summary="Atualiza parcialmente um evento existente",
        description="Atualiza parcialmente os dados de um evento existente pelo seu ID",
    ),
    destroy=extend_schema(
        summary="Exclui um evento",
        description="Exclui um evento existente pelo seu ID",
    ),
)


event_occurrences_schema = extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="start",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="Data inicial no formato YYYY-MM-DD (obrigatório).",
                required=True,
            ),
            OpenApiParameter(
                name="end",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="Data final no formato YYYY-MM-DD (obrigatório).",
                required=True,
            ),
        ],
        summary="Listar ocorrências de eventos",
        description=(
            "Retorna todas as ocorrências de eventos entre as datas informadas "
            "(intervalo obrigatório: start e end)."
        ),
    ),
    retrieve=extend_schema(
        summary="Recupera os detalhes de uma ocorrência de evento específica",
        description="Recupera os detalhes completos de uma ocorrência de evento específica pelo seu ID",
    ),
)
