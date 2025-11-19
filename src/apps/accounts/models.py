from django.db.models import (
    EmailField,
    CharField,
    BooleanField,
    TextChoices,
    DateTimeField,
)
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager


class CustomUser(AbstractBaseUser):
    class Role(TextChoices):
        STUDENT = "student", _("Aluno")
        PROFESSOR = "professor", _("Professor")
        ADMIN = "admin", _("Administrador")

    class CalendarView(TextChoices):
        DAY = "day", _("Dia")
        WEEK = "week", _("Semana")
        MONTH = "month", _("Mês")
        YEAR = "year", _("Ano")

    email = EmailField(_("email"), unique=True)
    name = CharField(_("name"), max_length=150, null=False, blank=False)
    role = CharField(_("role"), max_length=20, choices=Role.choices, default=Role.STUDENT)
    preferred_calendar_view = CharField(_("preferred calendar view"), max_length=10, choices=CalendarView.choices, default=CalendarView.MONTH)
    is_active = BooleanField(_("is active"), default=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = CustomUserManager()

    class Meta:
        db_table = "users"
