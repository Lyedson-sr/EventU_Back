from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Model de User customizado, para autenticar com email no lugar de username.
    """
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("O Email tem que ser fornecido"))
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", False)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Cria e salva um superuser com o email e senha dados.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("O superuser deve ter is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser deve ter is_superuser=True"))
        return self.create_user(email, password, **extra_fields)
