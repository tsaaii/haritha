# config/auth.py
"""
Authentication Configuration
Manages user access control and OAuth settings
"""

import json
import os
from typing import List, Dict, Optional

# Allowed users configuration - Easy to edit
ALLOWED_USERS = {
    # Email addresses that have access to the admin dashboard
    "administrators": [
        "saaitejaa@gmail.com",
        "director@swacchaandhra.gov.in",
        "your.email@gmail.com"  # Add your email here
    ],
    
    # Viewers with read-only access
    "viewers": [
        "viewer@swacchaandhra.gov.in",
        "analyst@swacchaandhra.gov.in"
    ],
    
    # Super admins with full access
    "super_admins": [
        "saaitejaa@gmail.com"
    ]
}

# OAuth Configuration
OAUTH_CONFIG = {
    "google": {
        "client_secrets_file": "client_secrets.json",  # Your Google OAuth credentials file
        "scopes": ["openid", "email", "profile"],
        "redirect_uri": "http://localhost:8050/oauth/callback",  # Adjust for production
        "hosted_domain": None  # Set to your domain to restrict to specific domain users
    }
}

# Session configuration
SESSION_CONFIG = {
    "secret_key": "your-secret-key-change-this-in-production",  # Change this!
    "session_timeout": 3600,  # 1 hour in seconds
    "remember_me_duration": 86400 * 30,  # 30 days in seconds
    "secure_cookies": False  # Set to True in production with HTTPS
}

# Security settings
SECURITY_CONFIG = {
    "max_login_attempts": 5,
    "lockout_duration": 900,  # 15 minutes in seconds
    "require_domain_verification": False,
    "allowed_domains": ["swacchaandhra.gov.in", "gmail.com"]  # Add your allowed domains
}

def get_user_role(email: str) -> Optional[str]:
    """
    Get user role based on email address
    
    Args:
        email (str): User email address
        
    Returns:
        str: User role or None if not authorized
    """
    email = email.lower().strip()
    
    if email in ALLOWED_USERS["super_admins"]:
        return "super_admin"
    elif email in ALLOWED_USERS["administrators"]:
        return "administrator"
    elif email in ALLOWED_USERS["viewers"]:
        return "viewer"
    else:
        return None

def is_user_authorized(email: str) -> bool:
    """
    Check if user is authorized to access the system
    
    Args:
        email (str): User email address
        
    Returns:
        bool: True if authorized, False otherwise
    """
    return get_user_role(email) is not None

def load_google_oauth_config() -> Dict:
    """
    Load Google OAuth configuration from client_secrets.json
    
    Returns:
        dict: OAuth configuration
    """
    try:
        with open(OAUTH_CONFIG["google"]["client_secrets_file"], 'r') as f:
            client_config = json.load(f)
        
        return {
            "client_id": client_config["web"]["client_id"],
            "client_secret": client_config["web"]["client_secret"],
            "auth_uri": client_config["web"]["auth_uri"],
            "token_uri": client_config["web"]["token_uri"],
            "redirect_uris": client_config["web"]["redirect_uris"]
        }
    except FileNotFoundError:
        print("Warning: client_secrets.json not found. Google OAuth will not work.")
        return {}
    except KeyError as e:
        print(f"Error: Invalid client_secrets.json format. Missing key: {e}")
        return {}

def get_permissions(role: str) -> List[str]:
    """
    Get permissions based on user role
    
    Args:
        role (str): User role
        
    Returns:
        list: List of permissions
    """
    permissions_map = {
        "super_admin": [
            "view_dashboard",
            "edit_data",
            "manage_users",
            "export_reports",
            "system_admin",
            "view_analytics",
            "manage_settings"
        ],
        "administrator": [
            "view_dashboard",
            "edit_data",
            "export_reports",
            "view_analytics"
        ],
        "viewer": [
            "view_dashboard",
            "view_analytics"
        ]
    }
    
    return permissions_map.get(role, [])

# Easy configuration updates
def add_user(email: str, role: str = "viewer") -> bool:
    """
    Add a new user to the allowed users list
    Note: This is for reference - you'll need to manually edit this file
    
    Args:
        email (str): User email address
        role (str): User role (viewer, administrator, super_admin)
        
    Returns:
        bool: Success status
    """
    role_key = f"{role}s" if role != "super_admin" else "super_admins"
    
    if role_key in ALLOWED_USERS:
        if email not in ALLOWED_USERS[role_key]:
            print(f"To add user {email} as {role}, edit config/auth.py and add to ALLOWED_USERS['{role_key}']")
            return True
    return False

def remove_user(email: str) -> bool:
    """
    Remove a user from all roles
    Note: This is for reference - you'll need to manually edit this file
    
    Args:
        email (str): User email address
        
    Returns:
        bool: Success status
    """
    removed = False
    for role_list in ALLOWED_USERS.values():
        if email in role_list:
            print(f"To remove user {email}, edit config/auth.py and remove from appropriate ALLOWED_USERS list")
            removed = True
    return removed

# Environment-based configuration
def get_environment_config():
    """Get configuration based on environment"""
    environment = os.getenv('FLASK_ENV', 'development')
    
    if environment == 'production':
        return {
            "redirect_uri": "https://yourdomain.com/oauth/callback",
            "secure_cookies": True,
            "session_timeout": 7200,  # 2 hours
            "require_domain_verification": True
        }
    else:
        return {
            "redirect_uri": "http://localhost:8050/oauth/callback",
            "secure_cookies": False,
            "session_timeout": 3600,  # 1 hour
            "require_domain_verification": False
        }

# Validation functions
def validate_email_domain(email: str) -> bool:
    """Validate if email domain is allowed"""
    if not SECURITY_CONFIG["require_domain_verification"]:
        return True
    
    domain = email.split('@')[-1].lower()
    return domain in SECURITY_CONFIG["allowed_domains"]

def get_user_display_name(email: str, role: str) -> str:
    """Get display name for user"""
    name = email.split('@')[0].replace('.', ' ').title()
    role_display = role.replace('_', ' ').title()
    return f"{name} ({role_display})"

# Export configuration
__all__ = [
    'ALLOWED_USERS',
    'OAUTH_CONFIG', 
    'SESSION_CONFIG',
    'SECURITY_CONFIG',
    'get_user_role',
    'is_user_authorized',
    'load_google_oauth_config',
    'get_permissions',
    'validate_email_domain',
    'get_user_display_name'
]