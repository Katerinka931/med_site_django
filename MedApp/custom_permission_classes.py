from rest_framework import permissions


class IsDoctorOrChief(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and (request.user.role == 3 or request.user.role == 2))


class IsChief(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == 2)


class IsNotAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.role != 1)


class IsAdminOrChief(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and (request.user.role == 1 or request.user.role == 2))


# if request.method in permissions.SAFE_METHODS: - это отдельное для метода GET если его можно, а метод post нельзя
