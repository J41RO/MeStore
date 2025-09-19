"""
Enterprise Fraud Detection Service for MeStore.

This module provides comprehensive fraud detection capabilities:
- Login attempt monitoring and anomaly detection
- IP-based risk assessment and geolocation analysis
- Device fingerprinting and behavioral analysis
- Enterprise security patterns for Colombian compliance

Author: Backend Senior Developer
Version: 1.0.0 Enterprise
"""

import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from enum import Enum
from pydantic import BaseModel
from fastapi import Request

from app.core.config import settings
from app.core.security import generate_device_fingerprint
from app.core.logger import get_logger

logger = get_logger(__name__)


class AlertType(str, Enum):
    """Alert type enumeration for fraud detection."""
    FRAUD_DETECTION = "fraud_detection"
    SUSPICIOUS_LOGIN = "suspicious_login"
    IP_ANOMALY = "ip_anomaly"
    DEVICE_ANOMALY = "device_anomaly"


class AlertSeverity(str, Enum):
    """Alert severity enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskLevel(str, Enum):
    """Risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FraudEvent(str, Enum):
    """Fraud event types."""
    LOGIN_FAILURE = "login_failure"
    MULTIPLE_IPS = "multiple_ips"
    SUSPICIOUS_DEVICE = "suspicious_device"
    RAPID_REQUESTS = "rapid_requests"
    GEOGRAPHIC_ANOMALY = "geographic_anomaly"
    CREDENTIAL_STUFFING = "credential_stuffing"


class FraudAlert(BaseModel):
    """Fraud detection alert model."""
    alert_id: str
    user_id: Optional[str]
    event_type: FraudEvent
    risk_level: RiskLevel
    ip_address: str
    device_fingerprint: str
    timestamp: datetime
    details: Dict
    action_taken: str
    expires_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class LoginAttempt(BaseModel):
    """Login attempt tracking model."""
    timestamp: datetime
    ip_address: str
    user_agent: str
    device_fingerprint: str
    success: bool
    user_id: Optional[str] = None


