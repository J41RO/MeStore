# ~/app/services/jwt_blacklist_service.py
# ---------------------------------------------------------------------------------------------
# MeStore - JWT Token Blacklisting Service
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: jwt_blacklist_service.py
# Ruta: ~/app/services/jwt_blacklist_service.py
# Autor: Security Backend AI
# Fecha de Creación: 2025-09-17
# Última Actualización: 2025-09-17
# Versión: 1.0.0
# Propósito: Enterprise-grade JWT token blacklisting and security management
#            Provides secure token revocation, session management, and audit trails
#
# ---------------------------------------------------------------------------------------------

"""
JWT Token Blacklisting Service for MeStore.

This service provides enterprise-grade JWT token blacklisting capabilities:
- Secure token revocation and blacklisting
- User session management and cleanup
- Token audit trails and security monitoring
- Redis-based high-performance storage
- Automatic cleanup and garbage collection
"""

import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict
from enum import Enum

import structlog
from app.core.redis.base import get_redis_client
from app.core.config import settings

logger = structlog.get_logger(__name__)


class BlacklistReason(Enum):
    """Reasons for token blacklisting."""
    USER_LOGOUT = "user_logout"
    ADMIN_REVOCATION = "admin_revocation"
    SECURITY_BREACH = "security_breach"
    PASSWORD_CHANGE = "password_change"
    ACCOUNT_SUSPENDED = "account_suspended"
    TOKEN_ROTATION = "token_rotation"
    DEVICE_COMPROMISED = "device_compromised"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"


@dataclass
class BlacklistEntry:
    """Token blacklist entry with metadata."""
    token_jti: str
    user_id: str
    reason: BlacklistReason
    blacklisted_at: datetime
    expires_at: datetime
    device_fingerprint: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    admin_id: Optional[str] = None
    notes: Optional[str] = None


