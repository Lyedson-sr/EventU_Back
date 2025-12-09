from dateutil.rrule import rrulestr
from django.utils import timezone
from django.db import transaction


class RecurrenceService:

    @staticmethod
    def generate_occurrences(event_id):
        # OBS: tive q botar aqui por causa de circular import
        from ..models import Event, EventOccurrences

        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            return

        if not event.recurrence_rrule:
            EventOccurrences.objects.create(
                event=event,
                occurrence_start=event.start_datetime,
                occurrence_end=event.end_datetime
            )
            return

        try:
            rrule = rrulestr(event.recurrence_rrule, dtstart=event.start_datetime)
        except Exception:
            return

        exceptions = event.recurrence_exceptions or {}
        exception_dates = exceptions.get("dates", [])

        duration = event.end_datetime - event.start_datetime

        MAX_OCCURRENCES = 500
        occurrences_to_create = []
        count = 0

        for occurrence_date in rrule:
            if count >= MAX_OCCURRENCES:
                break

            if timezone.is_naive(occurrence_date):
                occurrence_date = timezone.make_aware(occurrence_date)

            if occurrence_date.date().isoformat() in exception_dates:
                continue

            occurrences_to_create.append(
                EventOccurrences(
                    event=event,
                    occurrence_start=occurrence_date,
                    occurrence_end=occurrence_date + duration
                )
            )

            count += 1

        with transaction.atomic():
            EventOccurrences.objects.bulk_create(
                occurrences_to_create,
                batch_size=100 
            )

    @staticmethod
    def update_occurrences(event_id):
        from ..models import Event, EventOccurrences

        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            return

        EventOccurrences.objects.filter(event=event).delete()
        RecurrenceService.generate_occurrences(event.id)
