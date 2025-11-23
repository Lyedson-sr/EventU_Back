from django.db.models import Q
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Event
from .permissions import CanCreateEventType, CanViewEvent, IsEventCreatorOrAdmin
from .enums import EventType
from .serializers import (
    EventRetrieveSerializer,
    EventPatchSerializer,
    EventCreateSerializer,
    EventListSerializer,
)


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
