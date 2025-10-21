#!/usr/bin/env python3
"""
Tests específicos para validación de celulares colombianos en VendedorCreate.

Valida que:
1. VendedorCreate SOLO acepta celulares (códigos 3XX)
2. VendedorCreate rechaza teléfonos fijos
3. Todos los 40 códigos móviles son aceptados
4. Compatibilidad con UserCreate se preserva
"""

import pytest
from pydantic import ValidationError
from app.schemas.vendedor import VendedorCreate
from app.schemas.user import UserCreate
from app.utils.validators import get_mobile_operators_info


class TestVendedorCelularValidation:
    """Tests para validación específica de celulares en vendedores"""

    @pytest.fixture
    def base_vendedor_data(self):
        """Datos base para crear vendedor"""
        return {
            "email": "vendedor@test.com",
            "password": "Password123",
            "nombre": "Juan",
            "apellido": "Pérez",
            "cedula": "12345678"
        }

    def test_vendedor_acepta_celular_valido(self, base_vendedor_data):
        """VendedorCreate debe aceptar celulares válidos"""
        vendedor = VendedorCreate(
            **base_vendedor_data,
            telefono="3001234567"
        )
        assert vendedor.telefono == "+57 3001234567"

    def test_vendedor_rechaza_telefono_fijo(self, base_vendedor_data):
        """VendedorCreate debe rechazar teléfonos fijos"""
        with pytest.raises(ValidationError) as exc_info:
            VendedorCreate(
                **base_vendedor_data,
                telefono="6012345678"  # Fijo Bogotá
            )
        
        error_message = str(exc_info.value)
        assert "Solo se permiten números celulares" in error_message
        assert "601" in error_message

    def test_user_create_acepta_fijo(self):
        """UserCreate debe seguir aceptando teléfonos fijos"""
        user = UserCreate(
            email="user@test.com",
            password="Password123",
            nombre="Carlos",
            apellido="López",
            telefono="6012345678"
        )
        assert user.telefono == "+57 6012345678"

    def test_count_codigos_moviles(self):
        """Verificar que tenemos 40 códigos móviles"""
        operators_info = get_mobile_operators_info()
        total_codes = sum(len(codes) for codes in operators_info.values())
        assert total_codes == 40

    def test_diferentes_formatos_celular(self, base_vendedor_data):
        """Diferentes formatos de celular deben funcionar"""
        formatos = ["3001234567", "+57 300 123 4567", "300 123 4567"]
        
        for formato in formatos:
            vendedor = VendedorCreate(
                **base_vendedor_data,
                telefono=formato
            )
            assert vendedor.telefono == "+57 3001234567"