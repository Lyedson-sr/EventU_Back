from rest_framework.serializers import ModelSerializer, ValidationError, CharField
from .models import Event, EventOccurrences
from .enums import EventType


class EventCreateSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id",
            "group",
            "title",
            "description",
            "location",
            "event_type",
            "start_datetime",
            "end_datetime",
            "recurrence_rrule",
            "recurrence_exceptions",
            "color",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        event_type = attrs.get("event_type")
        group = attrs.get("group")
        user = self.context["request"].user

        if event_type == EventType.PERSONAL and group:
            raise ValidationError(
                {"detail": "Eventos pessoais não devem ter grupo associado."}
            )

        if event_type == EventType.GROUP and not group:
            raise ValidationError(
                {"detail": "Eventos de grupo devem ter um grupo associado."}
            )

        if event_type == EventType.INSTITUTIONAL and group:
            raise ValidationError(
                {"detail": "Eventos institucionais não devem ter grupo associado."}
            )

        if event_type == EventType.INSTITUTIONAL and not user.is_staff:
            raise ValidationError(
                {
                    "detail": "Apenas administradores podem criar eventos institucionais."
                }
            )
        
        if event_type == EventType.GROUP and group:
            if not group.group_members.filter(user=user).exists():
                raise ValidationError({"detail": "Você não é membro deste grupo."})

        return attrs


class EventRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id",
            "creator",
            "group",
            "title",
            "description",
            "location",
            "event_type",
            "start_datetime",
            "end_datetime",
            "recurrence_rrule",
            "recurrence_exceptions",
            "color",
            "created_at",
        ]


class EventPatchSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "location",
            "event_type",
            "start_datetime",
            "end_datetime",
            "recurrence_rrule",
            "recurrence_exceptions",
            "color",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        event_type = attrs.get("event_type")
        group = attrs.get("group")

        if event_type and group:
            if event_type == EventType.PERSONAL and group:
                raise ValidationError(
                    {"group": "Eventos pessoais não devem ter grupo associado."}
                )

            if event_type == EventType.INSTITUTIONAL and group:
                raise ValidationError(
                    {"group": "Eventos institucionais não devem ter grupo associado."}
                )

        return attrs


class EventListSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id",
            "creator",
            "group",
            "title",
            "event_type",
            "start_datetime",
            "end_datetime",
            "color",
            "created_at",
        ]


class EventOccurrencesSerializer(ModelSerializer):
    event_title = CharField(source='event.title', read_only=True)
    event_description = CharField(source='event.description', read_only=True)
    event_location = CharField(source='event.location', read_only=True)
    event_type = CharField(source='event.event_type', read_only=True)
    event_color = CharField(source='event.color', read_only=True)
    creator_name = CharField(source='event.creator.name', read_only=True)
    
    class Meta:
        model = EventOccurrences
        fields = [
            'id',
            'event_title',
            'event_description', 
            'event_location',
            'event_type',
            'event_color',
            'creator_name',
            'occurrence_start',
            'occurrence_end',
            'cancelled',
            'created_at',
            'updated_at'
        ]
