from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer, UserPatchSerializer, UserRetrieveSerializer
from .schemas import user_admin_actions_schema, user_actions_schema
from utils.permissions import IsAdmin


# Pra Admins
@user_admin_actions_schema
class UserAdminViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    http_method_names = ["get", "patch"]

    def get_serializer_class(self):
        if self.action == "partial_update":
            return UserPatchSerializer
        elif self.action == "retrieve":
            return UserRetrieveSerializer
        return UserSerializer
    

# Pra users autenticados
@user_actions_schema
class UserViewSet(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return UserPatchSerializer
        return UserRetrieveSerializer
    
    def get(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    def patch(self, request):
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200)
