from django.db.models import Q
from django.utils import timezone
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Event, EventOccurrences
from .permissions import CanCreateEventType, CanViewEvent, IsEventCreatorOrAdmin
from .enums import EventType
from .serializers import (
    EventRetrieveSerializer,
    EventPatchSerializer,
    EventCreateSerializer,
    EventListSerializer,
    EventOccurrencesSerializer,
)
from datetime import datetime


class EventsViewSet(ModelViewSet):
    queryset = Event.objects.all().order_by("-id")
    permission_classes = [
        IsAuthenticated,
        CanCreateEventType,
        CanViewEvent,
        IsEventCreatorOrAdmin,
    ]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return EventRetrieveSerializer
        elif self.action == "partial_update":
            return EventPatchSerializer
        elif self.action == "create":
            return EventCreateSerializer
        else:
            return EventListSerializer

    def get_queryset(self):
        user = self.request.user

        return (
            Event.objects.filter(
                Q(creator=user)
                | Q(group__group_members__user=user)
                | Q(event_type=EventType.INSTITUTIONAL)
            )
            .distinct()
            .order_by("-start_datetime")
        )

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class EventOccurrencesViewSet(ModelViewSet):
    queryset = EventOccurrences.objects.all().order_by("-id")
    permission_classes = [IsAuthenticated, CanViewEvent]
    http_method_names = ["get"]
    serializer_class = EventOccurrencesSerializer

    def list(self, request):
        start_date = request.query_params.get("start")
        end_date = request.query_params.get("end")

        if not start_date or not end_date:
            return Response(
                {
                    "detail": "Os parâmetros 'start' e 'end' são obrigatórios no formato YYYY-MM-DD."
                },
                status=400,
            )

        try:
            start_datetime = timezone.make_aware(
                datetime.strptime(start_date, "%Y-%m-%d")
            )
            end_datetime = timezone.make_aware(datetime.strptime(end_date, "%Y-%m-%d"))
            # Ajusta o end_datetime para o final do dia
            end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
        except ValueError:
            return Response(
                {"detail": "Formato de data inválido. Use YYYY-MM-DD."}, status=400
            )

        if start_datetime >= end_datetime:
            return Response(
                {"detail": "A data de início deve ser anterior à data de término."},
                status=400,
            )

        user = request.user

        accessible_events = Event.objects.filter(
            Q(creator=user)
            | Q(group__group_members__user=user)
            | Q(event_type=EventType.INSTITUTIONAL)
        ).distinct()

        occurrences = (
            EventOccurrences.objects.filter(
                event__in=accessible_events,
                occurrence_start__gte=start_datetime,
                occurrence_end__lte=end_datetime,
                cancelled=False,
            )
            .select_related("event")
            .order_by("occurrence_start")
        )

        serializer = self.get_serializer(occurrences, many=True)
        return Response(serializer.data, status=200)
