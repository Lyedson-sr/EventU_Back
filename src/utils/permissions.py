from rest_framework.permissions import DjangoModelPermissions
from apps.users.enums import Role


class IsAdmin(DjangoModelPermissions):
    """
    Permissão customizada que garante acesso se o usuário for admin.
    """
    def has_permission(self, request, view):
        if request.user.role == Role.ADMIN and request.user.is_staff:
            return True
        

class IsAdminOrHasPermission(DjangoModelPermissions):
    ...
