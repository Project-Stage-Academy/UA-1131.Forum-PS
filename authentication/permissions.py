from rest_framework.permissions import BasePermission
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, NotAuthenticated

# this permission handles errors if any
class CustomPermission(BasePermission):
    def check_errors(self, request):
        error = request.user.error
        if error:
            if error['status'] == status.HTTP_403_FORBIDDEN:
                raise PermissionDenied(detail=error['msg'])
            if error['status'] == status.HTTP_401_UNAUTHORIZED:
                raise NotAuthenticated(detail=error['msg'])
        return True
    
    def has_permission(self, request, view):
        self.check_errors(request)

# this permission ensures that user is not authenticated. 
# could be useful for registration or login functionality
class IsNotAuthenticated(CustomPermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return False
        return True

# this permission ensures that user is verified by email
# could be useful for verification functionality
class IsVerified(CustomPermission):
    def has_permission(self, request, view):
        super().has_permission(request, view)
        if not request.user.is_verified:
            return False
        return True

# this permission checks if user was authenticated  
class IsAuthenticated(CustomPermission):
    def has_permission(self, request, view):
        super().has_permission(request, view)
        return request.user.is_authenticated
# this permission checks if user is related to investor company at the moment
# and therefore acts as an investor
# checks if user has investor role, simply speaking   
class IsInvestor(CustomPermission):
    def has_permission(self, request, view):
        super().has_permission(request, view)
        if request.user.is_startup == False:
            return True
        return False
# this permission do the same as IsInvestor only for startup role
class IsStartup(CustomPermission):
    def has_permission(self, request, view):
        super().has_permission(request, view)
        if request.user.is_startup == True:
            return True
        return False
# this permission checks if user is related to company at the moment
# could be removed as IsInvestor and IsStartup are doing basicly the same job
class IsRelatedToCompany(CustomPermission):
    def has_permission(self, request, view):
        super().has_permission(request, view)
        if request.user.company_id:
            return True
        return False


class CustomUserUpdatePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj
