from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class Role(TextChoices):
    STUDENT = "student", _("Aluno")
    PROFESSOR = "professor", _("Professor")
    ADMIN = "admin", _("Administrador")

class CalendarView(TextChoices):
    DAY = "day", _("Dia")
    WEEK = "week", _("Semana")
    MONTH = "month", _("Mês")
    YEAR = "year", _("Ano")