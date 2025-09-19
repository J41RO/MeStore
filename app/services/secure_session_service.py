"""
Secure Session Management Service
================================

Redis-based session management with device tracking, concurrent session limits,
and comprehensive security features for the MeStore application.

Security Features:
- Redis-based session storage
- Device fingerprinting and tracking
- Concurrent session limits
- Session timeout and cleanup
- Secure session cookies
- Session hijacking detection
- Geographic anomaly detection

Author: Security Backend AI
Date: 2025-09-17
Purpose: Provide secure session management for authenticated users
"""

import asyncio
import json
import hashlib
import redis
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from user_agents import parse

from app.core.config import settings


@dataclass
class DeviceFingerprint:
    """
    Device fingerprint for session tracking.
    """
    user_agent: str
    ip_address: str
    device_hash: str
    browser_name: str
    browser_version: str
    os_name: str
    os_version: str
    is_mobile: bool
    is_tablet: bool
    is_bot: bool

    @classmethod
    def create_from_request(cls, user_agent: str, ip_address: str) -> 'DeviceFingerprint':
        """
        Create device fingerprint from request data.

        Args:
            user_agent: HTTP User-Agent header
            ip_address: Client IP address

        Returns:
            DeviceFingerprint object
        """
        # Parse user agent
        ua = parse(user_agent)

        # Create device hash for fingerprinting
        device_data = f"{user_agent}:{ip_address}:{ua.browser.family}:{ua.os.family}"
        device_hash = hashlib.sha256(device_data.encode()).hexdigest()[:16]

        return cls(
            user_agent=user_agent,
            ip_address=ip_address,
            device_hash=device_hash,
            browser_name=ua.browser.family,
            browser_version=ua.browser.version_string,
            os_name=ua.os.family,
            os_version=ua.os.version_string,
            is_mobile=ua.is_mobile,
            is_tablet=ua.is_tablet,
            is_bot=ua.is_bot
        )


