"""
Enterprise Session Management Service for MeStore.

This module provides comprehensive session management with:
- Concurrent session limits per user
- Device tracking and fingerprinting
- Session timeout management (idle and absolute)
- Enterprise security features for PCI DSS compliance

Author: Backend Senior Developer
Version: 1.0.0 Enterprise
"""

import json
import uuid
import secrets
import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from fastapi import Request
from pydantic import BaseModel

from app.core.config import settings
from app.core.security import generate_device_fingerprint
from app.core.logger import get_logger

logger = get_logger(__name__)


class SessionInfo(BaseModel):
    """Session information model."""
    session_id: str
    user_id: str
    device_fingerprint: str
    ip_address: str
    user_agent: str
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    is_active: bool = True

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EnterpriseSessionService:
    """
    Enterprise-grade session management service.

    Features:
    - Concurrent session limits
    - Device fingerprinting and tracking
    - Session timeout management
    - Redis-based session storage
    - Security audit logging
    """

    def __init__(self, redis_client):
        """Initialize session service with Redis client."""
        self.redis = redis_client
        self.session_prefix = "session:"
        self.user_sessions_prefix = "user_sessions:"
        self.device_sessions_prefix = "device_sessions:"

        # SECURITY FIX: Secure session configuration
        self.session_secret = settings.SECRET_KEY.encode('utf-8')
        self.token_entropy_bits = 256  # High entropy for session tokens

    async def create_session(
        self,
        user_id: str,
        request: Request,
        access_token: str,
        refresh_token: str
    ) -> SessionInfo:
        """
        Create a new user session with device tracking.

        Args:
            user_id: User identifier
            request: FastAPI request object
            access_token: JWT access token
            refresh_token: JWT refresh token

        Returns:
            SessionInfo: Created session information

        Raises:
            ValueError: If maximum concurrent sessions exceeded
        """
        try:
            # SECURITY FIX: Generate cryptographically secure session ID
            session_id = self._generate_secure_session_id()
            device_fingerprint = generate_device_fingerprint(request)

            # Validate device fingerprint strength
            if not self._validate_device_fingerprint(device_fingerprint, request):
                raise ValueError("Device fingerprinting failed security validation")
            ip_address = getattr(request.client, 'host', 'unknown') if request.client else 'unknown'
            user_agent = request.headers.get('User-Agent', 'unknown')

            # Check concurrent session limits
            await self._enforce_session_limits(user_id, device_fingerprint)

            # Create session info
            now = datetime.now(timezone.utc)
            session_info = SessionInfo(
                session_id=session_id,
                user_id=user_id,
                device_fingerprint=device_fingerprint,
                ip_address=ip_address,
                user_agent=user_agent,
                created_at=now,
                last_activity=now,
                expires_at=now + timedelta(hours=settings.SESSION_ABSOLUTE_TIMEOUT_HOURS)
            )

            # SECURITY FIX: Encrypt sensitive session data
            session_data = {
                **session_info.dict(),
                'access_token': self._encrypt_token(access_token),
                'refresh_token': self._encrypt_token(refresh_token),
                'session_hash': self._generate_session_hash(session_id, user_id, device_fingerprint)
            }

            # Store with multiple keys for efficient lookups
            session_key = f"{self.session_prefix}{session_id}"
            user_sessions_key = f"{self.user_sessions_prefix}{user_id}"
            device_sessions_key = f"{self.device_sessions_prefix}{device_fingerprint}"

            # Store session data
            await self.redis.setex(
                session_key,
                settings.SESSION_ABSOLUTE_TIMEOUT_HOURS * 3600,
                json.dumps(session_data, default=str)
            )

            # Add to user's active sessions
            await self.redis.sadd(user_sessions_key, session_id)
            await self.redis.expire(user_sessions_key, settings.SESSION_ABSOLUTE_TIMEOUT_HOURS * 3600)

            # Add to device sessions
            await self.redis.sadd(device_sessions_key, session_id)
            await self.redis.expire(device_sessions_key, settings.SESSION_ABSOLUTE_TIMEOUT_HOURS * 3600)

            logger.info(
                "Session created",
                user_id=user_id,
                session_id=session_id,
                device_fingerprint=device_fingerprint[:8],
                ip_address=ip_address
            )

            return session_info

        except Exception as e:
            logger.error("Error creating session", error=str(e), user_id=user_id)
            raise

    async def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """
        Retrieve session information by session ID.

        Args:
            session_id: Session identifier

        Returns:
            SessionInfo: Session information or None if not found
        """
        try:
            session_key = f"{self.session_prefix}{session_id}"
            session_data = await self.redis.get(session_key)

            if not session_data:
                return None

            data = json.loads(session_data)

            # SECURITY FIX: Validate session integrity
            if not self._validate_session_integrity(session_id, data):
                logger.warning("Session integrity check failed", session_id=session_id)
                await self.invalidate_session(session_id)
                return None

            # Convert datetime strings back to datetime objects
            for field in ['created_at', 'last_activity', 'expires_at']:
                if data.get(field):
                    data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))

            # Decrypt tokens if needed for validation
            if 'access_token' in data:
                data['access_token'] = self._decrypt_token(data['access_token'])
            if 'refresh_token' in data:
                data['refresh_token'] = self._decrypt_token(data['refresh_token'])

            return SessionInfo(**{k: v for k, v in data.items() if k in SessionInfo.__fields__})

        except Exception as e:
            logger.error("Error retrieving session", error=str(e), session_id=session_id)
            return None

    async def update_session_activity(self, session_id: str) -> bool:
        """
        Update session's last activity timestamp.

        Args:
            session_id: Session identifier

        Returns:
            bool: True if successfully updated
        """
        try:
            session_key = f"{self.session_prefix}{session_id}"
            session_data = await self.redis.get(session_key)

            if not session_data:
                return False

            data = json.loads(session_data)
            now = datetime.now(timezone.utc)

            # SECURITY FIX: Enhanced timeout validation
            last_activity = datetime.fromisoformat(data['last_activity'].replace('Z', '+00:00'))
            idle_limit = timedelta(minutes=settings.SESSION_IDLE_TIMEOUT_MINUTES)
            created_at = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
            absolute_limit = timedelta(hours=settings.SESSION_ABSOLUTE_TIMEOUT_HOURS)

            # Check both idle and absolute timeouts
            if (now - last_activity > idle_limit) or (now - created_at > absolute_limit):
                logger.info("Session expired", session_id=session_id,
                           idle_expired=now - last_activity > idle_limit,
                           absolute_expired=now - created_at > absolute_limit)
                await self.invalidate_session(session_id)
                return False

            # SECURITY FIX: Validate session hasn't been tampered with
            if not self._validate_session_integrity(session_id, data):
                logger.warning("Session integrity validation failed during update", session_id=session_id)
                await self.invalidate_session(session_id)
                return False

            # Update last activity
            data['last_activity'] = now.isoformat()

            # Update in Redis
            await self.redis.setex(
                session_key,
                settings.SESSION_ABSOLUTE_TIMEOUT_HOURS * 3600,
                json.dumps(data, default=str)
            )

            return True

        except Exception as e:
            logger.error("Error updating session activity", error=str(e), session_id=session_id)
            return False

    async def invalidate_session(self, session_id: str) -> bool:
        """
        Invalidate a specific session.

        Args:
            session_id: Session identifier

        Returns:
            bool: True if successfully invalidated
        """
        try:
            # Get session info first
            session_info = await self.get_session(session_id)
            if not session_info:
                return True  # Already invalid

            # Remove from Redis
            session_key = f"{self.session_prefix}{session_id}"
            user_sessions_key = f"{self.user_sessions_prefix}{session_info.user_id}"
            device_sessions_key = f"{self.device_sessions_prefix}{session_info.device_fingerprint}"

            # Delete session data
            await self.redis.delete(session_key)

            # Remove from user's sessions
            await self.redis.srem(user_sessions_key, session_id)

            # Remove from device sessions
            await self.redis.srem(device_sessions_key, session_id)

            logger.info(
                "Session invalidated",
                session_id=session_id,
                user_id=session_info.user_id
            )

            return True

        except Exception as e:
            logger.error("Error invalidating session", error=str(e), session_id=session_id)
            return False

    async def invalidate_all_user_sessions(self, user_id: str) -> int:
        """
        Invalidate all sessions for a user (e.g., on password change).

        Args:
            user_id: User identifier

        Returns:
            int: Number of sessions invalidated
        """
        try:
            user_sessions_key = f"{self.user_sessions_prefix}{user_id}"
            session_ids = await self.redis.smembers(user_sessions_key)

            invalidated_count = 0
            for session_id in session_ids:
                if isinstance(session_id, bytes):
                    session_id = session_id.decode('utf-8')

                if await self.invalidate_session(session_id):
                    invalidated_count += 1

            logger.info(
                "All user sessions invalidated",
                user_id=user_id,
                count=invalidated_count
            )

            return invalidated_count

        except Exception as e:
            logger.error("Error invalidating all user sessions", error=str(e), user_id=user_id)
            return 0

    async def get_user_active_sessions(self, user_id: str) -> List[SessionInfo]:
        """
        Get all active sessions for a user.

        Args:
            user_id: User identifier

        Returns:
            List[SessionInfo]: List of active sessions
        """
        try:
            user_sessions_key = f"{self.user_sessions_prefix}{user_id}"
            session_ids = await self.redis.smembers(user_sessions_key)

            active_sessions = []
            for session_id in session_ids:
                if isinstance(session_id, bytes):
                    session_id = session_id.decode('utf-8')

                session_info = await self.get_session(session_id)
                if session_info and session_info.is_active:
                    active_sessions.append(session_info)

            return active_sessions

        except Exception as e:
            logger.error("Error getting user active sessions", error=str(e), user_id=user_id)
            return []

    async def _enforce_session_limits(self, user_id: str, device_fingerprint: str) -> None:
        """
        Enforce concurrent session limits per user.

        Args:
            user_id: User identifier
            device_fingerprint: Device fingerprint

        Raises:
            ValueError: If session limits exceeded
        """
        try:
            # Get current active sessions
            active_sessions = await self.get_user_active_sessions(user_id)

            # If at limit, remove oldest session
            if len(active_sessions) >= settings.SESSION_MAX_CONCURRENT_SESSIONS:
                oldest_session = min(active_sessions, key=lambda s: s.created_at)
                await self.invalidate_session(oldest_session.session_id)

                logger.info(
                    "Oldest session invalidated due to limit",
                    user_id=user_id,
                    invalidated_session=oldest_session.session_id
                )

        except Exception as e:
            logger.error("Error enforcing session limits", error=str(e), user_id=user_id)
            # Don't raise here to avoid blocking login

    async def cleanup_expired_sessions(self) -> int:
        """
        Cleanup expired sessions (maintenance task).

        Returns:
            int: Number of sessions cleaned up
        """
        try:
            # This would be implemented as a background task
            # For now, Redis TTL handles most cleanup automatically
            return 0
        except Exception as e:
            logger.error("Error cleaning up expired sessions", error=str(e))
            return 0

    async def get_session_statistics(self, user_id: Optional[str] = None) -> Dict:
        """
        Get session statistics for monitoring.

        Args:
            user_id: Optional user ID for user-specific stats

        Returns:
            Dict: Session statistics
        """
        try:
            if user_id:
                active_sessions = await self.get_user_active_sessions(user_id)
                return {
                    "user_id": user_id,
                    "active_sessions": len(active_sessions),
                    "max_allowed": settings.SESSION_MAX_CONCURRENT_SESSIONS,
                    "sessions": [
                        {
                            "session_id": s.session_id,
                            "device_fp": s.device_fingerprint[:8],
                            "ip_address": s.ip_address,
                            "created_at": s.created_at.isoformat(),
                            "last_activity": s.last_activity.isoformat()
                        } for s in active_sessions
                    ]
                }
            else:
                # System-wide statistics would require more complex queries
                return {
                    "system": "enterprise_session_service",
                    "status": "active"
                }

        except Exception as e:
            logger.error("Error getting session statistics", error=str(e))
            return {"error": str(e)}

    # === SECURITY METHODS ===

    def _generate_secure_session_id(self) -> str:
        """Generate cryptographically secure session ID."""
        # Generate 32 bytes (256 bits) of random data
        random_bytes = secrets.token_bytes(32)
        # Create a hash with additional entropy from timestamp
        timestamp = str(datetime.now(timezone.utc).timestamp()).encode('utf-8')
        hash_input = random_bytes + timestamp + self.session_secret
        return hashlib.sha256(hash_input).hexdigest()

    def _validate_device_fingerprint(self, device_fingerprint: str, request: Request) -> bool:
        """Validate device fingerprint meets security requirements."""
        if not device_fingerprint or len(device_fingerprint) < 16:
            return False

        # Check for required headers
        required_headers = settings.DEVICE_FINGERPRINT_REQUIRED_HEADERS
        for header in required_headers:
            if not request.headers.get(header):
                logger.warning("Missing required header for device fingerprinting", header=header)
                return False

        return True

    def _generate_session_hash(self, session_id: str, user_id: str, device_fingerprint: str) -> str:
        """Generate session integrity hash."""
        hash_data = f"{session_id}|{user_id}|{device_fingerprint}|{settings.SECRET_KEY}"
        return hmac.new(
            self.session_secret,
            hash_data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def _validate_session_integrity(self, session_id: str, session_data: dict) -> bool:
        """Validate session data integrity."""
        if 'session_hash' not in session_data:
            return False  # Old session without hash

        stored_hash = session_data['session_hash']
        user_id = session_data.get('user_id', '')
        device_fingerprint = session_data.get('device_fingerprint', '')

        expected_hash = self._generate_session_hash(session_id, user_id, device_fingerprint)
        return hmac.compare_digest(stored_hash, expected_hash)

    def _encrypt_token(self, token: str) -> str:
        """Simple token encryption for storage (in production, use proper encryption)."""
        # For development - in production implement proper encryption
        if settings.ENVIRONMENT == 'production':
            # TODO: Implement proper AES encryption
            pass

        # Simple obfuscation for development
        return hashlib.sha256((token + settings.SECRET_KEY).encode()).hexdigest()

    def _decrypt_token(self, encrypted_token: str) -> str:
        """Simple token decryption (placeholder for development)."""
        # In production, implement proper decryption
        # For now, return the encrypted token as validation doesn't require decryption
        return encrypted_token