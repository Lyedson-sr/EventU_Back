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
from django.db.models.signals import post_save, pre_save
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from apps.users.models import User
from apps.groups.models import Group
from .enums import EventType
from .services.recurrence_services import RecurrenceService


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
        
        if self.group and self.group.creator != self.creator:
            raise ValidationError({
                "detail": "Apenas o criador do grupo pode criar eventos."
            })
        
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # se é um novo evento ou a RRULE foi modificada, gera ocorrências
        if is_new or self._state.adding:
            RecurrenceService.generate_occurrences(self)

    def __str__(self):
        return f"Event(id={self.id}, title={self.title}, creator={self.creator.email})"


@receiver(post_save, sender=Event)
def update_event_occurrences(sender, instance, **kwargs):
    if instance.pk and hasattr(instance, "_previous_recurrence_rrule"):
        if (instance.recurrence_rrule != instance._previous_recurrence_rrule or
            instance.start_datetime != getattr(instance, '_previous_start_datetime', None) or
            instance.end_datetime != getattr(instance, '_previous_end_datetime', None)):
            
            RecurrenceService.update_occurrences(instance)
        

@receiver(pre_save, sender=Event)
def store_previous_values(sender, instance, **kwargs):
    if instance.pk:
        try:
            previous = Event.objects.get(pk=instance.pk)
            instance._previous_recurrence_rrule = previous.recurrence_rrule
            instance._previous_start_datetime = previous.start_datetime
            instance._previous_end_datetime = previous.end_datetime
        except Event.DoesNotExist:
            pass


class EventOccurrences(Model):
    event = ForeignKey(Event, on_delete=CASCADE, related_name="occurrences")
    occurrence_start = DateTimeField(null=False, blank=False)
    occurrence_end = DateTimeField(null=False, blank=False)
    cancelled = BooleanField(null=False, blank=False, default=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        db_table = "event_occurrences"

    def __str__(self):
        return f"EventOccurrences(id={self.id}, event_id={self.event.id}, title={self.event.title}, occurrence_start={self.occurrence_start})"
    

class EventGuest(Model):
    event = ForeignKey(Event, on_delete=CASCADE, related_name="guests")
    user = ForeignKey(User, on_delete=CASCADE, related_name="event_guests", blank=True, null=True)
    email = EmailField(_("email do convidado"), max_length=255, blank=False, null=False)
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
            raise ValidationError({
                "detail": "Este e-mail já foi adicionado como convidado para este evento."
            })
        

    def __str__(self):
        return f"{self.name} <{self.email}> - {self.event.title}"
