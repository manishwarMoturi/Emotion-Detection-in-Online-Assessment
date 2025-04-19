from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, UserListView, UserDetailView,
    ChangePasswordView, CustomTokenObtainPairView,
    ProfileView
)

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User management
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<int:pk>/change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # Profile
    path('profile/', ProfileView.as_view(), name='profile'),
] 