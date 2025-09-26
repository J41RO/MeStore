"""
CSRF Protection Module for Admin Endpoints

This module provides CSRF (Cross-Site Request Forgery) protection for state-changing
operations on admin endpoints. It implements token-based CSRF protection following
industry best practices.
"""
import secrets
import hashlib
import time
from typing import Optional, Dict, Any
from fastapi import HTTPException, Request, status
from fastapi.security.utils import get_authorization_scheme_param


class CSRFProtectionError(HTTPException):
    """Exception raised when CSRF validation fails"""
    def __init__(self, detail: str = "CSRF token missing or invalid"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class CSRFTokenManager:
    """Manages CSRF token generation and validation"""

    def __init__(self, secret_key: str = None, token_lifetime: int = 3600):
        """
        Initialize CSRF token manager

        Args:
            secret_key: Secret key for token signing (auto-generated if not provided)
            token_lifetime: Token lifetime in seconds (default: 1 hour)
        """
        self.secret_key = secret_key or secrets.token_hex(32)
        self.token_lifetime = token_lifetime

    def generate_token(self, user_id: str, timestamp: Optional[int] = None) -> str:
        """
        Generate a CSRF token for a specific user

        Args:
            user_id: User identifier
            timestamp: Token creation timestamp (current time if not provided)

        Returns:
            CSRF token string
        """
        if timestamp is None:
            timestamp = int(time.time())

        # Create token payload: user_id:timestamp
        payload = f"{user_id}:{timestamp}"

        # Create HMAC signature
        signature = hashlib.sha256(
            f"{payload}:{self.secret_key}".encode()
        ).hexdigest()

        # Combine payload and signature
        token = f"{payload}:{signature}"

        # Base64 encode for URL safety
        import base64
        return base64.b64encode(token.encode()).decode()

    def validate_token(self, token: str, user_id: str) -> bool:
        """
        Validate a CSRF token

        Args:
            token: CSRF token to validate
            user_id: Expected user identifier

        Returns:
            True if token is valid, False otherwise
        """
        try:
            # Decode token
            import base64
            decoded_token = base64.b64decode(token.encode()).decode()

            # Split token components
            parts = decoded_token.split(':')
            if len(parts) != 3:
                return False

            token_user_id, timestamp_str, signature = parts

            # Verify user ID matches
            if token_user_id != user_id:
                return False

            # Verify token hasn't expired
            timestamp = int(timestamp_str)
            if int(time.time()) - timestamp > self.token_lifetime:
                return False

            # Verify signature
            payload = f"{token_user_id}:{timestamp_str}"
            expected_signature = hashlib.sha256(
                f"{payload}:{self.secret_key}".encode()
            ).hexdigest()

            return signature == expected_signature

        except (ValueError, TypeError):
            return False


# Global CSRF token manager instance
csrf_manager = CSRFTokenManager()


def get_csrf_token_from_request(request: Request) -> Optional[str]:
    """
    Extract CSRF token from request headers or form data

    Args:
        request: FastAPI request object

    Returns:
        CSRF token if found, None otherwise
    """
    # Try X-CSRF-Token header first
    csrf_token = request.headers.get("X-CSRF-Token")
    if csrf_token:
        return csrf_token

    # Try X-CSRFToken header (alternative format)
    csrf_token = request.headers.get("X-CSRFToken")
    if csrf_token:
        return csrf_token

    # For form submissions, check form data
    # Note: This would require async form parsing in actual implementation
    return None


def validate_csrf_protection(request: Request, user_id: str) -> None:
    """
    Validate CSRF protection for a request

    Args:
        request: FastAPI request object
        user_id: Current user identifier

    Raises:
        CSRFProtectionError: If CSRF validation fails
    """
    # Extract CSRF token from request
    csrf_token = get_csrf_token_from_request(request)

    if not csrf_token:
        raise CSRFProtectionError("CSRF token is required for this operation")

    # Validate token
    if not csrf_manager.validate_token(csrf_token, user_id):
        raise CSRFProtectionError("Invalid or expired CSRF token")


def generate_csrf_token_for_user(user_id: str) -> str:
    """
    Generate a CSRF token for a user (utility function)

    Args:
        user_id: User identifier

    Returns:
        CSRF token string
    """
    return csrf_manager.generate_token(user_id)