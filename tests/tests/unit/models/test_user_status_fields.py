# ~/tests/test_user_status_fields.py
import uuid
# ---------------------------------------------------------------------------------------------
# MeStore - Tests para campos de estado de User
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: test_user_status_fields.py
# Ruta: ~/tests/test_user_status_fields.py
# Autor: Jairo
# Fecha de Creación: 2025-07-26
# Última Actualización: 2025-07-26
# Versión: 1.0.0
# Propósito: Tests específicos para campos de estado is_verified y last_login
#
# Modificaciones:
# 2025-07-26 - Creación inicial de tests para campos de estado
#
# ---------------------------------------------------------------------------------------------

"""
Tests para campos de estado del modelo User.

Este módulo contiene tests específicos para verificar:
- Campo is_verified con default False
- Campo last_login como opcional
- Método to_dict() incluyendo nuevos campos
- Backward compatibility con usuarios existentes
"""

import pytest
from datetime import datetime, timezone
from app.models.user import User, UserType
from app.schemas.user import UserBase, UserRead


class TestUserStatusFields:
    """Tests para campos de estado is_verified y last_login."""

    def test_is_verified_default_false(self):
        """Test que is_verified tiene default False."""
        user_data = {
            'email': 'test@example.com',
            'password_hash': 'hashed_password',
            'nombre': 'Juan',
            'apellido': 'Pérez'
        }
        user = User(**user_data)

        # Verificar default value
        assert user.is_verified is False
        assert hasattr(user, 'is_verified')

    def test_last_login_nullable(self):
        """Test que last_login es nullable."""
        user_data = {
            'email': 'test@example.com',
            'password_hash': 'hashed_password',
            'nombre': 'Juan',
            'apellido': 'Pérez'
        }
        user = User(**user_data)

        # Verificar que puede ser None
        assert user.last_login is None
        assert hasattr(user, 'last_login')

    def test_last_login_can_be_set(self):
        """Test que last_login puede asignarse datetime."""
        now = datetime.now(timezone.utc)
        user_data = {
            'email': 'test@example.com',
            'password_hash': 'hashed_password',
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'last_login': now,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        user = User(**user_data)

        assert user.last_login == now

    def test_to_dict_includes_status_fields(self):
        """Test que to_dict() incluye is_verified y last_login."""
        now = datetime.now(timezone.utc)
        user_data = {
            'email': 'test@example.com',
            'password_hash': 'hashed_password',
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'is_verified': True,
            'last_login': now,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        user = User(**user_data)
        user_dict = user.to_dict()

        # Verificar que incluye los campos nuevos
        assert 'is_verified' in user_dict
        assert 'last_login' in user_dict
        assert user_dict['is_verified'] is True
        assert user_dict['last_login'] == now.isoformat()

    def test_to_dict_with_none_last_login(self):
        """Test que to_dict() maneja last_login=None correctamente."""
        user_data = {
            'email': 'test@example.com',
            'password_hash': 'hashed_password',
            'nombre': 'Juan',
            'apellido': 'Pérez'
        }
        user = User(**user_data)
        user_dict = user.to_dict()

        # Verificar que last_login es None en dict
        assert user_dict['last_login'] is None

    def test_userbase_schema_includes_is_verified(self):
        """Test que UserBase schema incluye is_verified."""
        user_data = {
            'email': 'test@example.com',
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'user_type': UserType.COMPRADOR
        }
        user_base = UserBase(**user_data)

        # Verificar default is_verified=False
        assert user_base.is_verified is False
        assert hasattr(user_base, 'is_verified')

    def test_userread_schema_includes_status_fields(self):
        """Test que UserRead schema incluye ambos campos."""
        now = datetime.now(timezone.utc)
        user_data = {
            'id': str(uuid.uuid4()),
            'email': 'test@example.com',
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'user_type': UserType.COMPRADOR,
            'is_active': True,
            'is_verified': True,
            'last_login': now,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        user_read = UserRead(**user_data)

        # Verificar que incluye todos los campos de estado
        assert user_read.is_active is True
        assert user_read.is_verified is True
        assert user_read.last_login == now