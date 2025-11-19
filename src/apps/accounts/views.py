from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import UserRegistrationSerializer, UserSerializer
from .schemas import auth_schema


@auth_schema
class AuthViewSet(ModelViewSet):
    queryset = CustomUser.objects.none()
    permission_classes = [AllowAny]
    http_method_names = ["post"]

    def get_serializer_class(self):
        if self.action == "register":
            return UserRegistrationSerializer
        return UserSerializer

    
    @action(detail=False, methods=["post"])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        return Response({
            "data": UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)
        
