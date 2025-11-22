from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsGroupCreatorOrReadOnly(BasePermission):
    """
    Permite que apenas o criador do grupo edite ou delete.
    Outros membros podem apenas visualizar.
    """
    def has_object_permission(self, request, view, obj):
        # GET permitido pra todos
        if request.method in SAFE_METHODS:
            return True
        
        # Apenas o criador pode editar ou deletar
        return obj.creator == request.user
    