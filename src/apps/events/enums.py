from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class EventType(TextChoices):
    PERSONAL = "personal", _("Pessoal")
    GROUP = "group", _("Grupo")
    INSTITUTIONAL = "institutional", _("Institucional")
    