from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    """
    Model de User customizado, para autenticar com email no lugar de username.
    """
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError(_("O Email tem que ser fornecido"))
        if not name:
            raise ValueError(_("O nome deve ser fornecido"))

        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", False)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, name, password, **extra_fields):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", "admin")

        if extra_fields.get("role") != "admin":
            raise ValueError("Superuser deve ter role='admin'")

        return self.create_user(email, name, password, **extra_fields)

