from rest_framework import permissions

from .models import Profile


class IsProfileOwner(permissions.BasePermission):
    """
    Permission that checks that the user who made the request is the same as the user that is trying to
    be modified
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_superuser: #superusers can modify anyone
            return True
        return (obj.id == request.user.id)

class IsRealAuthor(permissions.BasePermission):
    """
    Permission that checks that the user who made the request is the real author of the comment
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == 'POST':
            try:
                author_id = int(request.data['author_id'])
            except:
                return False
            return (request.user.id == author_id) #using int() bc it's json string.


class IsSuperUser(permissions.BasePermission):
    """
       Permission that checks that the user who made the request that involves changing administrative permissions
       is indeed a superuser.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if ('is_superuser') in request.data or ('is_staff') in request.data:
            return (request.user.is_superuser)

        return True

class AnonTriesToSuperUser(permissions.BasePermission):
    """
    Permission that checks if an anonymous user is trying to create a superuser account
    """

    def has_permission(self, request, view):
        if ('is_superuser') in request.data or ('is_staff') in request.data:
            return False
        return True