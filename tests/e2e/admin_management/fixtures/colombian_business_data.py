# ~/tests/e2e/admin_management/fixtures/colombian_business_data.py
# Colombian Business Context Data for E2E Testing
# Realistic data patterns for Colombian marketplace administrators

"""
Colombian Business Context Fixtures for E2E Testing.

This module provides realistic Colombian business data for testing
admin management workflows in a marketplace context.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any
import uuid
from dataclasses import dataclass, field

# Colombian timezone: UTC-5
COLOMBIA_TZ = timezone(timedelta(hours=-5))


@dataclass
class ColombianDepartment:
    """Colombian department data structure."""
    name: str
    code: str
    capital: str
    region: str
    major_cities: List[str]
    business_hours_start: int = 8  # 8 AM
    business_hours_end: int = 18   # 6 PM


@dataclass
class AdminPersona:
    """Admin user persona with Colombian context."""
    name: str
    email: str
    role: str
    department: str
    city: str
    security_level: int
    employee_id: str
    phone: str
    specialization: List[str]
    languages: List[str] = field(default_factory=lambda: ["Spanish"])


# Colombian Departments with Business Context
COLOMBIAN_DEPARTMENTS = {
    "cundinamarca": ColombianDepartment(
        name="Cundinamarca",
        code="CUN",
        capital="Bogotá",
        region="Andina",
        major_cities=["Bogotá", "Soacha", "Girardot", "Zipaquirá", "Facatativá"]
    ),
    "antioquia": ColombianDepartment(
        name="Antioquia",
        code="ANT",
        capital="Medellín",
        region="Andina",
        major_cities=["Medellín", "Bello", "Itagüí", "Envigado", "Apartadó"]
    ),
    "valle_del_cauca": ColombianDepartment(
        name="Valle del Cauca",
        code="VAL",
        capital="Cali",
        region="Pacífica",
        major_cities=["Cali", "Palmira", "Buenaventura", "Cartago", "Tuluá"]
    ),
    "atlantico": ColombianDepartment(
        name="Atlántico",
        code="ATL",
        capital="Barranquilla",
        region="Caribe",
        major_cities=["Barranquilla", "Soledad", "Malambo", "Sabanagrande"]
    ),
    "santander": ColombianDepartment(
        name="Santander",
        code="SAN",
        capital="Bucaramanga",
        region="Andina",
        major_cities=["Bucaramanga", "Floridablanca", "Girón", "Piedecuesta"]
    )
}

# Admin Personas for E2E Testing
ADMIN_PERSONAS = {
    "miguel_ceo": AdminPersona(
        name="Miguel Rodríguez",
        email="miguel.rodriguez@mestore.co",
        role="SUPERUSER",
        department="cundinamarca",
        city="Bogotá",
        security_level=5,
        employee_id="CEO001",
        phone="+57 301 234 5678",
        specialization=["Strategic Management", "Marketplace Operations", "Colombian Market"],
        languages=["Spanish", "English"]
    ),
    "maria_manager": AdminPersona(
        name="María Fernández",
        email="maria.fernandez@mestore.co",
        role="ADMIN",
        department="antioquia",
        city="Medellín",
        security_level=4,
        employee_id="ADM001",
        phone="+57 300 987 6543",
        specialization=["Vendor Management", "Regional Operations", "Antioquia Market"],
        languages=["Spanish", "English"]
    ),
    "carlos_regional": AdminPersona(
        name="Carlos Pérez",
        email="carlos.perez@mestore.co",
        role="ADMIN",
        department="valle_del_cauca",
        city="Cali",
        security_level=3,
        employee_id="ADM002",
        phone="+57 315 456 7890",
        specialization=["Regional Management", "Pacific Coast Operations"],
        languages=["Spanish"]
    ),
    "ana_security": AdminPersona(
        name="Ana Gutiérrez",
        email="ana.gutierrez@mestore.co",
        role="ADMIN",
        department="atlantico",
        city="Barranquilla",
        security_level=4,
        employee_id="SEC001",
        phone="+57 310 123 4567",
        specialization=["Security Management", "Compliance", "Caribbean Operations"],
        languages=["Spanish", "English"]
    ),
    "luis_coordinator": AdminPersona(
        name="Luis Morales",
        email="luis.morales@mestore.co",
        role="ADMIN",
        department="santander",
        city="Bucaramanga",
        security_level=3,
        employee_id="ADM003",
        phone="+57 312 345 6789",
        specialization=["Operations Coordination", "Northeast Region"],
        languages=["Spanish"]
    )
}

# Vendor Categories for Colombian Market
VENDOR_CATEGORIES = {
    "moda": {
        "name": "Moda y Ropa",
        "subcategories": ["Ropa Mujer", "Ropa Hombre", "Calzado", "Accesorios"],
        "typical_regions": ["cundinamarca", "antioquia", "valle_del_cauca"]
    },
    "electronicos": {
        "name": "Electrónicos",
        "subcategories": ["Celulares", "Computadores", "Electrodomésticos"],
        "typical_regions": ["cundinamarca", "antioquia", "atlantico"]
    },
    "hogar": {
        "name": "Hogar y Decoración",
        "subcategories": ["Muebles", "Decoración", "Cocina", "Jardín"],
        "typical_regions": ["valle_del_cauca", "santander", "antioquia"]
    },
    "deportes": {
        "name": "Deportes y Recreación",
        "subcategories": ["Fitness", "Deportes Acuáticos", "Fútbol", "Ciclismo"],
        "typical_regions": ["antioquia", "valle_del_cauca", "cundinamarca"]
    },
    "alimentacion": {
        "name": "Alimentación",
        "subcategories": ["Productos Orgánicos", "Bebidas", "Snacks", "Comida Regional"],
        "typical_regions": ["cundinamarca", "antioquia", "valle_del_cauca", "atlantico"]
    }
}

# Business Hours in Colombian Time
BUSINESS_HOURS = {
    "standard": {"start": 8, "end": 18},  # 8 AM - 6 PM
    "extended": {"start": 7, "end": 20},  # 7 AM - 8 PM
    "weekend": {"start": 9, "end": 16}    # 9 AM - 4 PM
}

# Colombian Business Compliance Data
COMPLIANCE_REQUIREMENTS = {
    "data_protection": {
        "law": "Ley 1581 de 2012",
        "description": "Régimen General de Protección de Datos Personales",
        "required_fields": ["habeas_data_accepted", "data_processing_consent"]
    },
    "tax_requirements": {
        "document_types": ["CC", "CE", "NIT", "PP"],
        "required_for_vendors": True
    },
    "financial_regulations": {
        "banking_supervision": "Superintendencia Financiera",
        "payment_processors": ["PSE", "Tarjetas", "Efectivo"]
    }
}


class ColombianBusinessDataFactory:
    """Factory for generating Colombian business test data."""

    @staticmethod
    def get_current_colombia_time() -> datetime:
        """Get current time in Colombian timezone (UTC-5)."""
        return datetime.now(COLOMBIA_TZ)

    @staticmethod
    def is_business_hours(dt: datetime = None) -> bool:
        """Check if given time is within Colombian business hours."""
        if dt is None:
            dt = ColombianBusinessDataFactory.get_current_colombia_time()

        # Convert to Colombian time if needed
        if dt.tzinfo != COLOMBIA_TZ:
            dt = dt.astimezone(COLOMBIA_TZ)

        hour = dt.hour
        day_of_week = dt.weekday()  # 0 = Monday, 6 = Sunday

        # Weekend check
        if day_of_week >= 5:  # Saturday or Sunday
            return BUSINESS_HOURS["weekend"]["start"] <= hour < BUSINESS_HOURS["weekend"]["end"]

        # Weekday business hours
        return BUSINESS_HOURS["standard"]["start"] <= hour < BUSINESS_HOURS["standard"]["end"]

    @staticmethod
    def generate_admin_test_data(persona_key: str) -> Dict[str, Any]:
        """Generate complete admin test data for a persona."""
        persona = ADMIN_PERSONAS[persona_key]
        department = COLOMBIAN_DEPARTMENTS[persona.department]

        return {
            "email": persona.email,
            "password_hash": "$2b$12$LHJIaP9sWLJ.WgHnrTqLMeYjKq7vBxKEY2A7KhM9vg2xW1nVx2Y1u",  # "testpassword123"
            "nombre": persona.name.split()[0],
            "apellido": " ".join(persona.name.split()[1:]),
            "user_type": persona.role,
            "security_clearance_level": persona.security_level,
            "department_id": persona.department,
            "employee_id": persona.employee_id,
            "telefono": persona.phone,
            "ciudad": persona.city,
            # Note: Removed invalid fields: departamento, specialization, languages, habeas_data_accepted, data_processing_consent
            "is_active": True,
            "is_verified": True,
            "performance_score": 95
        }

    @staticmethod
    def generate_vendor_test_data(category: str, region: str, count: int = 5) -> List[Dict[str, Any]]:
        """Generate vendor test data for a specific category and region."""
        vendors = []
        category_data = VENDOR_CATEGORIES.get(category, VENDOR_CATEGORIES["moda"])
        department = COLOMBIAN_DEPARTMENTS[region]

        for i in range(count):
            vendor_id = str(uuid.uuid4())
            vendors.append({
                "id": vendor_id,
                "business_name": f"{category_data['name']} {department.capital} {i+1}",
                "email": f"vendor.{category}.{region}.{i+1}@example.com",
                "categoria": category,
                "subcategoria": category_data["subcategories"][i % len(category_data["subcategories"])],
                "departamento": department.name,
                "ciudad": department.major_cities[i % len(department.major_cities)],
                "documento_tipo": "NIT",
                "documento_numero": f"90012345{i:03d}",
                "phone": f"+57 30{i%10} {100+i:03d} {1000+i:04d}",
                "is_active": True,
                "vendor_status": "APPROVED",
                "created_at": ColombianBusinessDataFactory.get_current_colombia_time() - timedelta(days=i*10)
            })

        return vendors

    @staticmethod
    def generate_crisis_scenario_data() -> Dict[str, Any]:
        """Generate data for crisis management scenarios."""
        return {
            "compromised_admin": {
                "id": str(uuid.uuid4()),
                "email": "compromised.admin@mestore.co",
                "department": "cundinamarca",
                "security_level": 3,
                "last_login": ColombianBusinessDataFactory.get_current_colombia_time() - timedelta(hours=2),
                "suspicious_activities": [
                    "Multiple failed login attempts from different IPs",
                    "Bulk permission changes outside business hours",
                    "Access to sensitive vendor data",
                    "Unusual geographic login pattern"
                ]
            },
            "affected_vendors": ColombianBusinessDataFactory.generate_vendor_test_data("electronicos", "cundinamarca", 10),
            "incident_timeline": [
                {
                    "timestamp": ColombianBusinessDataFactory.get_current_colombia_time() - timedelta(hours=3),
                    "event": "Suspicious login detected from foreign IP",
                    "severity": "MEDIUM"
                },
                {
                    "timestamp": ColombianBusinessDataFactory.get_current_colombia_time() - timedelta(hours=2),
                    "event": "Bulk permission changes initiated",
                    "severity": "HIGH"
                },
                {
                    "timestamp": ColombianBusinessDataFactory.get_current_colombia_time() - timedelta(hours=1),
                    "event": "Security breach confirmed",
                    "severity": "CRITICAL"
                }
            ]
        }

    @staticmethod
    def get_department_expansion_data() -> Dict[str, Any]:
        """Generate data for department expansion scenarios."""
        return {
            "new_departments": ["huila", "tolima", "caldas"],
            "expansion_timeline": {
                "phase_1": {
                    "duration_weeks": 4,
                    "departments": ["huila"],
                    "admin_count": 2,
                    "vendor_target": 25
                },
                "phase_2": {
                    "duration_weeks": 6,
                    "departments": ["tolima"],
                    "admin_count": 3,
                    "vendor_target": 40
                },
                "phase_3": {
                    "duration_weeks": 8,
                    "departments": ["caldas"],
                    "admin_count": 3,
                    "vendor_target": 35
                }
            },
            "required_permissions": [
                "users.create.regional",
                "vendors.approve.regional",
                "marketplace.configure.regional",
                "reports.generate.regional"
            ]
        }


# Export key data for easy access
__all__ = [
    "COLOMBIAN_DEPARTMENTS",
    "ADMIN_PERSONAS",
    "VENDOR_CATEGORIES",
    "BUSINESS_HOURS",
    "COMPLIANCE_REQUIREMENTS",
    "ColombianBusinessDataFactory",
    "COLOMBIA_TZ"
]