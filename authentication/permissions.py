from rest_framework.permissions import BasePermission
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from forum.positions import Founder, Employee, Representative

def check_errors(func):
    def wrapper(self, request, view):
        error = request.user.error
        if error:
            if error.status == status.HTTP_403_FORBIDDEN:
                raise PermissionDenied(detail=error.msg)
            if error.status == status.HTTP_401_UNAUTHORIZED:
                raise NotAuthenticated(detail=error.msg)
        return func(self, request, view)

    return wrapper


class PositionPermission(BasePermission):
    position_model = None
    @check_errors
    def has_permission(self, request, view):
        return request.user.position == self.position_model.position
            
class IsFounder(PositionPermission):
    position_model = Founder
        
class IsEmployee(PositionPermission):
    position_model = Employee

class IsRepresentative(PositionPermission):
    position_model = Representative

class IsNotAuthenticated(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return False
        return True

class IsVerified(BasePermission):
    @check_errors
    def has_permission(self, request, view):
        super().has_permission(request, view)
        if not request.user.is_verified:
            return False
        return True

class IsAuthenticated(BasePermission):
    @check_errors
    def has_permission(self, request, view):
        super().has_permission(request, view)
        return request.user.is_authenticated

class IsInvestor(BasePermission):
    @check_errors
    def has_permission(self, request, view):
        super().has_permission(request, view)
        if request.user.is_startup == False:
            return True
        return False

class IsStartup(BasePermission):
    @check_errors
    def has_permission(self, request, view):
        super().has_permission(request, view)
        if request.user.is_startup == True:
            return True
        return False

class IsRelatedToCompany(BasePermission):
    @check_errors
    def has_permission(self, request, view):
        super().has_permission(request, view)
        if request.user.company_id:
            return True
        return False


class CustomUserUpdatePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj
