from rest_framework.exceptions import APIException


class InvalidCredentials(APIException):
    status_code = 401
    default_detail = "Credenciais inválidas."
    default_code = "authorization"
    