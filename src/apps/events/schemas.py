from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


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
    )
)
