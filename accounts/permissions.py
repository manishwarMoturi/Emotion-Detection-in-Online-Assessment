from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'

class IsTestTaker(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'test_taker'

class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'student'

class IsSelfOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.role == 'admin'

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.role == 'admin'

class IsTestTakerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.role == 'test_taker' or request.user.role == 'admin'
        ) 