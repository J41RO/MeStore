# ~/tests/unit/test_password_utils.py
# ---------------------------------------------------------------------------------------------
# MeStore - Tests Unitarios para Password Utilities
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: test_password_utils.py
# Ruta: ~/tests/unit/test_password_utils.py
# Autor: Jairo
# Fecha de Creación: 2025-07-21
# Última Actualización: 2025-07-21
# Versión: 1.0.0
# Propósito: Tests unitarios para las funciones de hash y verificación de passwords
#
# Modificaciones:
# 2025-07-21 - Creación inicial de tests para tarea 1.1.2.2
#
# ---------------------------------------------------------------------------------------------

"""
Tests unitarios para app.utils.password.

Este módulo contiene tests para:
- hash_password(): Verificar que genera hash seguro diferente al original
- verify_password(): Verificar que funciona con password válida
- verify_password(): Verificar que retorna False con password incorrecta
"""

import pytest
from app.utils.password import hash_password, verify_password, pwd_context


def test_hash_password_no_retorna_original():
    """
    Test que hash_password() no retorna el string original.

    Verifica que el hash generado es diferente a la contraseña original
    y que tiene la longitud típica de un hash bcrypt.
    """
    password_original = "mi_password_segura_123"

    # Generar hash
    password_hash = hash_password(password_original)

    # Verificaciones
    assert password_hash != password_original, "El hash no debe ser igual a la password original"
    assert len(password_hash) >= 50, "El hash bcrypt debe tener al menos 50 caracteres"
    assert password_hash.startswith('$2b$')


def test_verify_password_con_password_valida():
    """
    Test que verify_password() funciona con password válida.

    Verifica que una password correcta es validada exitosamente
    contra su hash correspondiente.
    """
    password_original = "password_correcta_456"

    # Generar hash de la password
    password_hash = hash_password(password_original)

    # Verificar que la password original coincide con el hash
    resultado = verify_password(password_original, password_hash)

    assert resultado is True, "verify_password debe retornar True para password correcta"


def test_verify_password_con_password_incorrecta():
    """
    Test que verify_password() retorna False con password incorrecta.

    Verifica que una password incorrecta es rechazada correctamente
    cuando se verifica contra un hash que no le corresponde.
    """
    password_original = "password_correcta_789"
    password_incorrecta = "password_incorrecta_000"

    # Generar hash de la password original
    password_hash = hash_password(password_original)

    # Verificar que la password incorrecta NO coincide con el hash
    resultado = verify_password(password_incorrecta, password_hash)

    assert resultado is False, "verify_password debe retornar False para password incorrecta"


def test_hash_password_genera_hashes_unicos():
    """
    Test adicional: verify que hash_password genera hashes únicos.

    Verifica que dos llamadas con la misma password generan hashes diferentes
    debido al salt único de bcrypt.
    """
    password = "misma_password"

    hash1 = hash_password(password)
    hash2 = hash_password(password)

    assert hash1 != hash2, "Cada hash debe ser único debido al salt de bcrypt"

    # Pero ambos deben validar la password original
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True


def test_pwd_context_configuracion():
    """
    Test adicional: verificar que pwd_context está configurado correctamente.

    Verifica que el contexto de bcrypt está inicializado y funcional.
    """
    # Verificar que pwd_context existe y es del tipo correcto
    assert pwd_context is not None, "pwd_context debe estar inicializado"

    # Verificar que puede hacer hash
    test_password = "test_context_123"
    hash_directo = pwd_context.hash(test_password)

    assert len(hash_directo) >= 50, "Hash directo debe tener longitud bcrypt"
    assert pwd_context.verify(test_password, hash_directo) is True, "Context debe verificar correctamente"