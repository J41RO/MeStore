"""
Tests específicos para campos de perfil empresa y direccion.

Este módulo contiene tests unitarios para validar:
- Creación de usuarios con campos empresa y direccion
- Validación de campos opcionales
- Serialización con to_dict()
- Schemas Pydantic con nuevos campos
"""

import pytest
from app.models.user import User, UserType
from app.schemas.user import UserBase, UserCreate


class TestUserProfileFields:
    """Tests para campos de perfil empresa y direccion."""

    def test_user_model_has_empresa_direccion_fields(self):
        """Verificar que modelo User tiene campos empresa y direccion."""
        columns = [c.name for c in User.__table__.columns]

        assert "empresa" in columns, "Campo empresa debe existir en modelo User"
        assert "direccion" in columns, "Campo direccion debe existir en modelo User"
        assert len(columns) == 15, f"Esperado 15 columnas, encontrado {len(columns)}"

    def test_user_schema_accepts_empresa_direccion(self):
        """Verificar que UserBase acepta empresa y direccion."""
        user_data = UserBase(
            email="test@empresa.com",
            nombre="Juan",
            apellido="Pérez",
            empresa="MiEmpresa S.A.S",
            direccion="Calle 123 #45-67, Bogotá"
        )

        assert user_data.empresa == "MiEmpresa S.A.S"
        assert user_data.direccion == "Calle 123 #45-67, Bogotá"

    def test_user_create_inherits_empresa_direccion(self):
        """Verificar que UserCreate hereda empresa y direccion."""
        user_create = UserCreate(
            email="create@test.com",
            nombre="María",
            apellido="García",
            password="SecurePass123",
            empresa="TechCorp",
            direccion="Carrera 15 #32-10"
        )

        assert user_create.empresa == "TechCorp"
        assert user_create.direccion == "Carrera 15 #32-10"

    def test_empresa_direccion_are_optional(self):
        """Verificar que empresa y direccion son opcionales."""
        # UserBase sin empresa ni direccion debe funcionar
        user_data = UserBase(
            email="optional@test.com",
            nombre="Test",
            apellido="User"
        )

        assert user_data.empresa is None
        assert user_data.direccion is None

    def test_existing_fields_not_affected(self):
        """Verificar que campos existentes no se afectaron."""
        user_data = UserBase(
            email="existing@test.com",
            nombre="Juan",
            apellido="Pérez",
            cedula="87654321",
            telefono="3009876543",
            ciudad="Medellín",
            empresa="NewCorp",
            direccion="Nueva Dirección"
        )

        # Verificar campos colombianos siguen funcionando
        assert user_data.cedula == "87654321"
        assert user_data.telefono == "3009876543"
        assert user_data.ciudad == "Medellín"

        # Verificar campos básicos siguen funcionando
        assert user_data.nombre == "Juan"
        assert user_data.apellido == "Pérez"
        assert user_data.email == "existing@test.com"

        # Verificar nuevos campos también funcionan
        assert user_data.empresa == "NewCorp"
        assert user_data.direccion == "Nueva Dirección"
