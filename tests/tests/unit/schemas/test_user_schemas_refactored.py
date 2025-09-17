"""
Tests específicos para schemas refactorizados - Tarea 1.2.1.6

Valida:
- UserUpdate con campos opcionales
- Validadores Pydantic V2 
- UserResponse como alias
- Compatibilidad con UUID
"""

import pytest
from uuid import uuid4, UUID
from datetime import datetime
from pydantic import ValidationError

from app.schemas.user import (
    UserBase, UserCreate, UserUpdate, UserRead, UserResponse, UserInDB
)
from app.models.user import UserType


class TestUserUpdate:
    """Tests para UserUpdate schema con campos opcionales"""

    def test_user_update_empty(self):
        """UserUpdate puede ser vacío (actualizaciones parciales)"""
        user_update = UserUpdate()
        assert user_update is not None

    def test_user_update_partial_fields(self):
        """UserUpdate acepta campos parciales"""
        user_update = UserUpdate(
            nombre="Juan Carlos",
            telefono="3009876543"
        )
        assert user_update.nombre == "Juan Carlos"
        assert user_update.telefono == "+57 3009876543"

    def test_user_update_all_fields(self):
        """UserUpdate acepta todos los campos opcionales"""
        user_update = UserUpdate(
            nombre="Juan Carlos",
            apellido="Pérez González", 
            user_type=UserType.VENDEDOR,
            cedula="87654321",
            telefono="3009876543",
            ciudad="Medellín",
            empresa="Mi Nueva Empresa",
            direccion="Calle Nueva 123",
            is_verified=True
        )
        assert user_update.nombre == "Juan Carlos"
        assert user_update.user_type == UserType.VENDEDOR
        assert user_update.is_verified is True


class TestValidatorsV2:
    """Tests para validadores Pydantic V2"""

    def test_cedula_validator_valid(self):
        """Validador de cédula acepta formatos válidos"""
        valid_cedulas = ["12345678", "1234567890", "123456"]

        for cedula in valid_cedulas:
            user = UserBase(
                email="test@test.com",
                nombre="Test",
                apellido="User",
                cedula=cedula
            )
            assert user.cedula == cedula

    def test_cedula_validator_invalid(self):
        """Validador de cédula rechaza formatos inválidos"""
        invalid_cedulas = ["123", "12345678901", "abc123", ""]

        for cedula in invalid_cedulas:
            with pytest.raises(ValidationError):
                UserBase(
                    email="test@test.com",
                    nombre="Test", 
                    apellido="User",
                    cedula=cedula
                )

    def test_telefono_validator_valid(self):
        """Validador de teléfono acepta formatos válidos"""
        valid_phones = [
            "3001234567",
            "+57 300 123 4567", 
            "300 123 4567",
            "6012345678"  # Fijo Bogotá
        ]

        for phone in valid_phones:
            user = UserBase(
                email="test@test.com",
                nombre="Test",
                apellido="User", 
                telefono=phone
            )
            assert user.telefono.startswith("+57")

    def test_telefono_validator_invalid(self):
        """Validador de teléfono rechaza formatos inválidos"""
        invalid_phones = ["123", "12345678901", "+1 555 123 4567", "abc"]

        for phone in invalid_phones:
            with pytest.raises(ValidationError):
                UserBase(
                    email="test@test.com",
                    nombre="Test",
                    apellido="User",
                    telefono=phone
                )

    def test_password_validator_strong(self):
        """Validador de password acepta passwords fuertes"""
        strong_passwords = [
            "Password123",
            "MiClave2025!",
            "Secure@Pass1"
        ]

        for password in strong_passwords:
            user = UserCreate(
                email="test@test.com",
                nombre="Test",
                apellido="User",
                password=password
            )
            assert user.password == password

    def test_password_validator_weak(self):
        """Validador de password rechaza passwords débiles"""
        weak_passwords = [
            "123",
            "password",
            "PASSWORD", 
            "Password",
            "12345678"
        ]

        for password in weak_passwords:
            with pytest.raises(ValidationError):
                UserCreate(
                    email="test@test.com",
                    nombre="Test",
                    apellido="User", 
                    password=password
                )


class TestUserResponseAlias:
    """Tests para UserResponse como alias de UserRead"""

    def test_user_response_is_alias(self):
        """UserResponse es exactamente UserRead"""
        assert UserResponse == UserRead

    def test_user_response_functionality(self):
        """UserResponse funciona como UserRead"""
        user_data = {
            "id": uuid4(),
            "email": "test@test.com",
            "nombre": "Test",
            "apellido": "User",
            "user_type": UserType.COMPRADOR,
            "is_active": True,
            "is_verified": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        user_response = UserResponse(**user_data)
        user_read = UserRead(**user_data)

        assert user_response.id == user_read.id
        assert user_response.email == user_read.email


class TestUUIDCompatibility:
    """Tests para compatibilidad con UUID"""

    def test_user_read_uuid_field(self):
        """UserRead acepta UUID correctamente"""
        user_id = uuid4()
        user_data = {
            "id": user_id,
            "email": "test@test.com", 
            "nombre": "Test",
            "apellido": "User",
            "user_type": UserType.COMPRADOR,
            "is_active": True,
            "is_verified": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        user = UserRead(**user_data)
        assert isinstance(user.id, UUID)
        assert user.id == user_id

    def test_user_read_rejects_int_id(self):
        """UserRead rechaza id como entero"""
        user_data = {
            "id": 123,  # int en lugar de UUID
            "email": "test@test.com",
            "nombre": "Test", 
            "apellido": "User",
            "user_type": UserType.COMPRADOR,
            "is_active": True,
            "is_verified": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        with pytest.raises(ValidationError):
            UserRead(**user_data)


class TestSchemaInheritance:
    """Tests para herencia correcta de schemas"""

    def test_user_create_inherits_userbase(self):
        """UserCreate hereda correctamente de UserBase"""
        assert issubclass(UserCreate, UserBase)

        # UserCreate debe tener todos los campos de UserBase + password
        base_fields = set(UserBase.model_fields.keys())
        create_fields = set(UserCreate.model_fields.keys())

        assert base_fields.issubset(create_fields)
        assert "password" in create_fields

    def test_user_read_inherits_userbase(self):
        """UserRead hereda correctamente de UserBase"""
        assert issubclass(UserRead, UserBase)

        # UserRead debe tener todos los campos de UserBase + campos del sistema
        base_fields = set(UserBase.model_fields.keys())
        read_fields = set(UserRead.model_fields.keys())

        assert base_fields.issubset(read_fields)
        assert "id" in read_fields
        assert "created_at" in read_fields

    def test_user_indb_inherits_userread(self):
        """UserInDB hereda correctamente de UserRead"""
        assert issubclass(UserInDB, UserRead)

        # UserInDB debe tener todos los campos de UserRead + password_hash
        read_fields = set(UserRead.model_fields.keys())
        indb_fields = set(UserInDB.model_fields.keys())

        assert read_fields.issubset(indb_fields)
        assert "password_hash" in indb_fields


if __name__ == "__main__":
    pytest.main([__file__])
