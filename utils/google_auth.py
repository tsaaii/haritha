# utils/google_auth.py
"""
Google OAuth Authentication Integration
Handles Google OAuth flow for secure authentication
"""

import json
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
import hashlib
import base64

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    from googleapiclient.discovery import build
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False
    print("Google Auth libraries not installed. Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")

from config.auth import auth_config

class GoogleAuthManager:
    """Manages Google OAuth authentication"""
    
    def __init__(self, client_secrets_file="client_secrets.json"):
        self.client_secrets_file = client_secrets_file
        self.scopes = ['openid', 'email', 'profile']
        self.redirect_uri = None  # Will be set dynamically
        self.sessions = {}  # In-memory session storage (use Redis/DB in production)
        
        if not GOOGLE_AUTH_AVAILABLE:
            raise ImportError("Google Auth libraries not available")
        
        if not os.path.exists(client_secrets_file):
            raise FileNotFoundError(f"Client secrets file not found: {client_secrets_file}")
    
    def setup_oauth_flow(self, redirect_uri: str) -> Flow:
        """Setup OAuth flow with proper redirect URI"""
        self.redirect_uri = redirect_uri
        
        flow = Flow.from_client_secrets_file(
            self.client_secrets_file,
            scopes=self.scopes,
            redirect_uri=redirect_uri
        )
        return flow
    
    def get_authorization_url(self, redirect_uri: str) -> Tuple[str, str]:
        """
        Get Google OAuth authorization URL
        
        Returns:
            Tuple[str, str]: (authorization_url, state)
        """
        flow = self.setup_oauth_flow(redirect_uri)
        
        # Generate state parameter for CSRF protection
        state = secrets.token_urlsafe(32)
        
        authorization_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=state
        )
        
        return authorization_url, state
    
    def handle_oauth_callback(self, 
                            authorization_response: str, 
                            state: str, 
                            expected_state: str,
                            redirect_uri: str) -> Optional[Dict]:
        """
        Handle OAuth callback and get user info
        
        Args:
            authorization_response: Full callback URL
            state: State parameter from callback
            expected_state: Expected state for CSRF protection
            redirect_uri: OAuth redirect URI
            
        Returns:
            Optional[Dict]: User info if successful, None if failed
        """
        # Verify state parameter
        if state != expected_state:
            raise ValueError("Invalid state parameter - possible CSRF attack")
        
        try:
            flow = self.setup_oauth_flow(redirect_uri)
            flow.fetch_token(authorization_response=authorization_response)
            
            # Get user info
            credentials = flow.credentials
            user_info = self._get_user_info(credentials)
            
            return user_info
            
        except Exception as e:
            print(f"OAuth callback error: {e}")
            return None
    
    def _get_user_info(self, credentials: Credentials) -> Dict:
        """Get user information from Google API"""
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        
        return {
            'email': user_info.get('email'),
            'name': user_info.get('name'),
            'picture': user_info.get('picture'),
            'verified_email': user_info.get('verified_email', False),
            'google_id': user_info.get('id')
        }
    
    def create_session(self, user_info: Dict) -> str:
        """
        Create authenticated session
        
        Args:
            user_info: User information from Google
            
        Returns:
            str: Session token
        """
        # Check if user is allowed
        if not auth_config.is_user_allowed(user_info['email']):
            raise PermissionError(f"User {user_info['email']} is not authorized")
        
        # Get user details from config
        user_config = auth_config.get_user_info(user_info['email'])
        
        # Create session token
        session_token = secrets.token_urlsafe(32)
        
        # Store session info
        settings = auth_config.get_settings()
        timeout_minutes = settings.get('session_timeout_minutes', 480)
        
        session_data = {
            'user_info': user_info,
            'user_config': user_config,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(minutes=timeout_minutes),
            'last_activity': datetime.now()
        }
        
        self.sessions[session_token] = session_data
        
        return session_token
    
    def validate_session(self, session_token: str) -> Optional[Dict]:
        """
        Validate session token
        
        Args:
            session_token: Session token to validate
            
        Returns:
            Optional[Dict]: Session data if valid, None if invalid
        """
        if not session_token or session_token not in self.sessions:
            return None
        
        session_data = self.sessions[session_token]
        
        # Check if session expired
        if datetime.now() > session_data['expires_at']:
            del self.sessions[session_token]
            return None
        
        # Update last activity
        session_data['last_activity'] = datetime.now()
        
        return session_data
    
    def logout(self, session_token: str) -> bool:
        """
        Logout user and invalidate session
        
        Args:
            session_token: Session token to invalidate
            
        Returns:
            bool: True if session was found and invalidated
        """
        if session_token in self.sessions:
            del self.sessions[session_token]
            return True
        return False
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        current_time = datetime.now()
        expired_tokens = [
            token for token, data in self.sessions.items()
            if current_time > data['expires_at']
        ]
        
        for token in expired_tokens:
            del self.sessions[token]
    
    def get_active_sessions(self) -> Dict:
        """Get all active sessions (for admin monitoring)"""
        self.cleanup_expired_sessions()
        return {
            token: {
                'user_email': data['user_info']['email'],
                'user_name': data['user_info']['name'],
                'created_at': data['created_at'].isoformat(),
                'expires_at': data['expires_at'].isoformat(),
                'last_activity': data['last_activity'].isoformat()
            }
            for token, data in self.sessions.items()
        }

class MockGoogleAuth:
    """Mock authentication for development when Google Auth is not available"""
    
    def __init__(self):
        self.sessions = {}
    
    def get_authorization_url(self, redirect_uri: str) -> Tuple[str, str]:
        """Mock authorization URL"""
        return "http://localhost:8050/auth/mock", "mock_state"
    
    def handle_oauth_callback(self, *args, **kwargs) -> Optional[Dict]:
        """Mock OAuth callback"""
        return {
            'email': 'admin@swacchaap.gov.in',
            'name': 'Test Admin',
            'picture': '',
            'verified_email': True,
            'google_id': 'mock_id'
        }
    
    def create_session(self, user_info: Dict) -> str:
        """Mock session creation"""
        if not auth_config.is_user_allowed(user_info['email']):
            raise PermissionError(f"User {user_info['email']} is not authorized")
        
        session_token = "mock_session_token"
        self.sessions[session_token] = {
            'user_info': user_info,
            'user_config': auth_config.get_user_info(user_info['email']),
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(hours=8)
        }
        return session_token
    
    def validate_session(self, session_token: str) -> Optional[Dict]:
        """Mock session validation"""
        return self.sessions.get(session_token)
    
    def logout(self, session_token: str) -> bool:
        """Mock logout"""
        if session_token in self.sessions:
            del self.sessions[session_token]
            return True
        return False

# Global instance
if GOOGLE_AUTH_AVAILABLE:
    try:
        google_auth = GoogleAuthManager()
    except (FileNotFoundError, ImportError) as e:
        print(f"Google Auth setup failed: {e}. Using mock authentication.")
        google_auth = MockGoogleAuth()
else:
    google_auth = MockGoogleAuth()

def get_auth_manager():
    """Get authentication manager instance"""
    return google_auth