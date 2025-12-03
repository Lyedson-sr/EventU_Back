from rest_framework.serializers import ModelSerializer, ValidationError, CharField
from .models import Event, EventOccurrences, EventGuest
from .enums import EventType
from .services.guest_invitation_service import GuestInvitationService


class EventCreateSerializer(ModelSerializer):
    guest_emails = CharField(write_only=True, required=False)

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
            "guest_emails",
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
    
    def create(self, validated_data):
        guest_emails = validated_data.pop("guest_emails", "")

        event = Event.objects.create(**validated_data)

        if guest_emails:
            emails = [email.strip() for email in guest_emails.split(",") if email.strip()]

            for email in emails:
                EventGuest.objects.create(event=event, email=email)

        return event


class EventGuestSerializer(ModelSerializer):
    class Meta:
        model = EventGuest
        fields = [
            "id",
            "email",
            "invitation_sent",
        ]


class EventRetrieveSerializer(ModelSerializer):
    guests = EventGuestSerializer(many=True, read_only=True)

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
            "guests",
        ]


class EventPatchSerializer(ModelSerializer):
    guest_emails = CharField(required=False, write_only=True)

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
            "guest_emails",
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
    
    def update(self, instance, validated_data):
        guest_emails = validated_data.pop("guest_emails", None)

        instance = super().update(instance, validated_data)

        if guest_emails is not None:
            added = self.sync_guests(instance, guest_emails)

            if added:
                GuestInvitationService.send_invitations_async(instance)

        return instance

    def sync_guests(self, event, guest_emails_raw):
        emails = {
            email.strip()
            for email in guest_emails_raw.split(",")
            if email.strip()
        }

        # Convidados atuais no banco
        existing = set(event.guests.values_list("email", flat=True))

        # Emails para adicionar
        to_add = emails - existing

        # Emails para remover
        to_remove = existing - emails

        # Remover convidados
        event.guests.filter(email__in=to_remove).delete()

        # Adicionar convidados novos
        for email in to_add:
            EventGuest.objects.create(event=event, email=email)

        return to_add


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
