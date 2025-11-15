"""
Custom permissions for role-based access control.

Roles:
- admin: Full CRUD access to everything
- worker: CRUD on production data, read-only on finance
- accountant: CRUD on finance data, read-only on everything else
"""

from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Permission class that allows only admin users.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'rol') and
            request.user.rol == 'admin'
        )


class IsWorker(permissions.BasePermission):
    """
    Permission class that allows only worker users.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'rol') and
            request.user.rol == 'worker'
        )


class IsAccountant(permissions.BasePermission):
    """
    Permission class that allows only accountant users.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'rol') and
            request.user.rol == 'accountant'
        )


class ProductionPermission(permissions.BasePermission):
    """
    Permission for production endpoints.
    - admin: Full CRUD
    - worker: Full CRUD
    - accountant: Read-only
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not hasattr(request.user, 'rol'):
            return False
        
        user_role = request.user.rol
        
        # Admin has full access
        if user_role == 'admin':
            return True
        
        # Worker has full access
        if user_role == 'worker':
            return True
        
        # Accountant has read-only access
        if user_role == 'accountant':
            return request.method in permissions.SAFE_METHODS
        
        return False


class FinancePermission(permissions.BasePermission):
    """
    Permission for finance endpoints.
    - admin: Full CRUD
    - accountant: Full CRUD
    - worker: Read-only
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not hasattr(request.user, 'rol'):
            return False
        
        user_role = request.user.rol
        
        # Admin has full access
        if user_role == 'admin':
            return True
        
        # Accountant has full access
        if user_role == 'accountant':
            return True
        
        # Worker has read-only access
        if user_role == 'worker':
            return request.method in permissions.SAFE_METHODS
        
        return False


class ReportPermission(permissions.BasePermission):
    """
    Permission for report endpoints.
    - admin: Full CRUD
    - accountant: Full CRUD
    - worker: Read and create only
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not hasattr(request.user, 'rol'):
            return False
        
        user_role = request.user.rol
        
        # Admin has full access
        if user_role == 'admin':
            return True
        
        # Accountant has full access
        if user_role == 'accountant':
            return True
        
        # Worker can read and create, but not delete
        if user_role == 'worker':
            return request.method in ['GET', 'POST', 'HEAD', 'OPTIONS']
        
        return False
