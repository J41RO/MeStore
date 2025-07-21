# ~/tests/unit/test_security.py
# ---------------------------------------------------------------------------------------------
# MeStore - Tests de Seguridad
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------

"""
Tests unitarios para el módulo de seguridad.

Verifica el correcto funcionamiento de:
- Hashing de contraseñas con bcrypt
- Verificación de contraseñas
- Generación y decodificación de tokens JWT
"""

import pytest
from datetime import timedelta

from app.core.security import create_access_token, decode_access_token
from app.utils.password import hash_password, verify_password
from app.utils.password import hash_password, verify_password


class TestPasswordSecurity:
    """Tests para funciones de manejo de contraseñas."""

    def test_get_password_hash_generates_valid_hash(self):
        """Test que get_password_hash genera un hash válido."""
        password = "test_password_123"
        hashed = hash_password(password)

        # Verificar que el hash se generó
        assert hashed is not None
        assert len(hashed) > 0

        # Verificar que el hash es diferente al password original
        assert hashed != password

        # Verificar longitud típica de bcrypt (60 caracteres)
        assert len(hashed) == 60

        # Verificar que empieza con el prefijo de bcrypt
        assert hashed.startswith("$2b$")

    def test_verify_password_returns_true_for_valid_combination(self):
        """Test que verify_password devuelve True para combinación válida."""
        password = "my_secure_password_456"
        hashed = hash_password(password)

        # Verificar que la contraseña correcta es válida
        assert verify_password(password, hashed) is True

        # Verificar que una contraseña incorrecta es inválida
        assert verify_password("wrong_password", hashed) is False

        # Verificar que una cadena vacía es inválida
        assert verify_password("", hashed) is False

    def test_different_passwords_generate_different_hashes(self):
        """Test que contraseñas diferentes generan hashes diferentes."""
        password1 = "password_one"
        password2 = "password_two"

        hash1 = hash_password(password1)
        hash2 = hash_password(password2)

        # Los hashes deben ser diferentes
        assert hash1 != hash2

        # Cada uno debe verificar solo con su contraseña original
        assert verify_password(password1, hash1) is True
        assert verify_password(password1, hash2) is False
        assert verify_password(password2, hash1) is False
        assert verify_password(password2, hash2) is True


class TestJWTTokens:
    """Tests para funciones de tokens JWT."""

    def test_create_access_token_generates_jwt_and_can_be_decoded(self):
        """Test que create_access_token genera JWT válido que puede ser decodificado."""
        test_data = {"sub": "test@example.com", "user_id": 123}

        # Generar token
        token = create_access_token(test_data)

        # Verificar que el token se generó
        assert token is not None
        assert len(token) > 0
        assert isinstance(token, str)

        # Verificar que tiene estructura de JWT (3 partes separadas por puntos)
        token_parts = token.split(".")
        assert len(token_parts) == 3

        # Decodificar y verificar contenido
        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded["sub"] == "test@example.com"
        assert decoded["user_id"] == 123
        assert "exp" in decoded  # Debe tener fecha de expiración

    def test_create_access_token_with_custom_expiration(self):
        """Test que create_access_token respeta el tiempo de expiración personalizado."""
        test_data = {"sub": "test@example.com"}
        custom_delta = timedelta(minutes=60)

        # Generar token con expiración personalizada
        token = create_access_token(test_data, expires_delta=custom_delta)

        # Decodificar y verificar
        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded["sub"] == "test@example.com"
        assert "exp" in decoded

    def test_decode_access_token_returns_none_for_invalid_token(self):
        """Test que decode_access_token retorna None para tokens inválidos."""
        # Token completamente inválido
        invalid_token = "invalid.jwt.token"
        assert decode_access_token(invalid_token) is None

        # Token vacío
        assert decode_access_token("") is None

        # Token con formato incorrecto
        malformed_token = "header.payload"  # Solo 2 partes
        assert decode_access_token(malformed_token) is None


class TestSecurityIntegration:
    """Tests de integración para verificar el flujo completo."""

    def test_complete_auth_flow_simulation(self):
        """Test que simula flujo completo de autenticación."""
        # Simular registro de usuario
        user_email = "user@example.com"
        user_password = "secure_password_789"

        # 1. Hash de contraseña (como en registro)
        password_hash = hash_password(user_password)

        # 2. Verificación de contraseña (como en login)
        login_successful = verify_password(user_password, password_hash)
        assert login_successful is True

        # 3. Generación de token (como después de login exitoso)
        token_data = {"sub": user_email}
        access_token = create_access_token(token_data)

        # 4. Validación de token (como en rutas protegidas)
        token_payload = decode_access_token(access_token)
        assert token_payload is not None
        assert token_payload["sub"] == user_email

        # 5. Verificar que password incorrecto falla
        wrong_login = verify_password("wrong_password", password_hash)
        assert wrong_login is False