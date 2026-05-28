"""
Custom permission classes for tenant isolation and role-based access control.

Requirements: 3.2, 3.3, 14.2, 14.3, 14.4
"""

from rest_framework import permissions


class IsTenantAuthorized(permissions.BasePermission):
    """
    Permission class that enforces tenant isolation.
    
    Ensures users can only access data belonging to their authorized client company.
    Requirements: 3.2, 3.3, 14.4
    """
    
    message = "You do not have permission to access this tenant's data."
    
    def has_permission(self, request, view):
        """
        Check if user is authenticated and has tenant authorization.
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers can access all tenants
        if request.user.is_superuser:
            return True
        
        # Check if user has authorized_client_companies attribute
        if hasattr(request.user, 'authorized_client_companies'):
            return request.user.authorized_client_companies.exists()
        
        return True  # Allow if no specific tenant restrictions
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user can access this specific object based on tenant.
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers can access all objects
        if request.user.is_superuser:
            return True
        
        # Get the client_company from the object
        client_company = None
        if hasattr(obj, 'client_company'):
            client_company = obj.client_company
        elif hasattr(obj, 'record') and hasattr(obj.record, 'client_company'):
            client_company = obj.record.client_company
        
        if not client_company:
            return False
        
        # Check if user is authorized for this client company
        if hasattr(request.user, 'authorized_client_companies'):
            return request.user.authorized_client_companies.filter(
                id=client_company.id
            ).exists()
        
        return True  # Allow if no specific tenant restrictions


class IsAnalyst(permissions.BasePermission):
    """
    Permission class that restricts access to users with Analyst role or higher.
    
    Requirements: 14.2, 14.3
    """
    
    message = "You must be an Analyst or Administrator to perform this action."
    
    def has_permission(self, request, view):
        """
        Check if user has Analyst role or higher.
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers and staff have analyst permissions
        if request.user.is_superuser or request.user.is_staff:
            return True
        
        # Check for analyst group membership
        return request.user.groups.filter(name__in=['Analyst', 'Administrator']).exists()


class IsAdministrator(permissions.BasePermission):
    """
    Permission class that restricts access to users with Administrator role.
    
    Requirements: 14.2, 14.3
    """
    
    message = "You must be an Administrator to perform this action."
    
    def has_permission(self, request, view):
        """
        Check if user has Administrator role.
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers have administrator permissions
        if request.user.is_superuser:
            return True
        
        # Check for administrator group membership
        return request.user.groups.filter(name='Administrator').exists()


class IsApprovalAuthorized(permissions.BasePermission):
    """
    Permission class for approval workflow actions.
    
    Combines tenant authorization with analyst role requirement.
    Requirements: 8.1, 14.2, 14.3
    """
    
    message = "You must be an authorized Analyst to approve records."
    
    def has_permission(self, request, view):
        """
        Check if user is both an analyst and tenant-authorized.
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Must be analyst or higher
        is_analyst = (
            request.user.is_superuser or 
            request.user.is_staff or
            request.user.groups.filter(name__in=['Analyst', 'Administrator']).exists()
        )
        
        return is_analyst
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user can approve this specific record based on tenant.
        """
        # Use IsTenantAuthorized logic for object-level check
        tenant_permission = IsTenantAuthorized()
        return tenant_permission.has_object_permission(request, view, obj)
