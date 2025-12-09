from apps.users.models import User
from rest_framework.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError


def validate_unique_email(value: str) -> str:
    if User.objects.filter(email=value).exists():
        raise ValidationError(detail="Email inválido.", code="invalid")
    return value

def is_valid_email(email: str) -> bool:
    try:
        validate_email(email)
        return True
    except DjangoValidationError:
        return False
