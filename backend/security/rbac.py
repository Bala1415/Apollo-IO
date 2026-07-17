import logging
from typing import Set, Dict, List

logger = logging.getLogger("apollo.security.rbac")

# Define the complete set of system permissions
class Permissions:
    LEAD_READ = "lead:read"
    LEAD_WRITE = "lead:write"
    LEAD_DELETE = "lead:delete"
    
    COMPANY_READ = "company:read"
    
    REPORT_READ = "report:read"
    REPORT_EXPORT = "report:export"
    
    DASHBOARD_READ = "dashboard:read"
    
    NOTIFICATION_SEND = "notification:send"
    
    ADMINISTRATION = "admin:all"

# Define System Roles and their granted permissions
# Inheritance is flattened here for direct O(1) lookup during evaluation.
ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    "Admin": {
        Permissions.ADMINISTRATION,
        Permissions.LEAD_READ, Permissions.LEAD_WRITE, Permissions.LEAD_DELETE,
        Permissions.COMPANY_READ,
        Permissions.REPORT_READ, Permissions.REPORT_EXPORT,
        Permissions.DASHBOARD_READ,
        Permissions.NOTIFICATION_SEND
    },
    "Analyst": {
        Permissions.LEAD_READ, Permissions.LEAD_WRITE,
        Permissions.COMPANY_READ,
        Permissions.REPORT_READ, Permissions.REPORT_EXPORT,
        Permissions.DASHBOARD_READ
    },
    "Sales": {
        Permissions.LEAD_READ,
        Permissions.COMPANY_READ,
        Permissions.REPORT_READ,
        Permissions.DASHBOARD_READ
    },
    "Viewer": {
        Permissions.LEAD_READ,
        Permissions.COMPANY_READ,
        Permissions.REPORT_READ,
        Permissions.DASHBOARD_READ
    },
    "API Client": {
        Permissions.LEAD_READ, Permissions.LEAD_WRITE,
        Permissions.COMPANY_READ,
        Permissions.REPORT_READ
    }
}

def has_permission(user_role: str, required_permissions: List[str]) -> bool:
    """
    Evaluates if a given role possesses all required permissions.
    """
    if not required_permissions:
        return True
        
    granted_permissions = ROLE_PERMISSIONS.get(user_role, set())
    
    # Superuser override
    if Permissions.ADMINISTRATION in granted_permissions:
        return True
        
    # Check if all required permissions are in the granted set
    return all(req_perm in granted_permissions for req_perm in required_permissions)

def get_role_permissions(role: str) -> List[str]:
    """Returns the list of permissions for a specific role."""
    return list(ROLE_PERMISSIONS.get(role, set()))