class EnterpriseFraudDetectionService:
    """
    Enterprise-grade fraud detection service.

    Features:
    - Real-time login attempt monitoring
    - IP reputation and geolocation analysis
    - Device fingerprinting and anomaly detection
    - Behavioral pattern analysis
    - Automated response actions
    """

    def __init__(self, redis_client):
        """Initialize fraud detection service with Redis client."""
        self.redis = redis_client
        self.login_attempts_prefix = "fraud:login_attempts:"
        self.ip_reputation_prefix = "fraud:ip_reputation:"
        self.device_reputation_prefix = "fraud:device_reputation:"
        self.user_lockout_prefix = "fraud:user_lockout:"
        self.fraud_alerts_prefix = "fraud:alerts:"

    async def analyze_login_attempt(
        self,
        request: Request,
        email: str,
        success: bool,
        user_id: Optional[str] = None
    ) -> Tuple[RiskLevel, List[FraudAlert]]:
        """
        Analyze a login attempt for fraud indicators.

        Args:
            request: FastAPI request object
            email: User email attempting login
            success: Whether the login was successful
            user_id: User ID if login was successful

        Returns:
            Tuple[RiskLevel, List[FraudAlert]]: Risk level and any fraud alerts
        """
        try:
            ip_address = getattr(request.client, 'host', 'unknown') if request.client else 'unknown'
            user_agent = request.headers.get('User-Agent', 'unknown')
            device_fingerprint = generate_device_fingerprint(request)

            # Record the login attempt
            await self._record_login_attempt(
                ip_address=ip_address,
                user_agent=user_agent,
                device_fingerprint=device_fingerprint,
                email=email,
                success=success,
                user_id=user_id
            )

            alerts = []
            risk_scores = []

            # Check for various fraud indicators
            login_failure_risk, login_alerts = await self._check_login_failures(ip_address, email)
            alerts.extend(login_alerts)
            risk_scores.append(login_failure_risk)

            ip_reputation_risk, ip_alerts = await self._check_ip_reputation(ip_address)
            alerts.extend(ip_alerts)
            risk_scores.append(ip_reputation_risk)

            device_risk, device_alerts = await self._check_device_anomalies(
                device_fingerprint, user_id, ip_address
            )
            alerts.extend(device_alerts)
            risk_scores.append(device_risk)

            rate_limit_risk, rate_alerts = await self._check_rate_limiting(ip_address, email)
            alerts.extend(rate_alerts)
            risk_scores.append(rate_limit_risk)

            # Calculate overall risk level
            overall_risk = self._calculate_overall_risk(risk_scores)

            # Take automated actions based on risk level
            await self._take_automated_actions(overall_risk, ip_address, email, user_id)

            # Log the analysis
            logger.info(
                "Fraud analysis completed",
                email=email,
                ip_address=ip_address,
                device_fingerprint=device_fingerprint[:8],
                risk_level=overall_risk.value,
                alerts_count=len(alerts),
                success=success
            )

            return overall_risk, alerts

        except Exception as e:
            logger.critical("Critical fraud detection failure - SECURITY ALERT", error=str(e), email=email)
            # SECURITY FIX: Fail-secure behavior - treat system failure as HIGH RISK
            # This prevents fraud detection bypass when service fails
            critical_alert = FraudAlert(
                alert_type=AlertType.FRAUD_DETECTION,
                severity=AlertSeverity.CRITICAL,
                message=f"Fraud detection system failure for {email}",
                details={"error": str(e), "email": email, "timestamp": datetime.now().isoformat()},
                recommended_action="BLOCK ACCESS - System failure detected"
            )
            return RiskLevel.HIGH, [critical_alert]

    async def check_user_lockout_status(self, email: str) -> Tuple[bool, Optional[datetime]]:
        """
        Check if a user is currently locked out due to fraud detection.

        Args:
            email: User email to check

        Returns:
            Tuple[bool, Optional[datetime]]: Is locked out and expiration time
        """
        try:
            lockout_key = f"{self.user_lockout_prefix}{email}"
            lockout_data = await self.redis.get(lockout_key)

            if not lockout_data:
                return False, None

            data = json.loads(lockout_data)
            expires_at = datetime.fromisoformat(data['expires_at'].replace('Z', '+00:00'))

            if datetime.now(timezone.utc) > expires_at:
                # Lockout expired, clean up
                await self.redis.delete(lockout_key)
                return False, None

            return True, expires_at

        except Exception as e:
            logger.critical("Critical error checking user lockout status", error=str(e), email=email)
            # SECURITY FIX: Fail-secure - assume user is locked when system fails
            return True, datetime.now() + timedelta(minutes=30)

    async def _record_login_attempt(
        self,
        ip_address: str,
        user_agent: str,
        device_fingerprint: str,
        email: str,
        success: bool,
        user_id: Optional[str] = None
    ) -> None:
        """Record a login attempt for analysis."""
        try:
            attempt = LoginAttempt(
                timestamp=datetime.now(timezone.utc),
                ip_address=ip_address,
                user_agent=user_agent,
                device_fingerprint=device_fingerprint,
                success=success,
                user_id=user_id
            )

            # Store attempts by IP and by email
            ip_key = f"{self.login_attempts_prefix}ip:{ip_address}"
            email_key = f"{self.login_attempts_prefix}email:{email}"

            attempt_data = json.dumps(attempt.dict(), default=str)

            # Use Redis lists to store recent attempts (keep last 100)
            await self.redis.lpush(ip_key, attempt_data)
            await self.redis.ltrim(ip_key, 0, 99)  # Keep only last 100
            await self.redis.expire(ip_key, 86400)  # 24 hours

            await self.redis.lpush(email_key, attempt_data)
            await self.redis.ltrim(email_key, 0, 99)  # Keep only last 100
            await self.redis.expire(email_key, 86400)  # 24 hours

        except Exception as e:
            logger.error("Error recording login attempt", error=str(e))

    async def _check_login_failures(self, ip_address: str, email: str) -> Tuple[RiskLevel, List[FraudAlert]]:
        """Check for excessive login failures."""
        alerts = []
        risk_level = RiskLevel.LOW

        try:
            # Check failures by IP
            ip_key = f"{self.login_attempts_prefix}ip:{ip_address}"
            ip_attempts = await self.redis.lrange(ip_key, 0, 50)  # Check last 50

            ip_failures = []
            for attempt_data in ip_attempts:
                if isinstance(attempt_data, bytes):
                    attempt_data = attempt_data.decode('utf-8')

                attempt = json.loads(attempt_data)
                if not attempt['success']:
                    attempt_time = datetime.fromisoformat(attempt['timestamp'].replace('Z', '+00:00'))
                    if datetime.now(timezone.utc) - attempt_time < timedelta(hours=1):
                        ip_failures.append(attempt)

            # Check failures by email
            email_key = f"{self.login_attempts_prefix}email:{email}"
            email_attempts = await self.redis.lrange(email_key, 0, 50)

            email_failures = []
            for attempt_data in email_attempts:
                if isinstance(attempt_data, bytes):
                    attempt_data = attempt_data.decode('utf-8')

                attempt = json.loads(attempt_data)
                if not attempt['success']:
                    attempt_time = datetime.fromisoformat(attempt['timestamp'].replace('Z', '+00:00'))
                    if datetime.now(timezone.utc) - attempt_time < timedelta(hours=1):
                        email_failures.append(attempt)

            # Assess risk based on failure counts
            if len(ip_failures) >= settings.FRAUD_DETECTION_MAX_LOGIN_FAILURES:
                risk_level = RiskLevel.HIGH
                alerts.append(await self._create_fraud_alert(
                    event_type=FraudEvent.LOGIN_FAILURE,
                    risk_level=RiskLevel.HIGH,
                    ip_address=ip_address,
                    details={
                        "ip_failures_count": len(ip_failures),
                        "time_window": "1 hour"
                    }
                ))

            elif len(email_failures) >= settings.FRAUD_DETECTION_MAX_LOGIN_FAILURES:
                risk_level = RiskLevel.MEDIUM
                alerts.append(await self._create_fraud_alert(
                    event_type=FraudEvent.LOGIN_FAILURE,
                    risk_level=RiskLevel.MEDIUM,
                    ip_address=ip_address,
                    details={
                        "email_failures_count": len(email_failures),
                        "time_window": "1 hour"
                    }
                ))

        except Exception as e:
            logger.error("Error checking login failures", error=str(e))

        return risk_level, alerts

    async def _check_ip_reputation(self, ip_address: str) -> Tuple[RiskLevel, List[FraudAlert]]:
        """Check IP address reputation."""
        alerts = []
        risk_level = RiskLevel.LOW

        try:
            reputation_key = f"{self.ip_reputation_prefix}{ip_address}"
            reputation_data = await self.redis.get(reputation_key)

            if reputation_data:
                reputation = json.loads(reputation_data)
                score = reputation.get('risk_score', 0)

                if score >= 80:
                    risk_level = RiskLevel.CRITICAL
                elif score >= 60:
                    risk_level = RiskLevel.HIGH
                elif score >= 40:
                    risk_level = RiskLevel.MEDIUM

                if risk_level != RiskLevel.LOW:
                    alerts.append(await self._create_fraud_alert(
                        event_type=FraudEvent.SUSPICIOUS_DEVICE,
                        risk_level=risk_level,
                        ip_address=ip_address,
                        details=reputation
                    ))
            else:
                # New IP, assign initial neutral reputation
                await self._initialize_ip_reputation(ip_address)

        except Exception as e:
            logger.error("Error checking IP reputation", error=str(e))

        return risk_level, alerts

    async def _check_device_anomalies(
        self,
        device_fingerprint: str,
        user_id: Optional[str],
        ip_address: str
    ) -> Tuple[RiskLevel, List[FraudAlert]]:
        """Check for device-related anomalies."""
        alerts = []
        risk_level = RiskLevel.LOW

        try:
            device_key = f"{self.device_reputation_prefix}{device_fingerprint}"
            device_data = await self.redis.get(device_key)

            if device_data:
                device_info = json.loads(device_data)

                # Check for device used by multiple users
                if user_id and len(device_info.get('user_ids', [])) > 3:
                    risk_level = RiskLevel.MEDIUM
                    alerts.append(await self._create_fraud_alert(
                        event_type=FraudEvent.SUSPICIOUS_DEVICE,
                        risk_level=RiskLevel.MEDIUM,
                        ip_address=ip_address,
                        details={
                            "device_fingerprint": device_fingerprint[:8],
                            "user_count": len(device_info.get('user_ids', []))
                        }
                    ))

                # Check for device used from multiple IPs rapidly
                recent_ips = device_info.get('recent_ips', [])
                if len(recent_ips) > 5:  # More than 5 IPs in recent history
                    risk_level = max(risk_level, RiskLevel.MEDIUM)
                    alerts.append(await self._create_fraud_alert(
                        event_type=FraudEvent.MULTIPLE_IPS,
                        risk_level=RiskLevel.MEDIUM,
                        ip_address=ip_address,
                        details={
                            "device_fingerprint": device_fingerprint[:8],
                            "ip_count": len(recent_ips)
                        }
                    ))
            else:
                # New device, initialize tracking
                await self._initialize_device_tracking(device_fingerprint, user_id, ip_address)

        except Exception as e:
            logger.error("Error checking device anomalies", error=str(e))

        return risk_level, alerts

    async def _check_rate_limiting(self, ip_address: str, email: str) -> Tuple[RiskLevel, List[FraudAlert]]:
        """Check for rate limiting violations."""
        alerts = []
        risk_level = RiskLevel.LOW

        try:
            # Count recent attempts from IP
            ip_key = f"{self.login_attempts_prefix}ip:{ip_address}"
            recent_attempts = await self.redis.lrange(ip_key, 0, 20)  # Check last 20

            recent_count = 0
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=5)

            for attempt_data in recent_attempts:
                if isinstance(attempt_data, bytes):
                    attempt_data = attempt_data.decode('utf-8')

                attempt = json.loads(attempt_data)
                attempt_time = datetime.fromisoformat(attempt['timestamp'].replace('Z', '+00:00'))

                if attempt_time > cutoff_time:
                    recent_count += 1

            # Check if rate limit exceeded
            if recent_count > 10:  # More than 10 attempts in 5 minutes
                risk_level = RiskLevel.HIGH
                alerts.append(await self._create_fraud_alert(
                    event_type=FraudEvent.RAPID_REQUESTS,
                    risk_level=RiskLevel.HIGH,
                    ip_address=ip_address,
                    details={
                        "request_count": recent_count,
                        "time_window": "5 minutes"
                    }
                ))

        except Exception as e:
            logger.error("Error checking rate limiting", error=str(e))

        return risk_level, alerts

    def _calculate_overall_risk(self, risk_scores: List[RiskLevel]) -> RiskLevel:
        """Calculate overall risk level from multiple risk scores."""
        risk_values = {
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.HIGH: 3,
            RiskLevel.CRITICAL: 4
        }

        if not risk_scores:
            return RiskLevel.LOW

        max_risk = max(risk_values[risk] for risk in risk_scores)
        avg_risk = sum(risk_values[risk] for risk in risk_scores) / len(risk_scores)

        # Use weighted calculation (70% max, 30% average)
        overall_score = (max_risk * 0.7) + (avg_risk * 0.3)

        if overall_score >= 3.5:
            return RiskLevel.CRITICAL
        elif overall_score >= 2.5:
            return RiskLevel.HIGH
        elif overall_score >= 1.5:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    async def _take_automated_actions(
        self,
        risk_level: RiskLevel,
        ip_address: str,
        email: str,
        user_id: Optional[str]
    ) -> None:
        """Take automated actions based on risk level."""
        try:
            if risk_level == RiskLevel.CRITICAL:
                # Lock user account temporarily
                await self._lockout_user(email, minutes=60)
                logger.warning(
                    "User locked due to critical fraud risk",
                    email=email,
                    ip_address=ip_address,
                    lockout_minutes=60
                )

            elif risk_level == RiskLevel.HIGH:
                # Shorter lockout
                await self._lockout_user(email, minutes=settings.FRAUD_DETECTION_LOCKOUT_MINUTES)
                logger.warning(
                    "User locked due to high fraud risk",
                    email=email,
                    ip_address=ip_address,
                    lockout_minutes=settings.FRAUD_DETECTION_LOCKOUT_MINUTES
                )

        except Exception as e:
            logger.error("Error taking automated actions", error=str(e))

    async def _lockout_user(self, email: str, minutes: int) -> None:
        """Lock out a user for specified minutes."""
        try:
            lockout_key = f"{self.user_lockout_prefix}{email}"
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=minutes)

            lockout_data = {
                "email": email,
                "locked_at": datetime.now(timezone.utc).isoformat(),
                "expires_at": expires_at.isoformat(),
                "reason": "fraud_detection"
            }

            await self.redis.setex(
                lockout_key,
                minutes * 60,
                json.dumps(lockout_data, default=str)
            )

        except Exception as e:
            logger.error("Error locking user", error=str(e), email=email)

    async def _create_fraud_alert(
        self,
        event_type: FraudEvent,
        risk_level: RiskLevel,
        ip_address: str,
        details: Dict,
        user_id: Optional[str] = None
    ) -> FraudAlert:
        """Create and store a fraud alert."""
        try:
            alert = FraudAlert(
                alert_id=f"fraud_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{event_type.value}",
                user_id=user_id,
                event_type=event_type,
                risk_level=risk_level,
                ip_address=ip_address,
                device_fingerprint="",  # Will be set by caller
                timestamp=datetime.now(timezone.utc),
                details=details,
                action_taken="monitoring",
                expires_at=datetime.now(timezone.utc) + timedelta(days=7)
            )

            # Store alert in Redis
            alert_key = f"{self.fraud_alerts_prefix}{alert.alert_id}"
            await self.redis.setex(
                alert_key,
                7 * 24 * 3600,  # 7 days
                json.dumps(alert.dict(), default=str)
            )

            return alert

        except Exception as e:
            logger.error("Error creating fraud alert", error=str(e))
            raise

    async def _initialize_ip_reputation(self, ip_address: str) -> None:
        """Initialize reputation tracking for new IP."""
        try:
            reputation_key = f"{self.ip_reputation_prefix}{ip_address}"
            reputation_data = {
                "ip_address": ip_address,
                "first_seen": datetime.now(timezone.utc).isoformat(),
                "risk_score": 20,  # Neutral score for new IPs
                "login_attempts": 0,
                "successful_logins": 0,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }

            await self.redis.setex(
                reputation_key,
                30 * 24 * 3600,  # 30 days
                json.dumps(reputation_data, default=str)
            )

        except Exception as e:
            logger.error("Error initializing IP reputation", error=str(e))

    async def _initialize_device_tracking(
        self,
        device_fingerprint: str,
        user_id: Optional[str],
        ip_address: str
    ) -> None:
        """Initialize tracking for new device."""
        try:
            device_key = f"{self.device_reputation_prefix}{device_fingerprint}"
            device_data = {
                "device_fingerprint": device_fingerprint,
                "first_seen": datetime.now(timezone.utc).isoformat(),
                "user_ids": [user_id] if user_id else [],
                "recent_ips": [ip_address],
                "last_updated": datetime.now(timezone.utc).isoformat()
            }

            await self.redis.setex(
                device_key,
                30 * 24 * 3600,  # 30 days
                json.dumps(device_data, default=str)
            )

        except Exception as e:
            logger.error("Error initializing device tracking", error=str(e))
# Factory function for service creation
def get_fraud_detection_service(redis_client=None):
    """Get fraud detection service instance."""
    return EnterpriseFraudDetectionService(redis_client)

# Default instance (will be replaced with proper Redis client in production)
FraudDetectionService = None
