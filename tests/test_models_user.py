# ~/tests/test_models_user.py
# ---------------------------------------------------------------------------------------------
# MeStore - Tests para Modelo User
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: test_models_user.py
# Ruta: ~/tests/test_models_user.py
# Autor: Jairo
# Fecha de Creación: 2025-07-25
# Última Actualización: 2025-07-25
# Versión: 1.0.0
# Propósito: Tests completos para modelo SQLAlchemy User
#            Valida campos, constraints, timestamps y funcionalidad
#
# Modificaciones:
# 2025-07-25 - Tests iniciales para modelo User básico
#
# ---------------------------------------------------------------------------------------------

"""
Tests completos para el modelo SQLAlchemy User.

Este módulo contiene tests exhaustivos para:
- Creación básica de usuarios
- Validación de constraints (email único)
- Timestamps automáticos
- Representaciones string (__repr__, __str__)
- Integración con Base SQLAlchemy
"""

import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.models.user import User, UserType
from app.models.user import User, UserType
from app.models.base import Base


class TestUserModel:
    """Tests para el modelo User."""

    def test_user_creation_basic(self, test_db_session):
        """Test creación básica de usuario con campos mínimos."""
        # Arrange
        email = "test@example.com"
        password_hash = "hashed_password_123"

        # Act
        user = User(
            email=email,
            password_hash=password_hash
        )
        test_db_session.add(user)
        test_db_session.commit()

        # Assert
        assert user.id is not None
        assert user.email == email
        assert user.password_hash == password_hash
        assert user.is_active is True  # Default value
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    def test_user_creation_with_all_fields(self, test_db_session):
        """Test creación de usuario con todos los campos especificados."""
        # Arrange
        user_data = {
            "email": "complete@example.com",
            "password_hash": "hashed_password_456",
            "is_active": False,
            "user_type": UserType.VENDEDOR
        }

        # Act
        user = User(**user_data)
        test_db_session.add(user)
        test_db_session.commit()

        # Assert
        assert user.email == user_data["email"]
        assert user.password_hash == user_data["password_hash"]
        assert user.is_active == user_data["is_active"]
        assert user.user_type == user_data["user_type"]
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_email_unique_constraint(self, test_db_session):
        """Test que el email debe ser único en la tabla users."""
        # Arrange
        email = "unique@example.com"

        # Act - Crear primer usuario
        user1 = User(email=email, password_hash="hash1")
        test_db_session.add(user1)
        test_db_session.commit()

        # Act & Assert - Intentar crear segundo usuario con mismo email
        user2 = User(email=email, password_hash="hash2")
        test_db_session.add(user2)

        with pytest.raises(IntegrityError):
            test_db_session.commit()

    def test_user_required_fields(self, test_db_session):
        """Test que campos obligatorios no pueden ser None."""
        # Test email requerido
        with pytest.raises(IntegrityError):
            user = User(email=None, password_hash="hash")
            test_db_session.add(user)
            test_db_session.commit()

        test_db_session.rollback()

        # Test password_hash requerido
        with pytest.raises(IntegrityError):
            user = User(email="test@example.com", password_hash=None)
            test_db_session.add(user)
            test_db_session.commit()

    def test_user_timestamps_automatic(self, test_db_session):
        """Test que timestamps se crean automáticamente."""
        # Arrange & Act
        user = User(email="timestamp@example.com", password_hash="hash")
        creation_time = datetime.now()

        test_db_session.add(user)
        test_db_session.commit()

        # Assert
        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.created_at <= creation_time or user.created_at >= creation_time
        assert user.updated_at <= creation_time or user.updated_at >= creation_time

        # Test que created_at y updated_at son similares en creación
        time_diff = abs((user.updated_at - user.created_at).total_seconds())
        assert time_diff < 1  # Menos de 1 segundo de diferencia

    def test_user_repr_method(self, test_db_session):
        """Test representación __repr__ del modelo User."""
        # Arrange
        user = User(
            email="repr@example.com",
            password_hash="hash",
            is_active=True
        )
        test_db_session.add(user)
        test_db_session.commit()

        # Act
        repr_string = repr(user)

        # Assert
        assert f"User(id={user.id}" in repr_string
        assert "email='repr@example.com'" in repr_string
        assert "active=True" in repr_string

    def test_user_str_method(self, test_db_session):
        """Test representación __str__ del modelo User."""
        # Arrange - Usuario activo
        active_user = User(
            email="active@example.com",
            password_hash="hash",
            is_active=True
        )
        test_db_session.add(active_user)
        test_db_session.commit()

        # Act & Assert - Usuario activo
        str_active = str(active_user)
        assert "Usuario active@example.com (activo)" == str_active

        # Arrange - Usuario inactivo
        inactive_user = User(
            email="inactive@example.com",
            password_hash="hash",
            is_active=False
        )
        test_db_session.add(inactive_user)
        test_db_session.commit()

        # Act & Assert - Usuario inactivo
        str_inactive = str(inactive_user)
        assert "Usuario inactive@example.com (inactivo)" == str_inactive

    def test_user_inherits_from_base(self):
        """Test que User hereda correctamente de Base."""
        # Assert
        assert issubclass(User, Base)
        assert hasattr(User, '__tablename__')
        assert User.__tablename__ == 'users'

    def test_user_table_indexes(self):
        """Test que la tabla tiene los índices apropiados."""
        # Assert
        # Verificar que id tiene índice (primary key)
        id_column = User.__table__.columns['id']
        assert id_column.primary_key is True
        assert id_column.index is True

        # Verificar que email tiene índice
        email_column = User.__table__.columns['email']
        assert email_column.index is True
        assert email_column.unique is True


