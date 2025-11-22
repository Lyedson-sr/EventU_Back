from django.db.models import Q
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Group, GroupMember
from .serializers import (
    GroupRetrieveSerializer,
    GroupPatchSerializer,
    GroupCreateSerializer,
    GroupMemberCreateSerializer,
    GroupMemberListSerializer,
)
from .permissions import IsGroupCreatorOrReadOnly, IsGroupOwnerToAddMembers
from .schemas import group_schemas


@group_schemas
class GroupViewSet(ModelViewSet):
    queryset = Group.objects.all().order_by("-id")
    permission_classes = [IsAuthenticated, IsGroupCreatorOrReadOnly]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GroupRetrieveSerializer
        elif self.action == "partial_update":
            return GroupPatchSerializer
        elif self.action == "create":
            return GroupCreateSerializer
        return GroupRetrieveSerializer

    def get_queryset(self):
        # Pega o user logado
        user = self.request.user

        # Filtra grupos que o user é criador ou membro
        return Group.objects.filter(
            Q(creator=user) | Q(group_members__user=user)
        ).distinct()

    def perform_create(self, serializer):
        # Define o criador como o user logado
        serializer.save(creator=self.request.user)


class GroupMemberViewSet(ModelViewSet):
    queryset = GroupMember.objects.all().order_by("-id")
    permission_classes = [IsAuthenticated, IsGroupOwnerToAddMembers]
    http_method_names = ["get", "post", "delete"]

    def get_serializer_class(self):
        if self.action == "create":
            return GroupMemberCreateSerializer
        return GroupMemberListSerializer

    def get_queryset(self):
        # Filtra apenas membros do grupo especifico
        group_pk = self.kwargs.get("group_pk")
        return GroupMember.objects.filter(group_id=group_pk).select_related("user")

    def perform_create(self, serializer):
        # Define o grupo automaticamente pela URL
        group_pk = self.kwargs.get("group_pk")
        group = Group.objects.get(id=group_pk)
        serializer.save(group=group)
    
