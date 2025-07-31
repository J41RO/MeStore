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
        
        # Crear usuario con datos válidos debe ser exitoso
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
        """Test que strings vacíos son rechazados por validación min_length"""
        user_data = {
            "email": "test@example.com",
            "nombre": "",  # String vacío
            "apellido": ""  # String vacío
        }
        
        # String vacíos deben fallar con min_length=2
        with pytest.raises(ValidationError) as exc_info:
            user = UserBase(**user_data)

        # Verificar que ambos campos fallan por ser muy cortos
        errors = exc_info.value.errors()
        field_errors = [error['loc'][0] for error in errors]
        assert 'nombre' in field_errors
        assert 'apellido' in field_errors

        # Verificar tipo de error específico
        error_types = [error['type'] for error in errors]
        assert 'string_too_short' in error_types
    
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
        """Test que nombres muy largos son rechazados por max_length=50"""
        user_data = {
            "email": "test@example.com",
            "nombre": "A" * 100,  # Nombre muy largo (excede max_length=50)
            "apellido": "B" * 100  # Apellido muy largo (excede max_length=50)
        }
        
        # Nombres de 100 caracteres deben ser rechazados por max_length=50
        with pytest.raises(ValidationError) as exc_info:
            UserBase(**user_data)
        
        # Verificar que ambos campos fallan por exceder longitud máxima
        errors = exc_info.value.errors()
        field_errors = [error["loc"][0] for error in errors]
        assert "nombre" in field_errors
        assert "apellido" in field_errors
        
        # Verificar tipo de error específico
        error_types = [error["type"] for error in errors]
        assert "string_too_long" in error_types


class TestUserCreate:
    """Tests para el schema UserCreate"""
    
    def test_valid_user_create(self):
        """Test de creación válida de UserCreate"""
        user_data = {
            "email": "nuevo@example.com",
            "nombre": "Ana",
            "apellido": "González",
            "user_type": UserType.VENDEDOR,
            "password": "Password123"
        }
        
        user = UserCreate(**user_data)
        
        # Verificar herencia de UserBase
        assert user.email == "nuevo@example.com"
        assert user.nombre == "Ana"
        assert user.apellido == "González"
        assert user.user_type == UserType.VENDEDOR
        
        # Verificar campo adicional
        assert user.password == "Password123"
        assert isinstance(user.password, str)
    
    def test_user_create_with_default_type(self):
        """Test de UserCreate con tipo por defecto"""
        user_data = {
            "email": "default@example.com",
            "nombre": "Carlos",
            "apellido": "Rodríguez",
            "password": "SecurePass123"
        }
        
        user = UserCreate(**user_data)
        
        assert user.user_type == UserType.COMPRADOR  # Valor por defecto
        assert user.password == "SecurePass123"
    
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
    
