from rest_framework.permissions import DjangoModelPermissions


class IsAdmin(DjangoModelPermissions):
    """
    Permissão customizada que garante acesso se o usuário for admin.
    """
    def has_permission(self, request, view):
        if request.user.role == "admin" and request.user.is_superuser:
            return True
        

class IsAdminOrHasPermission(DjangoModelPermissions):
    ...
