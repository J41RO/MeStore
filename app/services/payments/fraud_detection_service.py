"""
Fraud Detection Service for Payment Processing

This service implements comprehensive fraud detection and prevention mechanisms
for the Wompi payment integration, including real-time transaction analysis,
risk scoring, and automated response actions.
"""

import logging
import asyncio
import json
import hashlib
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.models.order import Order, Transaction, PaymentStatus
from app.models.user import User
from app.models.payment import Payment

logger = logging.getLogger(__name__)
fraud_logger = logging.getLogger(f"{__name__}.fraud")
security_logger = logging.getLogger(f"{__name__}.security")


class RiskLevel(Enum):
    """Risk level classification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FraudAction(Enum):
    """Actions to take based on fraud detection"""
    ALLOW = "allow"
    REVIEW = "review"
    DECLINE = "decline"
    BLOCK = "block"


@dataclass
class RiskRule:
    """Definition of a fraud detection rule"""
    name: str
    description: str
    risk_score: int  # 0-100
    condition_function: callable
    action: FraudAction
    enabled: bool = True


@dataclass
class FraudAnalysisResult:
    """Result of fraud analysis"""
    risk_level: RiskLevel
    risk_score: int
    action: FraudAction
    triggered_rules: List[Dict[str, Any]]
    confidence: float
    metadata: Dict[str, Any]
    analysis_duration: float


class FraudDetectionService:
    """Comprehensive fraud detection and prevention service"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.rules: List[RiskRule] = []
        self._initialize_rules()

    def _initialize_rules(self):
        """Initialize fraud detection rules"""
        self.rules = [
            # Amount-based rules
            RiskRule(
                name="high_amount_transaction",
                description="Transaction amount exceeds normal thresholds",
                risk_score=30,
                condition_function=self._check_high_amount,
                action=FraudAction.REVIEW
            ),
            RiskRule(
                name="suspicious_amount_pattern",
                description="Unusual amount patterns (round numbers, specific sequences)",
                risk_score=20,
                condition_function=self._check_suspicious_amounts,
                action=FraudAction.REVIEW
            ),

            # Velocity-based rules
            RiskRule(
                name="rapid_transactions",
                description="Multiple transactions in short time period",
                risk_score=40,
                condition_function=self._check_rapid_transactions,
                action=FraudAction.REVIEW
            ),
            RiskRule(
                name="high_volume_user",
                description="User exceeding daily/weekly transaction limits",
                risk_score=35,
                condition_function=self._check_high_volume,
                action=FraudAction.REVIEW
            ),

            # Behavioral rules
            RiskRule(
                name="new_user_high_value",
                description="New user attempting high-value transaction",
                risk_score=50,
                condition_function=self._check_new_user_behavior,
                action=FraudAction.REVIEW
            ),
            RiskRule(
                name="unusual_time_pattern",
                description="Transaction at unusual hours for user",
                risk_score=25,
                condition_function=self._check_time_patterns,
                action=FraudAction.REVIEW
            ),

            # Technical rules
            RiskRule(
                name="multiple_payment_attempts",
                description="Multiple failed payment attempts before success",
                risk_score=45,
                condition_function=self._check_payment_attempts,
                action=FraudAction.REVIEW
            ),
            RiskRule(
                name="suspicious_user_agent",
                description="Suspicious or bot-like user agent patterns",
                risk_score=30,
                condition_function=self._check_user_agent,
                action=FraudAction.REVIEW
            ),

            # Geographic rules
            RiskRule(
                name="unusual_location",
                description="Transaction from unusual geographic location",
                risk_score=35,
                condition_function=self._check_location_risk,
                action=FraudAction.REVIEW
            ),

            # Critical rules that trigger immediate action
            RiskRule(
                name="known_fraud_patterns",
                description="Matches known fraud patterns or blacklisted entities",
                risk_score=100,
                condition_function=self._check_known_fraud_patterns,
                action=FraudAction.DECLINE
            ),
            RiskRule(
                name="duplicate_transaction",
                description="Exact duplicate of recent transaction",
                risk_score=80,
                condition_function=self._check_duplicate_transactions,
                action=FraudAction.DECLINE
            )
        ]

    async def analyze_transaction_risk(
        self,
        transaction_data: Dict[str, Any],
        user_data: Dict[str, Any],
        order_data: Dict[str, Any],
        request_metadata: Optional[Dict[str, Any]] = None
    ) -> FraudAnalysisResult:
        """
        Perform comprehensive fraud analysis on a transaction

        Args:
            transaction_data: Transaction details (amount, currency, etc.)
            user_data: User information and history
            order_data: Order details
            request_metadata: Request metadata (IP, user agent, etc.)

        Returns:
            FraudAnalysisResult with risk assessment and recommended action
        """
        start_time = datetime.utcnow()
        triggered_rules = []
        total_risk_score = 0

        fraud_logger.info(
            "Starting fraud analysis",
            extra={
                "transaction_id": transaction_data.get("id"),
                "user_id": user_data.get("id"),
                "amount": transaction_data.get("amount_in_cents"),
                "order_id": order_data.get("id")
            }
        )

        try:
            # Prepare analysis context
            context = {
                "transaction": transaction_data,
                "user": user_data,
                "order": order_data,
                "metadata": request_metadata or {},
                "timestamp": start_time
            }

            # Run all enabled fraud detection rules
            for rule in self.rules:
                if not rule.enabled:
                    continue

                try:
                    rule_result = await rule.condition_function(context)
                    if rule_result.get("triggered", False):
                        rule_info = {
                            "rule_name": rule.name,
                            "description": rule.description,
                            "risk_score": rule.risk_score,
                            "action": rule.action.value,
                            "details": rule_result.get("details", {}),
                            "confidence": rule_result.get("confidence", 1.0)
                        }
                        triggered_rules.append(rule_info)
                        total_risk_score += rule.risk_score

                        fraud_logger.warning(
                            f"Fraud rule triggered: {rule.name}",
                            extra={
                                "rule": rule.name,
                                "risk_score": rule.risk_score,
                                "transaction_id": transaction_data.get("id"),
                                "details": rule_result.get("details")
                            }
                        )

                except Exception as e:
                    logger.error(f"Error executing fraud rule {rule.name}: {e}")
                    continue

            # Calculate final risk assessment
            risk_level = self._calculate_risk_level(total_risk_score)
            action = self._determine_action(triggered_rules, risk_level)
            confidence = self._calculate_confidence(triggered_rules, total_risk_score)

            # Analysis duration
            duration = (datetime.utcnow() - start_time).total_seconds()

            result = FraudAnalysisResult(
                risk_level=risk_level,
                risk_score=total_risk_score,
                action=action,
                triggered_rules=triggered_rules,
                confidence=confidence,
                metadata={
                    "analysis_timestamp": start_time.isoformat(),
                    "rules_evaluated": len(self.rules),
                    "rules_triggered": len(triggered_rules),
                    "transaction_fingerprint": self._generate_transaction_fingerprint(context)
                },
                analysis_duration=duration
            )

            # Log final result
            fraud_logger.info(
                "Fraud analysis completed",
                extra={
                    "transaction_id": transaction_data.get("id"),
                    "risk_level": risk_level.value,
                    "risk_score": total_risk_score,
                    "action": action.value,
                    "rules_triggered": len(triggered_rules),
                    "duration_ms": duration * 1000
                }
            )

            # Create audit record
            await self._create_fraud_analysis_record(context, result)

            return result

        except Exception as e:
            logger.error(f"Error in fraud analysis: {e}")
            # Return safe default on error
            return FraudAnalysisResult(
                risk_level=RiskLevel.MEDIUM,
                risk_score=50,
                action=FraudAction.REVIEW,
                triggered_rules=[{
                    "rule_name": "analysis_error",
                    "description": "Error during fraud analysis",
                    "risk_score": 50,
                    "action": "review",
                    "details": {"error": str(e)}
                }],
                confidence=0.5,
                metadata={"error": str(e)},
                analysis_duration=(datetime.utcnow() - start_time).total_seconds()
            )

    # Fraud detection rule implementations

    async def _check_high_amount(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check for unusually high transaction amounts"""
        amount_cents = context["transaction"].get("amount_in_cents", 0)
        amount = Decimal(amount_cents) / 100

        # Get user's transaction history for comparison
        user_id = context["user"].get("id")
        if user_id:
            avg_amount = await self._get_user_average_transaction_amount(user_id)
            if avg_amount and amount > avg_amount * 5:  # 5x average
                return {
                    "triggered": True,
                    "details": {
                        "transaction_amount": float(amount),
                        "user_average": float(avg_amount),
                        "multiplier": float(amount / avg_amount)
                    },
                    "confidence": 0.8
                }

        # Check against global thresholds
        if amount > Decimal("1000000"):  # $10,000 USD equivalent
            return {
                "triggered": True,
                "details": {
                    "transaction_amount": float(amount),
                    "threshold": 1000000,
                    "reason": "exceeds_global_threshold"
                },
                "confidence": 0.9
            }

        return {"triggered": False}

    async def _check_suspicious_amounts(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check for suspicious amount patterns"""
        amount_cents = context["transaction"].get("amount_in_cents", 0)
        amount = Decimal(amount_cents) / 100

        suspicious_patterns = []

        # Round numbers (exact thousands, hundreds)
        if amount % 100 == 0 and amount >= 100:
            suspicious_patterns.append("round_hundreds")

        if amount % 1000 == 0 and amount >= 1000:
            suspicious_patterns.append("round_thousands")

        # Repeating digits
        amount_str = str(int(amount))
        if len(set(amount_str)) == 1 and len(amount_str) >= 3:
            suspicious_patterns.append("repeating_digits")

        # Sequential numbers
        if self._is_sequential(amount_str):
            suspicious_patterns.append("sequential_digits")

        if suspicious_patterns:
            return {
                "triggered": True,
                "details": {
                    "amount": float(amount),
                    "patterns": suspicious_patterns
                },
                "confidence": 0.6
            }

        return {"triggered": False}

    async def _check_rapid_transactions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check for rapid succession of transactions"""
        user_id = context["user"].get("id")
        if not user_id:
            return {"triggered": False}

        # Check transactions in last 10 minutes
        cutoff_time = datetime.utcnow() - timedelta(minutes=10)

        result = await self.db.execute(
            select(func.count(Transaction.id))
            .join(Order)
            .where(
                and_(
                    Order.buyer_id == user_id,
                    Transaction.created_at >= cutoff_time
                )
            )
        )
        recent_count = result.scalar() or 0

        if recent_count >= 5:  # 5+ transactions in 10 minutes
            return {
                "triggered": True,
                "details": {
                    "recent_transactions": recent_count,
                    "time_window_minutes": 10,
                    "threshold": 5
                },
                "confidence": 0.8
            }

        return {"triggered": False}

    async def _check_high_volume(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check for high transaction volume"""
        user_id = context["user"].get("id")
        if not user_id:
            return {"triggered": False}

        # Check daily volume
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        result = await self.db.execute(
            select(func.sum(Order.total_amount), func.count(Order.id))
            .where(
                and_(
                    Order.buyer_id == user_id,
                    Order.created_at >= today_start
                )
            )
        )
        daily_volume, daily_count = result.first() or (0, 0)

        # Check against limits
        if daily_volume and daily_volume > 50000:  # $500 daily limit
            return {
                "triggered": True,
                "details": {
                    "daily_volume": float(daily_volume),
                    "daily_count": daily_count,
                    "limit": 50000,
                    "type": "volume_limit"
                },
                "confidence": 0.9
            }

        if daily_count >= 20:  # 20 transactions per day
            return {
                "triggered": True,
                "details": {
                    "daily_count": daily_count,
                    "daily_volume": float(daily_volume) if daily_volume else 0,
                    "limit": 20,
                    "type": "count_limit"
                },
                "confidence": 0.8
            }

        return {"triggered": False}

    async def _check_new_user_behavior(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check for risky behavior from new users"""
        user_data = context["user"]
        user_id = user_data.get("id")
        created_at = user_data.get("created_at")

        if not user_id or not created_at:
            return {"triggered": False}

        # Parse created_at if it's a string
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            except:
                return {"triggered": False}

        # Check if user is new (less than 7 days old)
        account_age = datetime.utcnow() - created_at.replace(tzinfo=None)
        if account_age.days >= 7:
            return {"triggered": False}

        # Check transaction amount for new user
        amount_cents = context["transaction"].get("amount_in_cents", 0)
        amount = Decimal(amount_cents) / 100

        # New users with high-value transactions are risky
        if amount > Decimal("500"):  # $5,000 for account < 7 days old
            return {
                "triggered": True,
                "details": {
                    "account_age_days": account_age.days,
                    "transaction_amount": float(amount),
                    "threshold": 500,
                    "reason": "new_user_high_value"
                },
                "confidence": 0.7
            }

        return {"triggered": False}

    async def _check_time_patterns(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check for unusual time patterns"""
        transaction_time = context["timestamp"]
        hour = transaction_time.hour

        # Transactions between 2 AM and 6 AM are more suspicious
        if 2 <= hour <= 6:
            return {
                "triggered": True,
                "details": {
                    "transaction_hour": hour,
                    "reason": "unusual_hours",
                    "time_range": "02:00-06:00"
                },
                "confidence": 0.5
            }

        return {"triggered": False}

    async def _check_payment_attempts(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check for multiple payment attempts"""
        # This would require tracking failed attempts
        # For now, return a placeholder
        return {"triggered": False}

    async def _check_user_agent(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check for suspicious user agents"""
        user_agent = context["metadata"].get("user_agent", "")

        suspicious_patterns = []

        if not user_agent:
            suspicious_patterns.append("missing_user_agent")
        elif any(bot in user_agent.lower() for bot in ["bot", "crawler", "spider", "scraper"]):
            suspicious_patterns.append("bot_user_agent")
        elif len(user_agent) < 20:
            suspicious_patterns.append("short_user_agent")
        elif "curl" in user_agent.lower() or "wget" in user_agent.lower():
            suspicious_patterns.append("command_line_tool")

        if suspicious_patterns:
            return {
                "triggered": True,
                "details": {
                    "user_agent": user_agent,
                    "patterns": suspicious_patterns
                },
                "confidence": 0.6
            }

        return {"triggered": False}

    async def _check_location_risk(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check for location-based risk factors"""
        # Placeholder for geo-location checks
        # Would integrate with IP geolocation services
        return {"triggered": False}

    async def _check_known_fraud_patterns(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check against known fraud patterns"""
        # Placeholder for blacklist checks
        # Would check against fraud databases, blacklists, etc.
        return {"triggered": False}

    async def _check_duplicate_transactions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check for duplicate transactions"""
        user_id = context["user"].get("id")
        amount_cents = context["transaction"].get("amount_in_cents", 0)

        if not user_id:
            return {"triggered": False}

        # Check for exact same amount in last hour
        cutoff_time = datetime.utcnow() - timedelta(hours=1)

        result = await self.db.execute(
            select(func.count(Transaction.id))
            .join(Order)
            .where(
                and_(
                    Order.buyer_id == user_id,
                    Transaction.amount == amount_cents / 100,
                    Transaction.created_at >= cutoff_time
                )
            )
        )
        duplicate_count = result.scalar() or 0

        if duplicate_count > 0:
            return {
                "triggered": True,
                "details": {
                    "duplicate_count": duplicate_count,
                    "amount": amount_cents / 100,
                    "time_window_hours": 1
                },
                "confidence": 0.9
            }

        return {"triggered": False}

    # Helper methods

    def _calculate_risk_level(self, risk_score: int) -> RiskLevel:
        """Calculate risk level based on total risk score"""
        if risk_score >= 80:
            return RiskLevel.CRITICAL
        elif risk_score >= 60:
            return RiskLevel.HIGH
        elif risk_score >= 30:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _determine_action(self, triggered_rules: List[Dict], risk_level: RiskLevel) -> FraudAction:
        """Determine action based on triggered rules and risk level"""
        # Check for any DECLINE or BLOCK actions
        for rule in triggered_rules:
            if rule.get("action") == "decline":
                return FraudAction.DECLINE
            elif rule.get("action") == "block":
                return FraudAction.BLOCK

        # Default based on risk level
        if risk_level == RiskLevel.CRITICAL:
            return FraudAction.DECLINE
        elif risk_level == RiskLevel.HIGH:
            return FraudAction.REVIEW
        elif risk_level == RiskLevel.MEDIUM:
            return FraudAction.REVIEW
        else:
            return FraudAction.ALLOW

    def _calculate_confidence(self, triggered_rules: List[Dict], total_score: int) -> float:
        """Calculate confidence in the fraud analysis"""
        if not triggered_rules:
            return 1.0

        # Average confidence of triggered rules, weighted by risk score
        total_confidence = 0
        total_weight = 0

        for rule in triggered_rules:
            confidence = rule.get("confidence", 1.0)
            weight = rule.get("risk_score", 10)
            total_confidence += confidence * weight
            total_weight += weight

        return min(total_confidence / total_weight if total_weight > 0 else 0.5, 1.0)

    def _generate_transaction_fingerprint(self, context: Dict[str, Any]) -> str:
        """Generate unique fingerprint for transaction"""
        fingerprint_data = {
            "user_id": context["user"].get("id"),
            "amount": context["transaction"].get("amount_in_cents"),
            "currency": context["transaction"].get("currency"),
            "user_agent": context["metadata"].get("user_agent", ""),
            "ip_address": context["metadata"].get("ip_address", "")
        }

        fingerprint_string = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_string.encode()).hexdigest()

    def _is_sequential(self, number_str: str) -> bool:
        """Check if digits are in sequence"""
        if len(number_str) < 3:
            return False

        for i in range(len(number_str) - 2):
            if int(number_str[i+1]) != int(number_str[i]) + 1:
                return False
        return True

    async def _get_user_average_transaction_amount(self, user_id: int) -> Optional[Decimal]:
        """Get user's average transaction amount"""
        result = await self.db.execute(
            select(func.avg(Order.total_amount))
            .where(Order.buyer_id == user_id)
        )
        avg_amount = result.scalar()
        return Decimal(str(avg_amount)) if avg_amount else None

    async def _create_fraud_analysis_record(self, context: Dict[str, Any], result: FraudAnalysisResult) -> None:
        """Create audit record for fraud analysis"""
        # In a real system, this would create a record in a fraud_analysis table
        security_logger.info(
            "Fraud analysis audit record",
            extra={
                "transaction_id": context["transaction"].get("id"),
                "user_id": context["user"].get("id"),
                "risk_level": result.risk_level.value,
                "risk_score": result.risk_score,
                "action": result.action.value,
                "triggered_rules": [r["rule_name"] for r in result.triggered_rules],
                "confidence": result.confidence,
                "fingerprint": result.metadata.get("transaction_fingerprint")
            }
        )

    async def update_rule_configuration(
        self,
        rule_name: str,
        enabled: Optional[bool] = None,
        risk_score: Optional[int] = None,
        action: Optional[FraudAction] = None
    ) -> bool:
        """Update fraud detection rule configuration"""
        for rule in self.rules:
            if rule.name == rule_name:
                if enabled is not None:
                    rule.enabled = enabled
                if risk_score is not None:
                    rule.risk_score = risk_score
                if action is not None:
                    rule.action = action

                fraud_logger.info(
                    f"Updated fraud rule configuration: {rule_name}",
                    extra={
                        "rule_name": rule_name,
                        "enabled": rule.enabled,
                        "risk_score": rule.risk_score,
                        "action": rule.action.value
                    }
                )
                return True

        return False

    def get_rule_configuration(self) -> List[Dict[str, Any]]:
        """Get current fraud detection rule configuration"""
        return [
            {
                "name": rule.name,
                "description": rule.description,
                "risk_score": rule.risk_score,
                "action": rule.action.value,
                "enabled": rule.enabled
            }
            for rule in self.rules
        ]


def get_fraud_detection_service(db: AsyncSession) -> FraudDetectionService:
    """Factory function to create FraudDetectionService instance"""
    return FraudDetectionService(db)