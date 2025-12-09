from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.exceptions import NotFound
from apps.users.enums import Role
from .enums import EventType


class CanCreateEventType(BasePermission):
    """
    Controla quem pode criar cada tipo de evento.
    """

    def has_permission(self, request, view):
        if request.method != "POST":
            return True

        event_type = request.data.get("event_type")

        # Admin pode criar qualquer tipo de evento
        if request.user.role == Role.ADMIN and request.user.is_staff:
            return True

        # Users comuns podem criar evento do tipo "Pessoal" e "Grupo"
        if event_type in [EventType.PERSONAL, EventType.GROUP]:
            return True

        # Users comuns não podem criar evento do tipo "Institucional"
        if event_type == EventType.INSTITUTIONAL:
            return False

        return True


class CanViewEvent(BasePermission):
    """
    User só pode ver eventos que criou, que participa ou institucionais
    """

    def has_object_permission(self, request, view, obj):
        if obj.event_type == EventType.INSTITUTIONAL:
            return True

        if obj.creator == request.user:
            return True

        if (
            obj.event_type == EventType.GROUP
            and obj.group.group_members.filter(user=request.user).exists()
        ):
            return True

        return NotFound("Evento não encontrado.")
    

class IsEventCreatorOrAdmin(BasePermission):
    """
    Apenas creator ou admin pode editar/deletar
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        
        if obj.creator == request.user:
            return True
        
        raise NotFound("Evento não encontrado.")
