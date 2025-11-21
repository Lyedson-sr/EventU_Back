from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer, UserPatchSerializer, UserRetrieveSerializer
from utils.permissions import IsAdmin


# Pra Admins
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
