from rest_framework import permissions


class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user 
            and request.user.is_authenticated 
            and (request.user.is_teacher or request.user.user_type == 'TEACHER')
        )


class IsParent(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user 
            and request.user.is_authenticated 
            and (request.user.is_parent or request.user.user_type == 'PARENT')
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        user_attr = getattr(obj, 'user', obj)
        return user_attr == request.user