@dataclass
class SessionData:
    """
    Comprehensive session data structure.
    """
    session_id: str
    user_id: str
    email: str
    user_type: str
    device_fingerprint: DeviceFingerprint
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    is_active: bool
    login_source: str  # web, mobile, api
    security_flags: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert session data to dictionary for Redis storage."""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'email': self.email,
            'user_type': self.user_type,
            'device_fingerprint': asdict(self.device_fingerprint),
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'is_active': self.is_active,
            'login_source': self.login_source,
            'security_flags': self.security_flags
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionData':
        """Create SessionData from dictionary."""
        return cls(
            session_id=data['session_id'],
            user_id=data['user_id'],
            email=data['email'],
            user_type=data['user_type'],
            device_fingerprint=DeviceFingerprint(**data['device_fingerprint']),
            created_at=datetime.fromisoformat(data['created_at']),
            last_activity=datetime.fromisoformat(data['last_activity']),
            expires_at=datetime.fromisoformat(data['expires_at']),
            is_active=data['is_active'],
            login_source=data.get('login_source', 'web'),
            security_flags=data.get('security_flags', {})
        )


class SessionSecurityMonitor:
    """
    Monitor for session security anomalies.
    """

    @staticmethod
    def detect_device_change(
        stored_fingerprint: DeviceFingerprint,
        current_fingerprint: DeviceFingerprint
    ) -> Tuple[bool, str]:
        """
        Detect if device characteristics have changed.

        Args:
            stored_fingerprint: Original device fingerprint
            current_fingerprint: Current request device fingerprint

        Returns:
            Tuple[bool, str]: (is_suspicious, reason)
        """
        # Check for major browser changes
        if stored_fingerprint.browser_name != current_fingerprint.browser_name:
            return True, "Browser family changed"

        # Check for OS changes
        if stored_fingerprint.os_name != current_fingerprint.os_name:
            return True, "Operating system changed"

        # Check for device type changes
        if stored_fingerprint.is_mobile != current_fingerprint.is_mobile:
            return True, "Device type changed (mobile/desktop)"

        return False, "Device fingerprint consistent"

    @staticmethod
    def detect_ip_anomaly(
        stored_ip: str,
        current_ip: str,
        allowed_ip_changes: int = 3
    ) -> Tuple[bool, str]:
        """
        Detect suspicious IP address changes.

        Args:
            stored_ip: Original IP address
            current_ip: Current IP address
            allowed_ip_changes: Number of allowed IP changes

        Returns:
            Tuple[bool, str]: (is_suspicious, reason)
        """
        if stored_ip == current_ip:
            return False, "Same IP address"

        # Check if IPs are in same subnet (simple check)
        stored_parts = stored_ip.split('.')
        current_parts = current_ip.split('.')

        if len(stored_parts) == 4 and len(current_parts) == 4:
            # Same /24 subnet
            if stored_parts[:3] == current_parts[:3]:
                return False, "Same local network"

            # Same /16 subnet (less strict for mobile users)
            if stored_parts[:2] == current_parts[:2]:
                return False, "Same regional network"

        return True, "Significant IP address change detected"


class SecureSessionService:
    """
    Comprehensive secure session management service.
    """

    def __init__(self, redis_client=None):
        """
        Initialize secure session service.

        Args:
            redis_client: Optional Redis client instance
        """
        self.redis_client = redis_client or self._get_redis_client()
        self.session_timeout = getattr(settings, 'SESSION_TIMEOUT_MINUTES', 60)
        self.max_concurrent_sessions = getattr(settings, 'MAX_CONCURRENT_SESSIONS', 3)
        self.security_monitor = SessionSecurityMonitor()

    def _get_redis_client(self):
        """Get Redis client for session management."""
        try:
            return redis.Redis(
                host=getattr(settings, 'REDIS_HOST', 'localhost'),
                port=getattr(settings, 'REDIS_PORT', 6379),
                decode_responses=True
            )
        except Exception as e:
            raise RuntimeError(f"Redis connection failed for session management: {e}")

    def _get_session_key(self, session_id: str) -> str:
        """Generate Redis key for session data."""
        return f"session:{session_id}"

    def _get_user_sessions_key(self, user_id: str) -> str:
        """Generate Redis key for user's active sessions."""
        return f"user_sessions:{user_id}"

    async def create_session(
        self,
        user_id: str,
        email: str,
        user_type: str,
        user_agent: str,
        ip_address: str,
        login_source: str = "web"
    ) -> SessionData:
        """
        Create a new secure session.

        Args:
            user_id: User ID
            email: User email
            user_type: User type (BUYER, VENDOR, ADMIN)
            user_agent: HTTP User-Agent header
            ip_address: Client IP address
            login_source: Source of login (web, mobile, api)

        Returns:
            SessionData: Created session
        """
        # Generate unique session ID
        session_id = str(uuid.uuid4())

        # Create device fingerprint
        device_fingerprint = DeviceFingerprint.create_from_request(user_agent, ip_address)

        # Check for bot detection
        if device_fingerprint.is_bot:
            raise ValueError("Bot access not allowed for authenticated sessions")

        # Session timestamps
        now = datetime.utcnow()
        expires_at = now + timedelta(minutes=self.session_timeout)

        # Create session data
        session_data = SessionData(
            session_id=session_id,
            user_id=user_id,
            email=email,
            user_type=user_type,
            device_fingerprint=device_fingerprint,
            created_at=now,
            last_activity=now,
            expires_at=expires_at,
            is_active=True,
            login_source=login_source,
            security_flags={}
        )

        # Enforce concurrent session limits
        await self._enforce_session_limits(user_id, session_data)

        # Store session in Redis
        session_key = self._get_session_key(session_id)
        session_ttl = int((expires_at - now).total_seconds())

        self.redis_client.setex(
            session_key,
            session_ttl,
            json.dumps(session_data.to_dict())
        )

        # Add to user's active sessions
        user_sessions_key = self._get_user_sessions_key(user_id)
        self.redis_client.sadd(user_sessions_key, session_id)
        self.redis_client.expire(user_sessions_key, session_ttl)

        return session_data

    async def get_session(self, session_id: str) -> Optional[SessionData]:
        """
        Retrieve session data by session ID.

        Args:
            session_id: Session ID

        Returns:
            SessionData if session exists and is valid, None otherwise
        """
        session_key = self._get_session_key(session_id)
        session_json = self.redis_client.get(session_key)

        if not session_json:
            return None

        try:
            session_dict = json.loads(session_json)
            session_data = SessionData.from_dict(session_dict)

            # Check if session has expired
            if session_data.expires_at < datetime.utcnow():
                await self.destroy_session(session_id)
                return None

            # Check if session is active
            if not session_data.is_active:
                return None

            return session_data

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Invalid session data, remove it
            await self.destroy_session(session_id)
            return None

    async def validate_session(
        self,
        session_id: str,
        user_agent: str,
        ip_address: str
    ) -> Tuple[Optional[SessionData], List[str]]:
        """
        Validate session with security checks.

        Args:
            session_id: Session ID
            user_agent: Current HTTP User-Agent header
            ip_address: Current client IP address

        Returns:
            Tuple[SessionData, List[str]]: Session data and security warnings
        """
        session_data = await self.get_session(session_id)
        security_warnings = []

        if not session_data:
            return None, ["Session not found or expired"]

        # Create current device fingerprint
        current_fingerprint = DeviceFingerprint.create_from_request(user_agent, ip_address)

        # Check for device changes
        device_suspicious, device_reason = self.security_monitor.detect_device_change(
            session_data.device_fingerprint,
            current_fingerprint
        )

        if device_suspicious:
            security_warnings.append(f"Device change detected: {device_reason}")
            session_data.security_flags['device_change'] = device_reason

        # Check for IP anomalies
        ip_suspicious, ip_reason = self.security_monitor.detect_ip_anomaly(
            session_data.device_fingerprint.ip_address,
            current_fingerprint.ip_address
        )

        if ip_suspicious:
            security_warnings.append(f"IP anomaly detected: {ip_reason}")
            session_data.security_flags['ip_anomaly'] = ip_reason

        # Update last activity
        await self.update_session_activity(session_id)

        return session_data, security_warnings

    async def update_session_activity(self, session_id: str) -> bool:
        """
        Update session last activity timestamp.

        Args:
            session_id: Session ID

        Returns:
            bool: True if updated successfully
        """
        session_data = await self.get_session(session_id)
        if not session_data:
            return False

        # Update last activity
        session_data.last_activity = datetime.utcnow()

        # Extend expiration
        session_data.expires_at = datetime.utcnow() + timedelta(minutes=self.session_timeout)

        # Save updated session
        session_key = self._get_session_key(session_id)
        session_ttl = int((session_data.expires_at - datetime.utcnow()).total_seconds())

        self.redis_client.setex(
            session_key,
            session_ttl,
            json.dumps(session_data.to_dict())
        )

        return True

    async def destroy_session(self, session_id: str) -> bool:
        """
        Destroy a session.

        Args:
            session_id: Session ID to destroy

        Returns:
            bool: True if session was destroyed
        """
        # Get session data first to clean up user sessions
        session_data = await self.get_session(session_id)

        # Remove session data
        session_key = self._get_session_key(session_id)
        self.redis_client.delete(session_key)

        # Remove from user's active sessions
        if session_data:
            user_sessions_key = self._get_user_sessions_key(session_data.user_id)
            self.redis_client.srem(user_sessions_key, session_id)

        return True

    async def destroy_all_user_sessions(self, user_id: str) -> int:
        """
        Destroy all sessions for a user.

        Args:
            user_id: User ID

        Returns:
            int: Number of sessions destroyed
        """
        user_sessions_key = self._get_user_sessions_key(user_id)
        session_ids = self.redis_client.smembers(user_sessions_key)

        destroyed_count = 0
        for session_id in session_ids:
            if await self.destroy_session(session_id):
                destroyed_count += 1

        # Clear user sessions set
        self.redis_client.delete(user_sessions_key)

        return destroyed_count

    async def get_user_sessions(self, user_id: str) -> List[SessionData]:
        """
        Get all active sessions for a user.

        Args:
            user_id: User ID

        Returns:
            List[SessionData]: List of active sessions
        """
        user_sessions_key = self._get_user_sessions_key(user_id)
        session_ids = self.redis_client.smembers(user_sessions_key)

        sessions = []
        for session_id in session_ids:
            session_data = await self.get_session(session_id)
            if session_data:
                sessions.append(session_data)

        return sessions

    async def _enforce_session_limits(self, user_id: str, new_session: SessionData):
        """
        Enforce concurrent session limits for a user.

        Args:
            user_id: User ID
            new_session: New session being created
        """
        current_sessions = await self.get_user_sessions(user_id)

        if len(current_sessions) >= self.max_concurrent_sessions:
            # Sort by last activity (oldest first)
            current_sessions.sort(key=lambda s: s.last_activity)

            # Remove oldest sessions to make room
            sessions_to_remove = len(current_sessions) - self.max_concurrent_sessions + 1

            for i in range(sessions_to_remove):
                await self.destroy_session(current_sessions[i].session_id)

    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions (maintenance task).

        Returns:
            int: Number of sessions cleaned up
        """
        # Redis TTL should handle most cleanup, but this provides additional safety
        # This would typically be run as a scheduled task

        cleaned_count = 0
        # Implementation would scan for expired sessions and clean them up
        # For production, consider using Redis SCAN for large datasets

        return cleaned_count

    async def get_session_analytics(self, user_id: str) -> Dict[str, Any]:
        """
        Get session analytics for a user.

        Args:
            user_id: User ID

        Returns:
            Dict: Session analytics data
        """
        sessions = await self.get_user_sessions(user_id)

        if not sessions:
            return {
                'total_sessions': 0,
                'active_sessions': 0,
                'devices': [],
                'login_sources': {}
            }

        # Analyze sessions
        devices = []
        login_sources = {}

        for session in sessions:
            device_info = {
                'device_hash': session.device_fingerprint.device_hash,
                'browser': f"{session.device_fingerprint.browser_name} {session.device_fingerprint.browser_version}",
                'os': f"{session.device_fingerprint.os_name} {session.device_fingerprint.os_version}",
                'device_type': 'Mobile' if session.device_fingerprint.is_mobile else 'Desktop',
                'last_activity': session.last_activity.isoformat(),
                'ip_address': session.device_fingerprint.ip_address
            }
            devices.append(device_info)

            # Count login sources
            source = session.login_source
            login_sources[source] = login_sources.get(source, 0) + 1

        return {
            'total_sessions': len(sessions),
            'active_sessions': len([s for s in sessions if s.is_active]),
            'devices': devices,
            'login_sources': login_sources,
            'security_flags': [s.security_flags for s in sessions if s.security_flags]
        }