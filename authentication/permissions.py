from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from forum.errors import Error
from .models import STARTUP, INVESTMENT


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
    position = 'F'
    error = Error.NOT_FOUNDER
        
class IsRepresentative(PositionPermission):
    position = 'R'
    error = Error.NOT_REPRESENTATIVE  

class CompanyTypePermission(BasePermission):
    type = None
    error = None

    def has_permission(self, request, view):
        if request.user.get_company_type() != self.type:
            raise PermissionDenied(detail=self.error.msg)
        return True
    
class IsInvestor(CompanyTypePermission):
    type = INVESTMENT
    error = Error.NOT_INVESTOR

class IsStartup(CompanyTypePermission):
    type = STARTUP
    error = Error.NOT_STARTUP
            
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



class CustomUserUpdatePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj
