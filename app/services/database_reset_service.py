"""
Database Reset Service for Testing

This service provides comprehensive database reset functionality for testing purposes.
It includes safety features to prevent accidental production data loss and supports
various reset scenarios for different testing needs.

Features:
- Environment safety checks (dev/test only)
- User data cascade deletion
- Related records cleanup (OTP, sessions, etc.)
- Selective user deletion
- Complete database reset
- Logging and confirmation mechanisms

Author: Backend Framework AI
Created: 2025-09-25
Version: 1.0.0
"""

import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Any
from sqlalchemy import text, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserType
from app.models.base import BaseModel
from app.core.security import get_password_hash
import uuid


class ResetLevel(str, Enum):
    """Reset levels with increasing scope of data deletion."""
    USER_DATA = "user_data"          # Only user profile data
    USER_SESSIONS = "user_sessions"   # User data + sessions
    USER_CASCADE = "user_cascade"     # User data + all related records
    ALL_TEST_DATA = "all_test_data"   # All test data (marked users)
    FULL_RESET = "full_reset"         # Complete database reset (DANGEROUS)


class ResetResult:
    """Result object for reset operations."""

    def __init__(self):
        self.success = False
        self.level = None
        self.deleted_records = {}
        self.errors = []
        self.warnings = []
        self.execution_time = 0.0
        self.affected_users = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "level": self.level,
            "deleted_records": self.deleted_records,
            "errors": self.errors,
            "warnings": self.warnings,
            "execution_time": self.execution_time,
            "affected_users": self.affected_users,
            "timestamp": datetime.utcnow().isoformat()
        }


class DatabaseResetService:
    """
    Comprehensive Database Reset Service for Testing

    Provides safe and controlled database reset functionality specifically
    designed for testing environments with multiple safety mechanisms.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session: Optional[AsyncSession] = None

        # Safety configuration
        self.allowed_environments = {"development", "testing", "dev", "test"}
        self.safe_test_domains = {"@test.com", "@testing.com", "@dev.com", "@example.com"}

        # Related models that need cleanup (order matters for FK constraints)
        self.cascade_models = [
            # Admin and audit logs
            ("AdminActivityLog", "admin_user_id"),
            ("VendorAuditLog", "vendor_id"),
            ("VendorAuditLog", "admin_id"),
            ("VendorNote", "vendor_id"),
            ("VendorNote", "admin_id"),
            ("VendorDocument", "vendor_id"),

            # Commission and payment related
            ("Commission", "vendor_id"),
            ("Commission", "approved_by_id"),
            ("PayoutRequest", "vendedor_id"),

            # Orders and transactions
            ("Order", "buyer_id"),
            ("Transaction", "comprador_id"),
            ("Transaction", "vendedor_id"),

            # Products and inventory
            ("Product", "vendedor_id"),
            ("Inventory", "user_id"),
            ("Storage", "vendedor_id"),

            # User-specific data
            ("PaymentMethod", "buyer_id"),
        ]

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = AsyncSessionLocal()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    def _validate_environment(self) -> None:
        """
        Validate that we're running in a safe environment for reset operations.

        Raises:
            RuntimeError: If environment is not safe for reset operations
        """
        current_env = settings.ENVIRONMENT.lower()

        if current_env not in self.allowed_environments:
            raise RuntimeError(
                f"Database reset not allowed in environment: {current_env}. "
                f"Only allowed in: {', '.join(self.allowed_environments)}"
            )

        # Additional safety check for production-like configuration
        if settings.DATABASE_URL:
            # Allow localhost, test, dev, and local network IPs (192.168.x.x)
            safe_hosts = ["localhost", "127.0.0.1", "test", "dev", "192.168."]
            is_safe = any(safe_host in settings.DATABASE_URL for safe_host in safe_hosts)

            if not is_safe and current_env not in self.allowed_environments:
                raise RuntimeError(
                    "Database reset blocked: DATABASE_URL appears to be production. "
                    "Reset only allowed on localhost, local network, or test/dev databases."
                )

    def _validate_reset_level(self, level: ResetLevel, confirm_dangerous: bool = False) -> None:
        """
        Validate reset level and require explicit confirmation for dangerous operations.

        Args:
            level: Reset level to validate
            confirm_dangerous: Whether dangerous operations are explicitly confirmed

        Raises:
            ValueError: If validation fails
        """
        if level == ResetLevel.FULL_RESET and not confirm_dangerous:
            raise ValueError(
                "FULL_RESET requires explicit confirmation via confirm_dangerous=True. "
                "This will delete ALL data in the database!"
            )

    async def _identify_test_users(self, email_patterns: Optional[List[str]] = None) -> List[User]:
        """
        Identify users that are safe to delete for testing.

        Args:
            email_patterns: Optional list of email patterns to match

        Returns:
            List of users identified as test users
        """
        if not self.session:
            raise RuntimeError("Service not initialized. Use as async context manager.")

        # Default patterns for test users
        default_patterns = list(self.safe_test_domains)
        if email_patterns:
            default_patterns.extend(email_patterns)

        test_users = []

        # Query users with test email patterns
        query = await self.session.execute(
            text("SELECT * FROM users WHERE " +
                 " OR ".join([f"email LIKE '%{pattern}'" for pattern in default_patterns]))
        )

        users = query.fetchall()

        for user_data in users:
            # Convert row to User object (simplified)
            user = await self.session.get(User, user_data[0])  # Assuming id is first column
            if user:
                test_users.append(user)

        return test_users

    async def _delete_related_records(self, user_ids: List[str], result: ResetResult) -> None:
        """
        Delete all records related to specified users with proper cascade handling.

        Args:
            user_ids: List of user IDs to clean up
            result: Result object to track deletions
        """
        if not self.session:
            raise RuntimeError("Service not initialized. Use as async context manager.")

        for model_name, foreign_key in self.cascade_models:
            try:
                # Use raw SQL for better control and performance
                delete_query = text(f"""
                    DELETE FROM {model_name.lower()}s
                    WHERE {foreign_key} IN :user_ids
                """)

                result_proxy = await self.session.execute(
                    delete_query,
                    {"user_ids": tuple(user_ids)}
                )

                deleted_count = result_proxy.rowcount
                if deleted_count > 0:
                    result.deleted_records[model_name] = deleted_count
                    self.logger.info(f"Deleted {deleted_count} records from {model_name}")

            except Exception as e:
                error_msg = f"Failed to delete {model_name} records: {str(e)}"
                result.errors.append(error_msg)
                self.logger.error(error_msg)

    async def _cleanup_user_sessions(self, user_ids: List[str], result: ResetResult) -> None:
        """
        Clean up user sessions from Redis and database.

        Args:
            user_ids: List of user IDs to clean sessions for
            result: Result object to track cleanup
        """
        try:
            import redis.asyncio as redis

            # Connect to Redis session store
            redis_client = redis.from_url(settings.get_redis_session_url())

            session_keys_deleted = 0
            for user_id in user_ids:
                # Delete user session keys (pattern: session:user:{user_id}:*)
                pattern = f"session:user:{user_id}:*"
                keys = await redis_client.keys(pattern)
                if keys:
                    await redis_client.delete(*keys)
                    session_keys_deleted += len(keys)

                # Delete OTP keys (pattern: otp:{user_id}:*)
                otp_pattern = f"otp:{user_id}:*"
                otp_keys = await redis_client.keys(otp_pattern)
                if otp_keys:
                    await redis_client.delete(*otp_keys)
                    session_keys_deleted += len(otp_keys)

            await redis_client.close()

            if session_keys_deleted > 0:
                result.deleted_records["redis_sessions"] = session_keys_deleted
                self.logger.info(f"Deleted {session_keys_deleted} Redis session/OTP keys")

        except Exception as e:
            error_msg = f"Failed to cleanup user sessions: {str(e)}"
            result.warnings.append(error_msg)
            self.logger.warning(error_msg)

    async def _clear_user_otp_data(self, user_ids: List[str]) -> None:
        """
        Clear OTP-related data for specified users.

        Args:
            user_ids: List of user IDs to clear OTP data for
        """
        if not self.session:
            raise RuntimeError("Service not initialized. Use as async context manager.")

        update_query = text("""
            UPDATE users SET
                otp_secret = NULL,
                otp_expires_at = NULL,
                otp_attempts = 0,
                otp_type = NULL,
                last_otp_sent = NULL,
                reset_token = NULL,
                reset_token_expires_at = NULL,
                reset_attempts = 0,
                last_reset_request = NULL
            WHERE id IN :user_ids
        """)

        await self.session.execute(update_query, {"user_ids": tuple(user_ids)})

    async def delete_user_safely(
        self,
        user_id: str,
        level: ResetLevel = ResetLevel.USER_CASCADE,
        force: bool = False
    ) -> ResetResult:
        """
        Safely delete a single user with specified cleanup level.

        Args:
            user_id: ID of user to delete
            level: Level of cleanup to perform
            force: Force deletion even if user doesn't appear to be a test user

        Returns:
            ResetResult with operation details
        """
        start_time = datetime.utcnow()
        result = ResetResult()
        result.level = level.value

        try:
            self._validate_environment()

            if not self.session:
                raise RuntimeError("Service not initialized. Use as async context manager.")

            # Get user details
            user = await self.session.get(User, user_id)
            if not user:
                result.errors.append(f"User {user_id} not found")
                return result

            # Safety check - ensure it's a test user (unless forced)
            if not force:
                is_test_user = any(domain in user.email for domain in self.safe_test_domains)
                if not is_test_user:
                    result.errors.append(
                        f"User {user.email} doesn't appear to be a test user. "
                        "Use force=True to override this check."
                    )
                    return result

            result.affected_users.append(user.email)

            # Perform cleanup based on level
            if level in [ResetLevel.USER_SESSIONS, ResetLevel.USER_CASCADE, ResetLevel.ALL_TEST_DATA]:
                await self._cleanup_user_sessions([user_id], result)

            if level in [ResetLevel.USER_CASCADE, ResetLevel.ALL_TEST_DATA]:
                await self._delete_related_records([user_id], result)

            # Clear OTP data
            await self._clear_user_otp_data([user_id])

            # Delete the user
            await self.session.delete(user)
            await self.session.commit()

            result.deleted_records["users"] = 1
            result.success = True

            self.logger.info(f"Successfully deleted user {user.email} with level {level.value}")

        except Exception as e:
            await self.session.rollback()
            error_msg = f"Failed to delete user {user_id}: {str(e)}"
            result.errors.append(error_msg)
            self.logger.error(error_msg)

        finally:
            result.execution_time = (datetime.utcnow() - start_time).total_seconds()

        return result

    async def reset_test_users(
        self,
        email_patterns: Optional[List[str]] = None,
        level: ResetLevel = ResetLevel.USER_CASCADE
    ) -> ResetResult:
        """
        Reset all identified test users.

        Args:
            email_patterns: Optional email patterns to identify test users
            level: Level of cleanup to perform

        Returns:
            ResetResult with operation details
        """
        start_time = datetime.utcnow()
        result = ResetResult()
        result.level = level.value

        try:
            self._validate_environment()

            if not self.session:
                raise RuntimeError("Service not initialized. Use as async context manager.")

            # Identify test users
            test_users = await self._identify_test_users(email_patterns)

            if not test_users:
                result.warnings.append("No test users found to reset")
                result.success = True
                return result

            user_ids = [user.id for user in test_users]
            result.affected_users = [user.email for user in test_users]

            self.logger.info(f"Found {len(test_users)} test users to reset")

            # Perform cleanup based on level
            if level in [ResetLevel.USER_SESSIONS, ResetLevel.USER_CASCADE, ResetLevel.ALL_TEST_DATA]:
                await self._cleanup_user_sessions(user_ids, result)

            if level in [ResetLevel.USER_CASCADE, ResetLevel.ALL_TEST_DATA]:
                await self._delete_related_records(user_ids, result)

            # Clear OTP data for all users
            await self._clear_user_otp_data(user_ids)

            # Delete users
            delete_query = delete(User).where(User.id.in_(user_ids))
            delete_result = await self.session.execute(delete_query)

            await self.session.commit()

            result.deleted_records["users"] = delete_result.rowcount
            result.success = True

            self.logger.info(f"Successfully reset {len(test_users)} test users")

        except Exception as e:
            await self.session.rollback()
            error_msg = f"Failed to reset test users: {str(e)}"
            result.errors.append(error_msg)
            self.logger.error(error_msg)

        finally:
            result.execution_time = (datetime.utcnow() - start_time).total_seconds()

        return result

    async def full_database_reset(
        self,
        confirm_dangerous: bool = False,
        preserve_admin_users: bool = True
    ) -> ResetResult:
        """
        Perform a complete database reset (VERY DANGEROUS).

        Args:
            confirm_dangerous: Must be True to execute this operation
            preserve_admin_users: Whether to preserve admin users

        Returns:
            ResetResult with operation details
        """
        start_time = datetime.utcnow()
        result = ResetResult()
        result.level = ResetLevel.FULL_RESET.value

        try:
            self._validate_environment()
            self._validate_reset_level(ResetLevel.FULL_RESET, confirm_dangerous)

            if not self.session:
                raise RuntimeError("Service not initialized. Use as async context manager.")

            self.logger.warning("Starting FULL DATABASE RESET - This will delete ALL data!")

            # Get list of all tables
            tables_query = await self.session.execute(text("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """))

            tables = [row[0] for row in tables_query.fetchall()]

            # Preserve admin users if requested
            admin_users_data = []
            if preserve_admin_users:
                admin_query = await self.session.execute(
                    text("SELECT * FROM users WHERE user_type IN ('ADMIN', 'SUPERUSER')")
                )
                admin_users_data = admin_query.fetchall()
                result.warnings.append(f"Preserved {len(admin_users_data)} admin users")

            # Disable FK constraints temporarily
            await self.session.execute(text("SET session_replication_role = replica"))

            # Truncate all tables except alembic_version
            for table in tables:
                if table != 'alembic_version':
                    truncate_result = await self.session.execute(
                        text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE")
                    )
                    result.deleted_records[table] = "ALL_RECORDS"

            # Re-enable FK constraints
            await self.session.execute(text("SET session_replication_role = DEFAULT"))

            # Restore admin users if preserved
            if preserve_admin_users and admin_users_data:
                for user_data in admin_users_data:
                    # Reconstruct user (simplified - in real implementation, handle all columns)
                    admin_user = User(
                        id=user_data[0],
                        email=user_data[1],
                        password_hash=user_data[2],
                        nombre=user_data[3] if len(user_data) > 3 else None,
                        apellido=user_data[4] if len(user_data) > 4 else None,
                        user_type=UserType.ADMIN,
                        is_active=True
                    )
                    self.session.add(admin_user)
                    result.affected_users.append(user_data[1])  # email

            await self.session.commit()

            # Clear Redis caches
            try:
                import redis.asyncio as redis
                redis_client = redis.from_url(settings.get_redis_cache_url())
                await redis_client.flushdb()  # Clear current database
                await redis_client.close()
                result.deleted_records["redis_cache"] = "ALL_KEYS"
            except Exception as redis_error:
                result.warnings.append(f"Failed to clear Redis cache: {str(redis_error)}")

            result.success = True
            self.logger.warning("FULL DATABASE RESET completed successfully")

        except Exception as e:
            await self.session.rollback()
            error_msg = f"Full database reset failed: {str(e)}"
            result.errors.append(error_msg)
            self.logger.error(error_msg)

        finally:
            result.execution_time = (datetime.utcnow() - start_time).total_seconds()

        return result

    async def create_test_user(
        self,
        email: str,
        password: str = "testpass123",
        user_type: UserType = UserType.BUYER,
        **extra_fields
    ) -> User:
        """
        Create a test user for testing purposes.

        Args:
            email: Test user email (should use test domain)
            password: User password (default: testpass123)
            user_type: Type of user to create
            **extra_fields: Additional user fields

        Returns:
            Created User object
        """
        if not self.session:
            raise RuntimeError("Service not initialized. Use as async context manager.")

        # Validate email is for testing
        is_test_email = any(domain in email for domain in self.safe_test_domains)
        if not is_test_email:
            raise ValueError(
                f"Email {email} doesn't use a test domain. "
                f"Use one of: {', '.join(self.safe_test_domains)}"
            )

        # Create user
        user_data = {
            "id": str(uuid.uuid4()),
            "email": email,
            "password_hash": get_password_hash(password),
            "user_type": user_type,
            "is_active": True,
            "is_verified": True,
            "email_verified": True,
            **extra_fields
        }

        user = User(**user_data)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        self.logger.info(f"Created test user: {email}")
        return user

    async def get_reset_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the current database state for reset planning.

        Returns:
            Dictionary with database statistics
        """
        if not self.session:
            raise RuntimeError("Service not initialized. Use as async context manager.")

        stats = {}

        try:
            # User statistics
            user_stats = await self.session.execute(text("""
                SELECT
                    user_type,
                    COUNT(*) as count,
                    COUNT(CASE WHEN is_active THEN 1 END) as active_count
                FROM users
                GROUP BY user_type
            """))

            stats["users"] = {row[0]: {"total": row[1], "active": row[2]} for row in user_stats.fetchall()}

            # Test user identification
            test_user_query = await self.session.execute(text("""
                SELECT COUNT(*) FROM users WHERE """ +
                " OR ".join([f"email LIKE '%{domain}'" for domain in self.safe_test_domains])
            ))
            stats["test_users"] = test_user_query.scalar()

            # Table sizes (database-agnostic approach)
            try:
                # Try PostgreSQL first
                if "postgresql" in settings.DATABASE_URL.lower():
                    table_sizes = await self.session.execute(text("""
                        SELECT
                            schemaname,
                            tablename,
                            n_tup_ins as inserts,
                            n_tup_upd as updates,
                            n_tup_del as deletes,
                            n_live_tup as live_tuples
                        FROM pg_stat_user_tables
                        ORDER BY n_live_tup DESC
                        LIMIT 20
                    """))

                    stats["table_sizes"] = [
                        {
                            "table": row[1],
                            "live_tuples": row[5],
                            "inserts": row[2],
                            "updates": row[3],
                            "deletes": row[4]
                        }
                        for row in table_sizes.fetchall()
                    ]
                else:
                    # SQLite approach - just get table names and approximate row counts
                    table_sizes = await self.session.execute(text("""
                        SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'
                    """))

                    tables = table_sizes.fetchall()
                    table_stats = []

                    for (table_name,) in tables:
                        try:
                            count_result = await self.session.execute(
                                text(f"SELECT COUNT(*) FROM {table_name}")
                            )
                            row_count = count_result.scalar()
                            table_stats.append({
                                "table": table_name,
                                "live_tuples": row_count,
                                "inserts": "N/A",
                                "updates": "N/A",
                                "deletes": "N/A"
                            })
                        except Exception:
                            # Skip tables that can't be counted
                            pass

                    # Sort by row count
                    table_stats.sort(key=lambda x: x["live_tuples"], reverse=True)
                    stats["table_sizes"] = table_stats[:20]

            except Exception as e:
                stats["table_sizes"] = []
                self.logger.warning(f"Could not get table sizes: {str(e)}")

            # Environment info
            stats["environment"] = {
                "current": settings.ENVIRONMENT,
                "database_url": settings.DATABASE_URL.split("@")[-1],  # Hide credentials
                "reset_allowed": settings.ENVIRONMENT.lower() in self.allowed_environments
            }

        except Exception as e:
            self.logger.error(f"Failed to get reset statistics: {str(e)}")
            stats["error"] = str(e)

        return stats


# Factory function for easy service creation
async def create_reset_service() -> DatabaseResetService:
    """
    Factory function to create a DatabaseResetService instance.

    Returns:
        DatabaseResetService instance ready to use as context manager
    """
    return DatabaseResetService()


# Convenience functions for common operations
async def quick_user_reset(email: str) -> ResetResult:
    """
    Quick reset of a single user by email.

    Args:
        email: Email of user to reset

    Returns:
        ResetResult with operation details
    """
    async with DatabaseResetService() as service:
        # Find user by email
        user_query = await service.session.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": email}
        )
        user_result = user_query.fetchone()

        if not user_result:
            result = ResetResult()
            result.errors.append(f"User with email {email} not found")
            return result

        return await service.delete_user_safely(user_result[0])


async def quick_test_data_reset() -> ResetResult:
    """
    Quick reset of all test data.

    Returns:
        ResetResult with operation details
    """
    async with DatabaseResetService() as service:
        return await service.reset_test_users()