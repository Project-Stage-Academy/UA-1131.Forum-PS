from rest_framework.permissions import BasePermission
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from forum.errors import Error



class PositionPermission(BasePermission):
    """
    This permission defines if user have the required position.
    If not, the response with corresponding status is returned.
    """
    position = None
    error = None
    def has_permission(self, request, view):
        if not request.user.position == self.position:
            raise PermissionDenied(detail=self.error.msg)
        return True
            
class IsFounder(PositionPermission):
    position = 'Founder'
    error = Error.NOT_FOUNDER
        
class IsRepresentative(PositionPermission):
    position = 'Representative'
    error = Error.NOT_REPRESENTATIVE


class IsVerified(BasePermission):
    """
    Checking if registered user was verified.

    """
    def has_permission(self, request, view):
        if not request.user.is_verified:
            raise PermissionDenied(detail=Error.USER_IS_NOT_VERIFIED.msg)
        return True

class IsAuthenticated(BasePermission):
    """
    Checking if user is authenticated.
    
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            raise NotAuthenticated(detail=Error.NOT_AUTHENTICATED.msg)
        return True


class IsRelatedToCompany(BasePermission):
    """
    Checking if user is currently related to company.

    """
    def has_permission(self, request, view):
        if not request.user.company:
            raise NotAuthenticated(detail=Error.NO_RELATED_TO_COMPANY.msg)
        return True

class IsInvestor(BasePermission):
    """
    Checking if company user is currently related to is of investment.
    
    """
    def has_permission(self, request, view):
        if request.user.get_company_type():
            raise PermissionDenied(detail=Error.NOT_INVESTOR.msg)
        return True

class IsStartup(BasePermission):
    """
    Checking if company user is currently related to is startup.
    
    """
    def has_permission(self, request, view):
        if not request.user.get_company_type():
            raise PermissionDenied(detail=Error.NOT_STARTUP.msg)
        return True

class CustomUserUpdatePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj
