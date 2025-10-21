# ~/tests/test_user_colombian_fields.py
# Test específicos para campos colombianos del modelo User

import pytest
from uuid import uuid4
from app.models.user import User, UserType


def test_user_creation_with_colombian_fields():
    """Test crear usuario con campos colombianos"""
    user_data = {
        'id': uuid4(),
        'email': 'test@colombia.com',
        'password_hash': 'hashed_password',
        'nombre': 'Juan',
        'apellido': 'Pérez',
        'user_type': UserType.BUYER,
        'cedula': '12345678',
        'telefono': '+57 300 123 4567',
        'ciudad': 'Bogotá'
    }

    user = User(**user_data)

    # Verificar campos colombianos
    assert user.cedula == '12345678'
    assert user.telefono == '+57 300 123 4567'
    assert user.ciudad == 'Bogotá'


def test_user_creation_without_colombian_fields():
    """Test crear usuario sin campos colombianos (opcionales)"""
    user_data = {
        'id': uuid4(),
        'email': 'test2@colombia.com',
        'password_hash': 'hashed_password',
        'nombre': 'María',
        'apellido': 'García',
        'user_type': UserType.VENDOR
    }

    user = User(**user_data)

    # Verificar campos colombianos son None por defecto
    assert user.cedula is None
    assert user.telefono is None
    assert user.ciudad is None


def test_user_to_dict_includes_colombian_fields():
    """Test que to_dict() incluye campos colombianos"""
    user_data = {
        'id': uuid4(),
        'email': 'test3@colombia.com',
        'password_hash': 'hashed_password',
        'nombre': 'Carlos',
        'apellido': 'López',
        'user_type': UserType.BUYER,
        'cedula': '87654321',
        'telefono': '+57 301 987 6543',
        'ciudad': 'Medellín'
    }

    user = User(**user_data)
    user_dict = user.to_dict()

    # Verificar que campos colombianos están en diccionario
    assert 'cedula' in user_dict
    assert 'telefono' in user_dict
    assert 'ciudad' in user_dict
    assert user_dict['cedula'] == '87654321'
    assert user_dict['telefono'] == '+57 301 987 6543'
    assert user_dict['ciudad'] == 'Medellín'


def test_cedula_uniqueness_constraint():
    """Test que cedula tiene constraint de unicidad"""
    # Verificar que la columna cedula tiene unique=True
    cedula_column = User.__table__.columns['cedula']
    assert cedula_column.unique is True
    assert cedula_column.nullable is True  # Opcional
    assert cedula_column.index is True     # Indexada
