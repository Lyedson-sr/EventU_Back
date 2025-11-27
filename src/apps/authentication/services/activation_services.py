import random
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from apps.users.models import User


class ActivationService:
    @staticmethod
    def generate_activation_code(user: User) -> str:
        """
        Gera código de 6 dígitos e salva no cache por 1h
        """
        code = str(random.randint(1000, 9999))
        cache_key = f"activation_code_{user.id}"
        cache.set(cache_key, code, timeout=3600)
        return code
    
    @staticmethod
    def verify_activation_code(user_id: int, code: str) -> bool:
        """
        Verifica se o código está correto
        """
        cache_key = f"activation_code_{user_id}"
        stored_code = cache.get(cache_key)

        if stored_code and stored_code == code:
            cache.delete(cache_key) # Remove o codigo usado
            return True
        return False
    
    @staticmethod
    def send_activation_email(user: User, code: str) -> None:
        """
        Envia email com código de ativação
        """
        subject = "Ative sua conta no EventU"
        message = f"""
        Olá {user.name}!

        Seu código de ativação é: {code}

        Use este código para ativar sua conta no EventU.

        O código expira em 1 hora.

        Atenciosamente,
        Equipe EventU
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