class TestUserModelIntegration:
    """Tests de integración del modelo User con SQLAlchemy."""

    def test_user_query_by_email(self, test_db_session):
        """Test consulta de usuario por email."""
        # Arrange
        email = "query@example.com"
        user = User(email=email, password_hash="hash")
        test_db_session.add(user)
        test_db_session.commit()

        # Act
        found_user = test_db_session.query(User).filter(User.email == email).first()

        # Assert
        assert found_user is not None
        assert found_user.email == email
        assert found_user.id == user.id

    def test_user_query_active_users(self, test_db_session):
        """Test consulta de usuarios activos."""
        # Arrange
        active_user = User(email="active@test.com", password_hash="hash", is_active=True)
        inactive_user = User(email="inactive@test.com", password_hash="hash", is_active=False)

        test_db_session.add_all([active_user, inactive_user])
        test_db_session.commit()

        # Act
        active_users = test_db_session.query(User).filter(User.is_active == True).all()

        # Assert
        assert len(active_users) >= 1
        assert active_user in active_users
        assert inactive_user not in active_users

    def test_user_count_total(self, test_db_session):
        """Test contar total de usuarios en la tabla."""
        # Arrange
        initial_count = test_db_session.query(User).count()

        users = [
            User(email=f"user{i}@test.com", password_hash="hash")
            for i in range(3)
        ]
        test_db_session.add_all(users)
        test_db_session.commit()

        # Act
        final_count = test_db_session.query(User).count()

        # Assert
        assert final_count == initial_count + 3



class TestUserTypeEnum:
    """Tests específicos para el enum UserType."""

    def test_user_type_enum_values(self):
        """Test que UserType enum tiene los valores correctos."""
        # Assert
        assert UserType.COMPRADOR.value == "comprador"
        assert UserType.VENDEDOR.value == "vendedor"
        assert len(list(UserType)) == 2

    def test_user_type_default_value(self, test_db_session):
        """Test que user_type tiene valor por defecto COMPRADOR."""
        # Arrange & Act
        user = User(email="default@test.com", password_hash="hash")
        test_db_session.add(user)
        test_db_session.commit()

        # Assert
        assert user.user_type == UserType.COMPRADOR

    def test_user_type_vendedor(self, test_db_session):
        """Test creación de usuario tipo VENDEDOR."""
        # Arrange & Act
        user = User(
            email="vendedor@test.com",
            password_hash="hash",
            user_type=UserType.VENDEDOR
        )
        test_db_session.add(user)
        test_db_session.commit()

        # Assert
        assert user.user_type == UserType.VENDEDOR

    def test_user_query_by_user_type(self, test_db_session):
        """Test consulta de usuarios por tipo."""
        # Arrange
        comprador = User(email="comp@test.com", password_hash="hash", user_type=UserType.COMPRADOR)
        vendedor = User(email="vend@test.com", password_hash="hash", user_type=UserType.VENDEDOR)

        test_db_session.add_all([comprador, vendedor])
        test_db_session.commit()

        # Act
        compradores = test_db_session.query(User).filter(User.user_type == UserType.COMPRADOR).all()
        vendedores = test_db_session.query(User).filter(User.user_type == UserType.VENDEDOR).all()

        # Assert
        assert comprador in compradores
        assert vendedor in vendedores
        assert comprador not in vendedores
        assert vendedor not in compradores