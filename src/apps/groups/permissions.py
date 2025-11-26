from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Group, GroupMember


class IsGroupCreatorOrReadOnly(BasePermission):
    """
    Permite que apenas o criador do grupo edite ou delete.
    Outros membros podem apenas visualizar.
    """
    def has_object_permission(self, request, view, obj):
        # GET permitido pra todos
        if request.method in SAFE_METHODS:
            return True
        
        # Acesso total pra superusers e staff
        if request.user.is_staff:
            return True

        # Apenas o criador pode editar ou deletar
        return obj.creator == request.user


class IsGroupOwnerToAddMembers(BasePermission):
    """
    Dono pode adicionar/remover membros, membros podem apenas ver.
    """
    def has_permission(self, request, view):
        group = get_object_or_404(Group, id=view.kwargs.get("group_pk"))

        is_member = GroupMember.objects.filter(
            group=group, user=request.user
        ).exists()

        if request.method in SAFE_METHODS:
            return is_member or group.creator == request.user

        return group.creator == request.user
        
    def has_object_permission(self, request, view, obj):
        # GET pra qualquer membro
        if request.method in SAFE_METHODS:
            return GroupMember.objects.filter(group=obj.group, user=request.user).exists()
        
        # DELETE apenas para o criador
        return obj.group.creator == request.user
