from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from apps.users.models import User
import random


class PasswordResetService:
    CODE_TTL = 600 # 10 min

    @staticmethod
    def generate_reset_code(user_id: int) -> str:
        code = str(random.randint(1000, 9999))
        cache.set(f"password_reset_{user_id}", code, timeout=PasswordResetService.CODE_TTL)
        return code
    
    
    @staticmethod
    def send_reset_email(user: User) -> None:
        code = PasswordResetService.generate_reset_code(user.id)
        send_mail(
            subject="Código de redefinição de senha",
            message=f"Seu código para redefinir a senha é: {code}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )


    @staticmethod
    def verify_code(email: str, code: str) -> bool:
        """Verifica se o código é válido para o email"""
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return False
        
        cached_code = cache.get(f"password_reset_{user.id}")
        return cached_code == code

    
    @staticmethod
    def reset_password(email: str, code: str, new_password: str) -> User:
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValueError("Email ou código inválido")
        
        cached_code = cache.get(f"password_reset_{user.id}")
        if cached_code != code:
            raise ValueError("Email ou código inválido")
        
        user.set_password(new_password)
        user.save()
        cache.delete(f"password_reset_{user.id}") # tira do cache
        return user