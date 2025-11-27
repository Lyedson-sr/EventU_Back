from django.db.models import (
    Model,
    CharField,
    TextField,
    ForeignKey,
    DateTimeField,
    JSONField,
    BooleanField,
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
    title = CharField(max_length=40, null=False, blank=False)
    description = TextField(blank=True)
    location = CharField(max_length=40, blank=True)
    event_type = CharField(_("event type"), max_length=15, choices=EventType.choices, default=EventType.PERSONAL)
    start_datetime = DateTimeField(null=False, blank=False)
    end_datetime = DateTimeField(null=False, blank=False)
    recurrence_rrule = CharField(max_length=255, blank=True, null=True)
    recurrence_exceptions = JSONField(blank=True, null=True, default=dict)
    color = CharField(null=False, blank=False, max_length=7, default="#3b82f6")
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        db_table = "events"

    def clean(self):
        if self.start_datetime >= self.end_datetime:
            raise ValidationError({
                "detail": "A data de término deve ser após a data de início."
            })
        
        if self.group.creator != self.creator:
            raise ValidationError({
                "detail": "Apenas o criador do grupo pode criar eventos."
            })
