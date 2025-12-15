from django.db.models import (
    Model,
    CharField,
    TextField,
    ForeignKey,
    DateTimeField,
    JSONField,
    BooleanField,
    EmailField,
    CASCADE,
)
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from apps.users.models import User
from apps.groups.models import Group
from .enums import EventType


class Event(Model):
    creator = ForeignKey(User, on_delete=CASCADE, related_name="created_events")
    group = ForeignKey(Group, on_delete=CASCADE, related_name="events", null=True, blank=True)

    title = CharField(max_length=80)
    description = TextField(blank=True)
    location = CharField(max_length=40, null=True, blank=True)

    event_type = CharField(
        _("event type"),
        max_length=15,
        choices=EventType.choices,
        default=EventType.PERSONAL,
    )

    start_datetime = DateTimeField()
    end_datetime = DateTimeField()

    recurrence_rrule = CharField(max_length=255, blank=True, null=True)
    recurrence_exceptions = JSONField(blank=True, null=True, default=dict)

    color = CharField(max_length=7, default="#3b82f6")

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        db_table = "events"

    def clean(self):
        if self.start_datetime >= self.end_datetime:
            raise ValidationError({"detail": "A data de término deve ser após a inicial."})

        if self.group and self.group.creator != self.creator:
            raise ValidationError({"detail": "Somente o dono do grupo pode criar eventos."})

    def __str__(self):
        return f"Event(id={self.id}, title={self.title})"


class EventOccurrences(Model):
    event = ForeignKey(Event, on_delete=CASCADE, related_name="occurrences")

    occurrence_start = DateTimeField()
    occurrence_end = DateTimeField()

    cancelled = BooleanField(default=False)

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        db_table = "event_occurrences"
        ordering = ["occurrence_start"]

    def __str__(self):
        return f"{self.event.title} - {self.occurrence_start}"


class EventGuest(Model):
    event = ForeignKey(Event, on_delete=CASCADE, related_name="guests")
    user = ForeignKey(User, on_delete=CASCADE, related_name="event_guests", blank=True, null=True)

    email = EmailField(_("email do convidado"), max_length=255)
    invitation_sent = BooleanField(default=False)
    invitation_sent_at = DateTimeField(null=True, blank=True)

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        db_table = "event_guests"
        unique_together = [["event", "email"]]

    def clean(self):
        if EventGuest.objects.filter(
            event=self.event,
            email=self.email
        ).exclude(id=self.id).exists():
            raise ValidationError({"detail": "Este e-mail já é convidado deste evento."})

    def __str__(self):
        return f"{self.email} - {self.event.title}"
