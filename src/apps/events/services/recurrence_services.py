from dateutil.rrule import rrulestr
from django.utils import timezone


class RecurrenceService:
    @staticmethod
    def generate_occurrences(event):
        # OBS: tive que botar aqui por conta de circular import
        from ..models import EventOccurrences

        # Se não tem regra de recorrência, cria apenas uma ocorrência
        if not event.recurrence_rrule:
            EventOccurrences.objects.create(
                event=event,
                occurrence_start=event.start_datetime,
                occurrence_end=event.end_datetime
            )
            return

        # Parse da RRULE
        try:
            rrule = rrulestr(
                event.recurrence_rrule,
                dtstart=event.start_datetime
            )
        except Exception as e:
            raise ValueError(f"RRULE inválida: {str(e)}")

        # Gera as ocorrências
        exceptions = event.recurrence_exceptions or {}
        exception_dates = exceptions.get('dates', [])

        for occurrence_date in rrule:
            # Converte para datetime aware se necessário
            if timezone.is_naive(occurrence_date):
                occurrence_date = timezone.make_aware(occurrence_date)

            # Calcula a duração do evento
            duration = event.end_datetime - event.start_datetime

            # Define start e end da ocorrência
            occurrence_start = occurrence_date
            occurrence_end = occurrence_start + duration

            # Verifica se essa data tá nas exceções
            occurrence_date_str = occurrence_date.date().isoformat()
            if occurrence_date_str in exception_dates:
                continue

            # Cria a ocorrência
            EventOccurrences.objects.create(
                event=event,
                occurrence_start=occurrence_start,
                occurrence_end=occurrence_end
            )

    @staticmethod
    def update_occurrences(event):
        # OBS: também tive que colocar aqui por causa de circular import
        from ..models import EventOccurrences

        # Deleta ocorrências existentes e gera novas
        EventOccurrences.objects.filter(event=event).delete()
        RecurrenceService.generate_occurrences(event)