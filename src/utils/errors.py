from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException, ErrorDetail, ValidationError


class UniqueValidationError(ValidationError):
    """
    Erro customizado para lidar com erros de validação para campos que devem ser únicos.
    Herda de ValidationError do DRF.
    """
    def __init__(self, message, code="unique"):
        super().__init__({"non_field_errors": [ErrorDetail(message, code)]})


class GenericError(APIException):
    """
    Erro genérico para dar raise em exceptions com status code, messages e error codes customizados.
    Herda de APIException do DRF.
    """
    def __init__(self, status_code: status, detail: str, code: str):
        super().__init__(detail=_(detail), code=code)
        self.status_code = status_code
