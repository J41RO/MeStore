# ~/tests/schemas/test_user.py
# ---------------------------------------------------------------------------------------------
# MeStore - Tests para Esquemas de Usuario
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
"""
Tests completos para User Schemas

Cubre:
- UserBase: validación de campos base
- UserCreate: validación de datos de creación
- UserRead: serialización de datos de lectura
- Validaciones de email, tipos, campos requeridos
- Casos límite y errores de validación
- Integración con UserType enum
"""

import pytest
from pydantic import ValidationError
from app.schemas.user import UserBase, UserCreate, UserRead
from app.models.user import UserType


class TestUserBase:
    """Tests para el schema UserBase"""
    
    def test_valid_user_base_creation(self):
        """Test de creación válida de UserBase"""
        user_data = {
            "email": "test@example.com",
            "nombre": "Juan",
            "apellido": "Pérez",
            "user_type": UserType.COMPRADOR
        }
        
        user = UserBase(**user_data)
        
        # Verificar que todos los campos se asignan correctamente
        assert user.email == "test@example.com"
        assert user.nombre == "Juan"
        assert user.apellido == "Pérez"
        assert user.user_type == UserType.COMPRADOR
        
        # Verificar tipos
        assert isinstance(user.email, str)
        assert isinstance(user.nombre, str)
        assert isinstance(user.apellido, str)
        assert isinstance(user.user_type, UserType)
    
    def test_user_base_default_user_type(self):
        """Test del tipo de usuario por defecto"""
        user_data = {
            "email": "test@example.com",
            "nombre": "Juan",
            "apellido": "Pérez"
            # user_type omitido intencionalmente
        }
        
        user = UserBase(**user_data)
        
        # Verificar que se asigna el tipo por defecto
        assert user.user_type == UserType.COMPRADOR
    
    def test_user_base_vendedor_type(self):
        """Test con tipo de usuario VENDEDOR"""
        user_data = {
            "email": "vendedor@example.com",
            "nombre": "María",
            "apellido": "García",
            "user_type": UserType.VENDEDOR
        }
        
        user = UserBase(**user_data)
        
        assert user.user_type == UserType.VENDEDOR
    
    def test_user_base_invalid_email(self):
        """Test de validación de email inválido"""
        user_data = {
            "email": "email_invalido",  # Email sin formato válido
            "nombre": "Juan",
            "apellido": "Pérez"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserBase(**user_data)
        
        # Verificar que el error es de email
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any("email" in str(error).lower() for error in errors)
    
    def test_user_base_missing_required_fields(self):
        """Test de campos requeridos faltantes"""
        # Test faltando email
        with pytest.raises(ValidationError) as exc_info:
            UserBase(nombre="Juan", apellido="Pérez")
        
        errors = exc_info.value.errors()
        field_errors = [error['loc'][0] for error in errors]
        assert 'email' in field_errors
        
        # Test faltando nombre
        with pytest.raises(ValidationError) as exc_info:
            UserBase(email="test@example.com", apellido="Pérez")
        
        errors = exc_info.value.errors()
        field_errors = [error['loc'][0] for error in errors]
        assert 'nombre' in field_errors
        
        # Test faltando apellido
        with pytest.raises(ValidationError) as exc_info:
            UserBase(email="test@example.com", nombre="Juan")
        
        errors = exc_info.value.errors()
        field_errors = [error['loc'][0] for error in errors]
        assert 'apellido' in field_errors
    
    def test_user_base_empty_strings(self):
        """Test con strings vacíos"""
        user_data = {
            "email": "test@example.com",
            "nombre": "",  # String vacío
            "apellido": ""  # String vacío
        }
        
        # Pydantic permite strings vacíos por defecto
        user = UserBase(**user_data)
        assert user.nombre == ""
        assert user.apellido == ""
    
    def test_user_base_special_characters(self):
        """Test con caracteres especiales en nombres"""
        user_data = {
            "email": "test@example.com",
            "nombre": "José María",
            "apellido": "García-López"
        }
        
        user = UserBase(**user_data)
        assert user.nombre == "José María"
        assert user.apellido == "García-López"
    
    def test_user_base_long_names(self):
        """Test con nombres largos"""
        user_data = {
            "email": "test@example.com",
            "nombre": "A" * 100,  # Nombre muy largo
            "apellido": "B" * 100  # Apellido muy largo
        }
        
        user = UserBase(**user_data)
        assert len(user.nombre) == 100
        assert len(user.apellido) == 100


class TestUserCreate:
    """Tests para el schema UserCreate"""
    
    def test_valid_user_create(self):
        """Test de creación válida de UserCreate"""
        user_data = {
            "email": "nuevo@example.com",
            "nombre": "Ana",
            "apellido": "González",
            "user_type": UserType.VENDEDOR,
            "password": "password123"
        }
        
        user = UserCreate(**user_data)
        
        # Verificar herencia de UserBase
        assert user.email == "nuevo@example.com"
        assert user.nombre == "Ana"
        assert user.apellido == "González"
        assert user.user_type == UserType.VENDEDOR
        
        # Verificar campo adicional
        assert user.password == "password123"
        assert isinstance(user.password, str)
    
    def test_user_create_with_default_type(self):
        """Test de UserCreate con tipo por defecto"""
        user_data = {
            "email": "default@example.com",
            "nombre": "Carlos",
            "apellido": "Rodríguez",
            "password": "securepass"
        }
        
        user = UserCreate(**user_data)
        
        assert user.user_type == UserType.COMPRADOR  # Valor por defecto
        assert user.password == "securepass"
    
    def test_user_create_missing_password(self):
        """Test de UserCreate sin password"""
        user_data = {
            "email": "test@example.com",
            "nombre": "Juan",
            "apellido": "Pérez"
            # password omitido intencionalmente
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        
        # Verificar que el error es por password faltante
        errors = exc_info.value.errors()
        field_errors = [error['loc'][0] for error in errors]
        assert 'password' in field_errors
    
    def test_user_create_empty_password(self):
        """Test con password vacío"""
        user_data = {
            "email": "test@example.com",
            "nombre": "Juan",
            "apellido": "Pérez",
            "password": ""  # Password vacío
        }
        
        # Pydantic permite strings vacíos por defecto
        user = UserCreate(**user_data)
        assert user.password == ""
    
    def test_user_create_inherits_base_validations(self):
        """Test que UserCreate hereda validaciones de UserBase"""
        user_data = {
            "email": "email_invalido",  # Email inválido
            "nombre": "Juan",
            "apellido": "Pérez",
            "password": "password123"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        
        # Verificar que falla por email inválido
        errors = exc_info.value.errors()
        assert any("email" in str(error).lower() for error in errors)


class TestUserRead:
    """Tests para el schema UserRead"""
    
    def test_valid_user_read(self):
        """Test de creación válida de UserRead"""
        user_data = {
            "email": "read@example.com",
            "nombre": "Luis",
            "apellido": "Martín",
            "user_type": UserType.COMPRADOR,
            "id": 123,
            "is_active": True,
            "is_verified": False,
            "last_login": None
        }
        
        user = UserRead(**user_data)
        
        # Verificar herencia de UserBase
        assert user.email == "read@example.com"
        assert user.nombre == "Luis"
        assert user.apellido == "Martín"
        assert user.user_type == UserType.COMPRADOR
        
        # Verificar campos adicionales
        assert user.id == 123
        assert user.is_active is True
        assert user.is_verified is False
        assert user.last_login is None
        assert isinstance(user.id, int)
        assert isinstance(user.is_active, bool)
        assert isinstance(user.is_verified, bool)
    
    def test_user_read_inactive_user(self):
        """Test con usuario inactivo"""
        user_data = {
            "email": "inactive@example.com",
            "nombre": "Pedro",
            "apellido": "López",
            "id": 456,
            "is_active": False,
            "is_verified": False,
            "last_login": None
        }
        
        user = UserRead(**user_data)
        
        assert user.is_active is False
        assert user.is_verified is False
        assert user.user_type == UserType.COMPRADOR  # Default
    
    def test_user_read_missing_id(self):
        """Test de UserRead sin id"""
        user_data = {
            "email": "test@example.com",
            "nombre": "Juan",
            "apellido": "Pérez",
            "is_active": True,
            "is_verified": False,
            "last_login": None
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserRead(**user_data)
        
        # Verificar que el error es por id faltante
        errors = exc_info.value.errors()
        field_errors = [error['loc'][0] for error in errors]
        assert 'id' in field_errors
    
    def test_user_read_missing_is_active(self):
        """Test de UserRead sin is_active"""
        user_data = {
            "email": "test@example.com",
            "nombre": "Juan",
            "apellido": "Pérez",
            "id": 789,
            "is_verified": False,
            "last_login": None
            # is_active omitido intencionalmente
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserRead(**user_data)
        
        # Verificar que el error es por is_active faltante
        errors = exc_info.value.errors()
        field_errors = [error['loc'][0] for error in errors]
        assert 'is_active' in field_errors
    
    def test_user_read_invalid_id_type(self):
        """Test con tipo de id inválido"""
        user_data = {
            "email": "test@example.com",
            "nombre": "Juan",
            "apellido": "Pérez",
            "id": "not_an_integer",  # String en lugar de int
            "is_active": True,
            "is_verified": False,
            "last_login": None
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserRead(**user_data)
        
        # Verificar que el error es por tipo de id
        errors = exc_info.value.errors()
        assert any(error['loc'][0] == 'id' for error in errors)
    
    def test_user_read_config_from_attributes(self):
        """Test de la configuración from_attributes"""
        # Verificar que la clase Config existe
        assert hasattr(UserRead, 'Config')
        assert hasattr(UserRead.Config, 'from_attributes')
        assert UserRead.Config.from_attributes is True
    
    def test_user_read_inherits_base_validations(self):
        """Test que UserRead hereda validaciones de UserBase"""
        user_data = {
            "email": "email_invalido",  # Email inválido
            "nombre": "Juan",
            "apellido": "Pérez",
            "id": 123,
            "is_active": True,
            "is_verified": False,
            "last_login": None
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserRead(**user_data)
        
        # Verificar que falla por email inválido
        errors = exc_info.value.errors()
        assert any("email" in str(error).lower() for error in errors)


class TestUserSchemaIntegration:
    """Tests de integración entre schemas"""
    
    def test_create_to_read_conversion_concept(self):
        """Test conceptual de conversión Create -> Read"""
        # Datos de creación
        create_data = {
            "email": "integration@example.com",
            "nombre": "Ana",
            "apellido": "Silva",
            "user_type": UserType.VENDEDOR,
            "password": "secret123"
        }
        
        user_create = UserCreate(**create_data)
        
        # Simular datos que vendrían de la base de datos
        read_data = {
            "email": user_create.email,
            "nombre": user_create.nombre,
            "apellido": user_create.apellido,
            "user_type": user_create.user_type,
            "id": 999,
            "is_active": True,
            "is_verified": False,
            "last_login": None
        }
        
        user_read = UserRead(**read_data)
        
        # Verificar que los datos se mantienen consistentes
        assert user_read.email == user_create.email
        assert user_read.nombre == user_create.nombre
        assert user_read.apellido == user_create.apellido
        assert user_read.user_type == user_create.user_type
        
        # Verificar campos adicionales de read
        assert user_read.id == 999
        assert user_read.is_active is True
        assert user_read.is_verified is False
    
    def test_all_user_types_compatibility(self):
        """Test de compatibilidad con todos los tipos de usuario"""
        for user_type in UserType:
            # Test con UserBase
            base_data = {
                "email": f"{user_type.value}@example.com",
                "nombre": "Test",
                "apellido": "User",
                "user_type": user_type
            }
            
            user_base = UserBase(**base_data)
            assert user_base.user_type == user_type
            
            # Test con UserCreate
            create_data = {**base_data, "password": "testpass"}
            user_create = UserCreate(**create_data)
            assert user_create.user_type == user_type
            
            # Test con UserRead
            read_data = {
                **base_data, 
                "id": 1, 
                "is_active": True,
                "is_verified": False,
                "last_login": None
            }
            user_read = UserRead(**read_data)
            assert user_read.user_type == user_type
    
    def test_schema_serialization(self):
        """Test de serialización de schemas"""
        user_data = {
            "email": "serialize@example.com",
            "nombre": "Test",
            "apellido": "Serialization",
            "user_type": UserType.COMPRADOR,
            "id": 555,
            "is_active": True,
            "is_verified": False,
            "last_login": None
        }
        
        user_read = UserRead(**user_data)
        
        # Test de serialización a dict
        user_dict = user_read.model_dump()
        
        assert isinstance(user_dict, dict)
        assert user_dict["email"] == "serialize@example.com"
        assert user_dict["nombre"] == "Test"
        assert user_dict["apellido"] == "Serialization"
        assert user_dict["user_type"] == UserType.COMPRADOR
        assert user_dict["id"] == 555
        assert user_dict["is_active"] is True
        assert user_dict["is_verified"] is False
        assert user_dict["last_login"] is None
    
    def test_schema_json_serialization(self):
        """Test de serialización JSON"""
        user_data = {
            "email": "json@example.com",
            "nombre": "JSON",
            "apellido": "Test",
            "user_type": UserType.VENDEDOR,
            "id": 777,
            "is_active": False,
            "is_verified": True,
            "last_login": None
        }
        
        user_read = UserRead(**user_data)
        
        # Test de serialización a JSON
        user_json = user_read.model_dump_json()
        
        assert isinstance(user_json, str)
        assert "json@example.com" in user_json
        assert "JSON" in user_json
        assert "Test" in user_json
        assert str(UserType.VENDEDOR.value) in user_json
        assert "777" in user_json
        assert "false" in user_json.lower()  # is_active: false
        assert "true" in user_json.lower()   # is_verified: true


class TestEdgeCases:
    """Tests de casos límite y edge cases"""
    
    def test_unicode_names(self):
        """Test con nombres Unicode"""
        user_data = {
            "email": "unicode@example.com",
            "nombre": "José María",
            "apellido": "García-Müller",
            "user_type": UserType.COMPRADOR
        }
        
        user = UserBase(**user_data)
        
        assert user.nombre == "José María"
        assert user.apellido == "García-Müller"
    
    def test_email_edge_cases(self):
        """Test de casos límite de email"""
        valid_emails = [
            "simple@example.com",
            "very.common@example.com",
            "disposable.style.email.with+symbol@example.com",
            "x@example.com",
            "example@s.example"
        ]
        
        for email in valid_emails:
            user_data = {
                "email": email,
                "nombre": "Test",
                "apellido": "User"
            }
            
            user = UserBase(**user_data)
            assert user.email == email
    
    def test_password_edge_cases(self):
        """Test de casos límite de password"""
        passwords = [
            "a",  # Password de 1 carácter
            "A" * 1000,  # Password muy largo
            "special!@#$%^&*()chars",  # Caracteres especiales
            "密码",  # Caracteres Unicode
            "pass word with spaces"  # Espacios
        ]
        
        for password in passwords:
            user_data = {
                "email": "test@example.com",
                "nombre": "Test",
                "apellido": "User",
                "password": password
            }
            
            user = UserCreate(**user_data)
            assert user.password == password