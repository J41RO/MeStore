# ~/tests/unit/test_jwt_tokens.py
# ---------------------------------------------------------------------------------------------
# MeStore - Tests Unitarios para JWT Tokens
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: test_jwt_tokens.py
# Ruta: ~/tests/unit/test_jwt_tokens.py
# Autor: Jairo
# Fecha de Creación: 2025-07-21
# Última Actualización: 2025-07-21
# Versión: 1.0.0
# Propósito: Tests unitarios para funciones JWT de access y refresh tokens
#            Valida generación, decodificación y expiración de tokens
#
# Modificaciones:
# 2025-07-21 - Creación inicial de tests JWT
#
# ---------------------------------------------------------------------------------------------

"""
Tests unitarios para el sistema JWT de MeStore.

Este módulo contiene tests para:
- Generación de access tokens con sub y exp
- Generación de refresh tokens correctos
- Decodificación válida de ambos tipos de tokens
- Validación de expiración de tokens
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from app.core.security import (
   create_access_token,
   decode_access_token,
   create_refresh_token,
   decode_refresh_token
)


class TestJWTTokens:
   """Suite de tests para funciones JWT."""

   def test_create_access_token_includes_sub_and_exp(self):
       """Test que access token incluye subject y expiration."""
       # Arrange
       test_data = {"sub": "test@example.com"}

       # Act
       token = create_access_token(test_data)
       payload = decode_access_token(token)

       # Assert
       assert payload is not None
       assert payload["sub"] == "test@example.com"
       assert "exp" in payload
       assert isinstance(payload["exp"], int)

       # Verificar que exp es tiempo futuro
       current_time = datetime.now(timezone.utc).timestamp()
       assert payload["exp"] > current_time

   def test_create_refresh_token_generated_correctly(self):
       """Test que refresh token se genera correctamente con tipo."""
       # Arrange
       test_data = {"sub": "user@example.com"}

       # Act
       token = create_refresh_token(test_data)
       payload = decode_refresh_token(token)

       # Assert
       assert payload is not None
       assert payload["sub"] == "user@example.com"
       assert payload["type"] == "refresh"
       assert "exp" in payload

       # Verificar que exp es tiempo futuro (7 días)
       current_time = datetime.now(timezone.utc).timestamp()
       assert payload["exp"] > current_time

       # Verificar que refresh token dura más que access token
       access_token = create_access_token(test_data)
       access_payload = decode_access_token(access_token)
       assert payload["exp"] > access_payload["exp"]

   def test_decode_access_and_refresh_tokens_valid(self):
       """Test decodificación válida de access y refresh tokens."""
       # Arrange
       test_data = {"sub": "decode@example.com", "user_id": 123}

       # Act
       access_token = create_access_token(test_data)
       refresh_token = create_refresh_token(test_data)

       access_payload = decode_access_token(access_token)
       refresh_payload = decode_refresh_token(refresh_token)

       # Assert - Access Token
       assert access_payload is not None
       assert access_payload["sub"] == "decode@example.com"
       assert access_payload["user_id"] == 123
       assert "type" not in access_payload  # Access tokens no tienen type

       # Assert - Refresh Token
       assert refresh_payload is not None
       assert refresh_payload["sub"] == "decode@example.com"
       assert refresh_payload["user_id"] == 123
       assert refresh_payload["type"] == "refresh"

   def test_expired_tokens_invalidated_correctly(self):
       """Test que tokens expirados son invalidados correctamente."""
       # Arrange - Crear token con expiración inmediata
       test_data = {"sub": "expired@example.com"}
       expired_delta = timedelta(seconds=-1)  # Expirado hace 1 segundo

       # Act
       expired_access_token = create_access_token(test_data, expired_delta)

       # Assert
       payload = decode_access_token(expired_access_token)
       assert payload is None  # Token expirado debe retornar None

   def test_invalid_tokens_return_none(self):
       """Test que tokens inválidos retornan None."""
       # Arrange
       invalid_tokens = [
           "token_completamente_inválido",
           "Bearer invalid.token.here",
           "",
           "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.invalid.signature"
       ]

       # Act & Assert
       for invalid_token in invalid_tokens:
           access_result = decode_access_token(invalid_token)
           refresh_result = decode_refresh_token(invalid_token)

           assert access_result is None
           assert refresh_result is None

   def test_refresh_token_type_validation(self):
       """Test que decode_refresh_token valida el tipo del token."""
       # Arrange - Crear access token (sin type="refresh")
       test_data = {"sub": "typetest@example.com"}
       access_token = create_access_token(test_data)

       # Act - Intentar decodificar access token como refresh
       result = decode_refresh_token(access_token)

       # Assert - Debe retornar None porque no es tipo refresh
       assert result is None

   def test_custom_expiration_time_respected(self):
       """Test que tiempo de expiración personalizado es respetado."""
       # Arrange
       test_data = {"sub": "custom@example.com"}
       custom_delta = timedelta(minutes=60)  # 1 hora

       # Act
       token = create_access_token(test_data, custom_delta)
       payload = decode_access_token(token)

       # Assert
       assert payload is not None

       # Calcular tiempo esperado de expiración (aproximadamente)
       expected_exp = (datetime.now(timezone.utc) + custom_delta).timestamp()
       actual_exp = payload["exp"]

       # Debe estar dentro de un rango de 5 segundos
       assert abs(actual_exp - expected_exp) < 5