class JWTBlacklistService:
    """
    Enterprise-grade JWT token blacklisting service.

    Provides comprehensive token revocation, session management, and security
    monitoring capabilities with Redis-based high-performance storage.
    """

    def __init__(self):
        self.redis_prefix = "jwt_blacklist"
        self.session_prefix = "user_sessions"
        self.audit_prefix = "blacklist_audit"

    async def blacklist_token(
        self,
        token_jti: str,
        user_id: str,
        reason: BlacklistReason,
        expires_at: Optional[datetime] = None,
        device_fingerprint: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        admin_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> bool:
        """
        Blacklist a JWT token with comprehensive metadata.

        Args:
            token_jti: JWT ID (jti claim) of the token to blacklist
            user_id: ID of the user who owns the token
            reason: Reason for blacklisting
            expires_at: When the blacklist entry should expire
            device_fingerprint: Device fingerprint associated with token
            ip_address: IP address where token was revoked
            user_agent: User agent of the client
            admin_id: ID of admin who revoked the token (if applicable)
            notes: Additional notes about the blacklisting

        Returns:
            bool: True if successfully blacklisted

        Example:
            >>> service = JWTBlacklistService()
            >>> await service.blacklist_token(
            ...     "token123", "user456", BlacklistReason.USER_LOGOUT
            ... )
            True
        """
        try:
            redis_client = await get_redis_client()

            # Create blacklist entry
            entry = BlacklistEntry(
                token_jti=token_jti,
                user_id=user_id,
                reason=reason,
                blacklisted_at=datetime.now(timezone.utc),
                expires_at=expires_at or (
                    datetime.now(timezone.utc) +
                    timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
                ),
                device_fingerprint=device_fingerprint,
                ip_address=ip_address,
                user_agent=user_agent,
                admin_id=admin_id,
                notes=notes
            )

            # Store in Redis with expiration
            blacklist_key = f"{self.redis_prefix}:{token_jti}"
            entry_data = json.dumps(asdict(entry), default=str)

            # Calculate TTL in seconds
            ttl = int((entry.expires_at - datetime.now(timezone.utc)).total_seconds())
            if ttl <= 0:
                ttl = 60  # Minimum 1 minute TTL

            await redis_client.setex(blacklist_key, ttl, entry_data)

            # Update user session tracking
            await self._update_user_session_tracking(user_id, token_jti, "blacklisted")

            # Log audit event
            await self._log_blacklist_event(entry)

            logger.info(
                "Token successfully blacklisted",
                token_jti=token_jti,
                user_id=user_id,
                reason=reason.value,
                expires_at=entry.expires_at.isoformat(),
                ttl=ttl
            )

            return True

        except Exception as e:
            logger.error(
                "Failed to blacklist token",
                error=str(e),
                token_jti=token_jti,
                user_id=user_id,
                reason=reason.value
            )
            return False

    async def is_token_blacklisted(self, token_jti: str) -> bool:
        """
        Check if a token is blacklisted.

        Args:
            token_jti: JWT ID (jti claim) to check

        Returns:
            bool: True if token is blacklisted

        Example:
            >>> service = JWTBlacklistService()
            >>> await service.is_token_blacklisted("token123")
            False
        """
        try:
            redis_client = await get_redis_client()
            blacklist_key = f"{self.redis_prefix}:{token_jti}"

            result = await redis_client.get(blacklist_key)
            is_blacklisted = result is not None

            if is_blacklisted:
                logger.debug(
                    "Token found in blacklist",
                    token_jti=token_jti
                )

            return is_blacklisted

        except Exception as e:
            logger.error(
                "Failed to check token blacklist",
                error=str(e),
                token_jti=token_jti
            )
            # Fail secure: if we can't check blacklist, assume token is valid
            # This prevents Redis outages from breaking authentication entirely
            return False

    async def get_blacklist_entry(self, token_jti: str) -> Optional[BlacklistEntry]:
        """
        Get detailed blacklist entry information.

        Args:
            token_jti: JWT ID to get information for

        Returns:
            BlacklistEntry: Blacklist entry if found, None otherwise
        """
        try:
            redis_client = await get_redis_client()
            blacklist_key = f"{self.redis_prefix}:{token_jti}"

            entry_data = await redis_client.get(blacklist_key)
            if not entry_data:
                return None

            entry_dict = json.loads(entry_data)

            # Convert datetime strings back to datetime objects
            entry_dict['blacklisted_at'] = datetime.fromisoformat(entry_dict['blacklisted_at'])
            entry_dict['expires_at'] = datetime.fromisoformat(entry_dict['expires_at'])
            entry_dict['reason'] = BlacklistReason(entry_dict['reason'])

            return BlacklistEntry(**entry_dict)

        except Exception as e:
            logger.error(
                "Failed to get blacklist entry",
                error=str(e),
                token_jti=token_jti
            )
            return None

    async def blacklist_user_tokens(
        self,
        user_id: str,
        reason: BlacklistReason,
        admin_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> int:
        """
        Blacklist all active tokens for a specific user.

        Args:
            user_id: User identifier
            reason: Reason for blacklisting all tokens
            admin_id: ID of admin performing the action
            notes: Additional notes

        Returns:
            int: Number of tokens blacklisted

        Example:
            >>> service = JWTBlacklistService()
            >>> count = await service.blacklist_user_tokens(
            ...     "user123", BlacklistReason.SECURITY_BREACH
            ... )
            >>> print(f"Blacklisted {count} tokens")
        """
        try:
            redis_client = await get_redis_client()

            # Find all active sessions for this user
            session_pattern = f"{self.session_prefix}:{user_id}:*"
            session_keys = await redis_client.keys(session_pattern)

            blacklisted_count = 0

            for session_key in session_keys:
                session_data = await redis_client.get(session_key)
                if session_data:
                    try:
                        session_info = json.loads(session_data)
                        token_jti = session_info.get("token_jti")

                        if token_jti:
                            success = await self.blacklist_token(
                                token_jti=token_jti,
                                user_id=user_id,
                                reason=reason,
                                device_fingerprint=session_info.get("device_fingerprint"),
                                ip_address=session_info.get("ip_address"),
                                user_agent=session_info.get("user_agent"),
                                admin_id=admin_id,
                                notes=notes
                            )

                            if success:
                                blacklisted_count += 1

                    except json.JSONDecodeError:
                        logger.warning(
                            "Invalid session data format",
                            session_key=session_key
                        )

            logger.info(
                "User tokens blacklisted",
                user_id=user_id,
                count=blacklisted_count,
                reason=reason.value
            )

            return blacklisted_count

        except Exception as e:
            logger.error(
                "Failed to blacklist user tokens",
                error=str(e),
                user_id=user_id,
                reason=reason.value
            )
            return 0

    async def cleanup_expired_blacklist_entries(self) -> int:
        """
        Clean up expired blacklist entries from Redis.

        Returns:
            int: Number of entries cleaned up
        """
        try:
            redis_client = await get_redis_client()

            # Get all blacklist keys
            blacklist_pattern = f"{self.redis_prefix}:*"
            blacklist_keys = await redis_client.keys(blacklist_pattern)

            cleaned_count = 0
            current_time = datetime.now(timezone.utc)

            for key in blacklist_keys:
                entry_data = await redis_client.get(key)
                if entry_data:
                    try:
                        entry_dict = json.loads(entry_data)
                        expires_at = datetime.fromisoformat(entry_dict['expires_at'])

                        if expires_at <= current_time:
                            await redis_client.delete(key)
                            cleaned_count += 1

                    except (json.JSONDecodeError, KeyError, ValueError):
                        # If we can't parse the entry, delete it
                        await redis_client.delete(key)
                        cleaned_count += 1

            if cleaned_count > 0:
                logger.info(
                    "Cleaned up expired blacklist entries",
                    count=cleaned_count
                )

            return cleaned_count

        except Exception as e:
            logger.error(
                "Failed to cleanup blacklist entries",
                error=str(e)
            )
            return 0

    async def get_user_blacklisted_tokens(self, user_id: str) -> List[BlacklistEntry]:
        """
        Get all blacklisted tokens for a specific user.

        Args:
            user_id: User identifier

        Returns:
            List[BlacklistEntry]: List of blacklist entries for the user
        """
        try:
            redis_client = await get_redis_client()

            # Get all blacklist keys
            blacklist_pattern = f"{self.redis_prefix}:*"
            blacklist_keys = await redis_client.keys(blacklist_pattern)

            user_entries = []

            for key in blacklist_keys:
                entry_data = await redis_client.get(key)
                if entry_data:
                    try:
                        entry_dict = json.loads(entry_data)
                        if entry_dict.get('user_id') == user_id:
                            # Convert to BlacklistEntry object
                            entry_dict['blacklisted_at'] = datetime.fromisoformat(entry_dict['blacklisted_at'])
                            entry_dict['expires_at'] = datetime.fromisoformat(entry_dict['expires_at'])
                            entry_dict['reason'] = BlacklistReason(entry_dict['reason'])

                            user_entries.append(BlacklistEntry(**entry_dict))

                    except (json.JSONDecodeError, KeyError, ValueError) as e:
                        logger.warning(
                            "Invalid blacklist entry format",
                            key=key,
                            error=str(e)
                        )

            return user_entries

        except Exception as e:
            logger.error(
                "Failed to get user blacklisted tokens",
                error=str(e),
                user_id=user_id
            )
            return []

    async def get_blacklist_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive blacklist statistics.

        Returns:
            Dict[str, Any]: Statistics about blacklisted tokens
        """
        try:
            redis_client = await get_redis_client()

            # Get all blacklist keys
            blacklist_pattern = f"{self.redis_prefix}:*"
            blacklist_keys = await redis_client.keys(blacklist_pattern)

            stats = {
                "total_blacklisted": len(blacklist_keys),
                "by_reason": {},
                "by_user": {},
                "recent_24h": 0,
                "expires_soon": 0  # Expires within 1 hour
            }

            current_time = datetime.now(timezone.utc)
            twenty_four_hours_ago = current_time - timedelta(hours=24)
            one_hour_from_now = current_time + timedelta(hours=1)

            for key in blacklist_keys:
                entry_data = await redis_client.get(key)
                if entry_data:
                    try:
                        entry_dict = json.loads(entry_data)

                        # Count by reason
                        reason = entry_dict.get('reason', 'unknown')
                        stats["by_reason"][reason] = stats["by_reason"].get(reason, 0) + 1

                        # Count by user
                        user_id = entry_dict.get('user_id', 'unknown')
                        stats["by_user"][user_id] = stats["by_user"].get(user_id, 0) + 1

                        # Count recent blacklistings
                        blacklisted_at = datetime.fromisoformat(entry_dict['blacklisted_at'])
                        if blacklisted_at >= twenty_four_hours_ago:
                            stats["recent_24h"] += 1

                        # Count expiring soon
                        expires_at = datetime.fromisoformat(entry_dict['expires_at'])
                        if expires_at <= one_hour_from_now:
                            stats["expires_soon"] += 1

                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue

            return stats

        except Exception as e:
            logger.error(
                "Failed to get blacklist statistics",
                error=str(e)
            )
            return {"error": str(e)}

    async def _update_user_session_tracking(
        self,
        user_id: str,
        token_jti: str,
        status: str
    ) -> None:
        """Update user session tracking information."""
        try:
            redis_client = await get_redis_client()
            session_key = f"{self.session_prefix}:{user_id}:{token_jti}"

            session_data = await redis_client.get(session_key)
            if session_data:
                session_info = json.loads(session_data)
                session_info["status"] = status
                session_info["updated_at"] = datetime.now(timezone.utc).isoformat()

                await redis_client.setex(
                    session_key,
                    settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                    json.dumps(session_info)
                )

        except Exception as e:
            logger.warning(
                "Failed to update session tracking",
                error=str(e),
                user_id=user_id,
                token_jti=token_jti
            )

    async def _log_blacklist_event(self, entry: BlacklistEntry) -> None:
        """Log blacklist event for audit purposes."""
        try:
            redis_client = await get_redis_client()

            audit_event = {
                "event_type": "token_blacklisted",
                "token_jti": entry.token_jti,
                "user_id": entry.user_id,
                "reason": entry.reason.value,
                "timestamp": entry.blacklisted_at.isoformat(),
                "device_fingerprint": entry.device_fingerprint,
                "ip_address": entry.ip_address,
                "admin_id": entry.admin_id,
                "notes": entry.notes
            }

            # Store audit event with 90-day retention
            audit_key = f"{self.audit_prefix}:{entry.blacklisted_at.strftime('%Y%m%d')}:{entry.token_jti}"
            await redis_client.setex(
                audit_key,
                90 * 24 * 60 * 60,  # 90 days
                json.dumps(audit_event)
            )

        except Exception as e:
            logger.warning(
                "Failed to log blacklist audit event",
                error=str(e),
                token_jti=entry.token_jti
            )


# Global service instance
jwt_blacklist_service = JWTBlacklistService()


# Convenience functions for easier usage
async def blacklist_token(
    token_jti: str,
    user_id: str,
    reason: BlacklistReason,
    **kwargs
) -> bool:
    """Convenience function to blacklist a token."""
    return await jwt_blacklist_service.blacklist_token(
        token_jti, user_id, reason, **kwargs
    )


async def is_token_blacklisted(token_jti: str) -> bool:
    """Convenience function to check if token is blacklisted."""
    return await jwt_blacklist_service.is_token_blacklisted(token_jti)


async def blacklist_user_tokens(
    user_id: str,
    reason: BlacklistReason,
    **kwargs
) -> int:
    """Convenience function to blacklist all user tokens."""
    return await jwt_blacklist_service.blacklist_user_tokens(
        user_id, reason, **kwargs
    )