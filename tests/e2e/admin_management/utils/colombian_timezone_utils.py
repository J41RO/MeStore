# ~/tests/e2e/admin_management/utils/colombian_timezone_utils.py
# Colombian Timezone and Business Hours Utilities
# Realistic time handling for Colombian marketplace operations

"""
Colombian Timezone and Business Hours Utilities.

This module provides utilities for handling Colombian timezone,
business hours, and time-based business rules for E2E testing.
"""

from datetime import datetime, timezone, timedelta, time
from typing import Dict, List, Tuple, Optional
from enum import Enum
import pytz
from dataclasses import dataclass


class BusinessDay(Enum):
    """Colombian business day types."""
    WEEKDAY = "weekday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"
    HOLIDAY = "holiday"


class BusinessHoursType(Enum):
    """Different business hours configurations."""
    STANDARD = "standard"      # 8 AM - 6 PM
    EXTENDED = "extended"      # 7 AM - 8 PM
    WEEKEND = "weekend"        # 9 AM - 4 PM
    HOLIDAY = "holiday"        # Closed


@dataclass
class BusinessHours:
    """Business hours configuration."""
    start_hour: int
    end_hour: int
    description: str
    applies_to: List[BusinessDay]


# Colombian timezone
COLOMBIA_TZ = pytz.timezone('America/Bogota')  # UTC-5

# Business hours configurations
BUSINESS_HOURS_CONFIG = {
    BusinessHoursType.STANDARD: BusinessHours(
        start_hour=8,
        end_hour=18,
        description="Standard business hours (8 AM - 6 PM)",
        applies_to=[BusinessDay.WEEKDAY]
    ),
    BusinessHoursType.EXTENDED: BusinessHours(
        start_hour=7,
        end_hour=20,
        description="Extended business hours (7 AM - 8 PM)",
        applies_to=[BusinessDay.WEEKDAY]
    ),
    BusinessHoursType.WEEKEND: BusinessHours(
        start_hour=9,
        end_hour=16,
        description="Weekend hours (9 AM - 4 PM)",
        applies_to=[BusinessDay.SATURDAY]
    ),
    BusinessHoursType.HOLIDAY: BusinessHours(
        start_hour=0,
        end_hour=0,
        description="Closed on holidays",
        applies_to=[BusinessDay.HOLIDAY, BusinessDay.SUNDAY]
    )
}

# Colombian holidays (2025 - for testing purposes)
COLOMBIAN_HOLIDAYS_2025 = [
    "2025-01-01",  # Año Nuevo
    "2025-01-06",  # Reyes Magos
    "2025-03-24",  # San José
    "2025-04-17",  # Jueves Santo
    "2025-04-18",  # Viernes Santo
    "2025-05-01",  # Día del Trabajo
    "2025-05-19",  # Ascensión del Señor
    "2025-06-09",  # Corpus Christi
    "2025-06-16",  # Sagrado Corazón
    "2025-06-30",  # San Pedro y San Pablo
    "2025-07-20",  # Día de la Independencia
    "2025-08-07",  # Batalla de Boyacá
    "2025-08-18",  # Asunción de la Virgen
    "2025-10-13",  # Día de la Raza
    "2025-11-03",  # Todos los Santos
    "2025-11-17",  # Independencia de Cartagena
    "2025-12-08",  # Inmaculada Concepción
    "2025-12-25",  # Navidad
]


class ColombianTimeManager:
    """Manager for Colombian time and business rules."""

    @staticmethod
    def get_current_colombia_time() -> datetime:
        """Get current time in Colombian timezone."""
        return datetime.now(COLOMBIA_TZ)

    @staticmethod
    def convert_to_colombia_time(dt: datetime) -> datetime:
        """Convert datetime to Colombian timezone."""
        if dt.tzinfo is None:
            # Assume UTC if no timezone info
            dt = dt.replace(tzinfo=pytz.UTC)
        return dt.astimezone(COLOMBIA_TZ)

    @staticmethod
    def get_business_day_type(dt: datetime = None) -> BusinessDay:
        """Determine the business day type for a given date."""
        if dt is None:
            dt = ColombianTimeManager.get_current_colombia_time()

        # Convert to Colombian time if needed
        dt = ColombianTimeManager.convert_to_colombia_time(dt)

        # Check if it's a holiday
        date_str = dt.strftime("%Y-%m-%d")
        if date_str in COLOMBIAN_HOLIDAYS_2025:
            return BusinessDay.HOLIDAY

        # Check day of week
        day_of_week = dt.weekday()  # 0 = Monday, 6 = Sunday

        if day_of_week < 5:  # Monday to Friday
            return BusinessDay.WEEKDAY
        elif day_of_week == 5:  # Saturday
            return BusinessDay.SATURDAY
        else:  # Sunday
            return BusinessDay.SUNDAY

    @staticmethod
    def is_business_hours(dt: datetime = None,
                         hours_type: BusinessHoursType = BusinessHoursType.STANDARD) -> bool:
        """Check if given time is within business hours."""
        if dt is None:
            dt = ColombianTimeManager.get_current_colombia_time()

        dt = ColombianTimeManager.convert_to_colombia_time(dt)
        business_day = ColombianTimeManager.get_business_day_type(dt)
        hours_config = BUSINESS_HOURS_CONFIG[hours_type]

        # Check if this business day type applies to the hours configuration
        if business_day not in hours_config.applies_to:
            # Try weekend hours for Saturday
            if business_day == BusinessDay.SATURDAY:
                weekend_config = BUSINESS_HOURS_CONFIG[BusinessHoursType.WEEKEND]
                if business_day in weekend_config.applies_to:
                    return weekend_config.start_hour <= dt.hour < weekend_config.end_hour
            return False

        # Check if within hours
        return hours_config.start_hour <= dt.hour < hours_config.end_hour

    @staticmethod
    def get_next_business_hour(dt: datetime = None,
                              hours_type: BusinessHoursType = BusinessHoursType.STANDARD) -> datetime:
        """Get the next business hour start time."""
        if dt is None:
            dt = ColombianTimeManager.get_current_colombia_time()

        dt = ColombianTimeManager.convert_to_colombia_time(dt)
        hours_config = BUSINESS_HOURS_CONFIG[hours_type]

        # If already in business hours, return current time
        if ColombianTimeManager.is_business_hours(dt, hours_type):
            return dt

        # Find next business day and time
        check_date = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        for i in range(7):  # Check up to a week ahead
            current_check = check_date + timedelta(days=i)
            business_day = ColombianTimeManager.get_business_day_type(current_check)

            if business_day in hours_config.applies_to:
                return current_check.replace(hour=hours_config.start_hour)

        # Fallback: next Monday at standard business hours
        days_until_monday = (7 - dt.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        next_monday = (dt + timedelta(days=days_until_monday)).replace(hour=8, minute=0, second=0, microsecond=0)
        return next_monday

    @staticmethod
    def calculate_business_hours_between(start_dt: datetime, end_dt: datetime,
                                       hours_type: BusinessHoursType = BusinessHoursType.STANDARD) -> float:
        """
        Calculate business hours between two datetime objects.

        Returns:
            float: Number of business hours between start and end datetime
        """
        start_dt = ColombianTimeManager.convert_to_colombia_time(start_dt)
        end_dt = ColombianTimeManager.convert_to_colombia_time(end_dt)

        if start_dt >= end_dt:
            return 0.0

        total_hours = 0.0
        current_dt = start_dt.replace(minute=0, second=0, microsecond=0)

        while current_dt < end_dt:
            if ColombianTimeManager.is_business_hours(current_dt, hours_type):
                # Calculate how much of this hour counts
                hour_end = min(current_dt + timedelta(hours=1), end_dt)
                hour_start = max(current_dt, start_dt)
                hour_duration = (hour_end - hour_start).total_seconds() / 3600
                total_hours += hour_duration

            current_dt += timedelta(hours=1)

        return total_hours

    @staticmethod
    def simulate_admin_work_schedule(admin_persona: str, base_date: datetime = None) -> Dict[str, any]:
        """
        Simulate a realistic admin work schedule based on persona.

        Args:
            admin_persona: Admin persona key (miguel_ceo, maria_manager, etc.)
            base_date: Base date for schedule generation

        Returns:
            Dict with schedule information
        """
        if base_date is None:
            base_date = ColombianTimeManager.get_current_colombia_time()

        base_date = ColombianTimeManager.convert_to_colombia_time(base_date)

        # Define work patterns by persona
        work_patterns = {
            "miguel_ceo": {
                "typical_start": 7,   # 7 AM
                "typical_end": 19,    # 7 PM
                "works_weekends": True,
                "emergency_availability": True,
                "timezone_flexibility": True
            },
            "maria_manager": {
                "typical_start": 8,   # 8 AM
                "typical_end": 18,    # 6 PM
                "works_weekends": False,
                "emergency_availability": True,
                "timezone_flexibility": False
            },
            "carlos_regional": {
                "typical_start": 8,   # 8 AM
                "typical_end": 17,    # 5 PM
                "works_weekends": False,
                "emergency_availability": False,
                "timezone_flexibility": False
            },
            "ana_security": {
                "typical_start": 6,   # 6 AM (security monitoring)
                "typical_end": 20,    # 8 PM
                "works_weekends": True,
                "emergency_availability": True,
                "timezone_flexibility": True
            },
            "luis_coordinator": {
                "typical_start": 8,   # 8 AM
                "typical_end": 17,    # 5 PM
                "works_weekends": False,
                "emergency_availability": False,
                "timezone_flexibility": False
            }
        }

        pattern = work_patterns.get(admin_persona, work_patterns["carlos_regional"])

        # Generate weekly schedule
        weekly_schedule = {}
        for day in range(7):  # Week starting from base_date
            current_date = base_date + timedelta(days=day)
            business_day = ColombianTimeManager.get_business_day_type(current_date)

            if business_day == BusinessDay.WEEKDAY:
                start_time = current_date.replace(
                    hour=pattern["typical_start"], minute=0, second=0, microsecond=0
                )
                end_time = current_date.replace(
                    hour=pattern["typical_end"], minute=0, second=0, microsecond=0
                )
                available = True
            elif business_day == BusinessDay.SATURDAY and pattern["works_weekends"]:
                start_time = current_date.replace(hour=9, minute=0, second=0, microsecond=0)
                end_time = current_date.replace(hour=14, minute=0, second=0, microsecond=0)
                available = True
            else:
                start_time = None
                end_time = None
                available = pattern["emergency_availability"]

            weekly_schedule[current_date.strftime("%Y-%m-%d")] = {
                "business_day": business_day.value,
                "available": available,
                "start_time": start_time.isoformat() if start_time else None,
                "end_time": end_time.isoformat() if end_time else None,
                "emergency_only": not available and pattern["emergency_availability"]
            }

        return {
            "admin_persona": admin_persona,
            "schedule_week": weekly_schedule,
            "work_pattern": pattern,
            "timezone": "America/Bogota"
        }


class BusinessRulesValidator:
    """Validator for Colombian business rules and compliance."""

    @staticmethod
    def validate_business_hours_operation(operation_time: datetime,
                                        operation_type: str,
                                        admin_persona: str = None) -> Dict[str, any]:
        """
        Validate if an operation can be performed during business hours.

        Args:
            operation_time: When the operation is being performed
            operation_type: Type of operation (vendor_approval, bulk_action, etc.)
            admin_persona: Admin persona performing the operation

        Returns:
            Dict with validation results
        """
        colombia_time = ColombianTimeManager.convert_to_colombia_time(operation_time)
        business_day = ColombianTimeManager.get_business_day_type(colombia_time)
        is_business_hours = ColombianTimeManager.is_business_hours(colombia_time)

        # Define operation restrictions
        operation_rules = {
            "vendor_approval": {
                "requires_business_hours": False,
                "max_security_level_required": 4,
                "audit_trail_required": True
            },
            "bulk_action": {
                "requires_business_hours": True,
                "max_security_level_required": 4,
                "audit_trail_required": True
            },
            "permission_changes": {
                "requires_business_hours": True,
                "max_security_level_required": 5,
                "audit_trail_required": True
            },
            "crisis_response": {
                "requires_business_hours": False,
                "max_security_level_required": 4,
                "audit_trail_required": True
            },
            "routine_maintenance": {
                "requires_business_hours": True,
                "max_security_level_required": 3,
                "audit_trail_required": False
            }
        }

        rules = operation_rules.get(operation_type, operation_rules["routine_maintenance"])

        validation_result = {
            "operation_time": colombia_time.isoformat(),
            "business_day": business_day.value,
            "is_business_hours": is_business_hours,
            "operation_type": operation_type,
            "admin_persona": admin_persona,
            "validation_passed": True,
            "warnings": [],
            "restrictions": []
        }

        # Check business hours requirement
        if rules["requires_business_hours"] and not is_business_hours:
            validation_result["validation_passed"] = False
            validation_result["restrictions"].append(
                "Operation requires business hours execution"
            )

        # Check holiday restrictions
        if business_day == BusinessDay.HOLIDAY:
            validation_result["warnings"].append(
                "Operation performed on Colombian holiday"
            )

        # Check weekend warnings
        if business_day in [BusinessDay.SATURDAY, BusinessDay.SUNDAY] and rules["requires_business_hours"]:
            validation_result["warnings"].append(
                "Non-standard operation time - weekend execution"
            )

        return validation_result

    @staticmethod
    def get_optimal_operation_time(operation_type: str,
                                 current_time: datetime = None) -> datetime:
        """Get the optimal time to perform an operation based on business rules."""
        if current_time is None:
            current_time = ColombianTimeManager.get_current_colombia_time()

        current_time = ColombianTimeManager.convert_to_colombia_time(current_time)

        # If operation can be done anytime, return current time
        validation = BusinessRulesValidator.validate_business_hours_operation(
            current_time, operation_type
        )

        if validation["validation_passed"] and not validation["warnings"]:
            return current_time

        # Find next optimal time
        return ColombianTimeManager.get_next_business_hour(current_time)


# Export key classes and functions
__all__ = [
    "BusinessDay",
    "BusinessHoursType",
    "BusinessHours",
    "ColombianTimeManager",
    "BusinessRulesValidator",
    "COLOMBIA_TZ",
    "BUSINESS_HOURS_CONFIG",
    "COLOMBIAN_HOLIDAYS_2025"
]