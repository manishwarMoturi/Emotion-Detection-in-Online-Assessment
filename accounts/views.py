from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserUpdateSerializer, ChangePasswordSerializer
from .permissions import IsAdminUser, IsSelfOrAdmin

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

class UserListView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAdminUser,)
    serializer_class = UserSerializer
    
    def get_queryset(self):
        queryset = User.objects.all()
        role = self.request.query_params.get('role', None)
        if role is not None:
            queryset = queryset.filter(role=role)
        return queryset

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    permission_classes = (IsSelfOrAdmin,)
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer

class ChangePasswordView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (IsSelfOrAdmin,)
    serializer_class = ChangePasswordSerializer
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"old_password": ["Wrong password."]}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Password updated successfully"}, 
                          status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            user = User.objects.get(username=request.data['username'])
            response.data['user'] = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
            
        return response

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_object(self):
        return self.request.user 