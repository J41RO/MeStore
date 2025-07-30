# ~/tests/models/test_storage_contracts.py
# ---------------------------------------------------------------------------------------------
# MeStore - Tests para Funcionalidad de Contratos en Storage
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------

import pytest
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from app.models.storage import Storage, StorageType


class TestStorageContracts:
    """Tests para funcionalidad de contratos en Storage"""

    def test_create_storage_with_contrato(self, test_db_session):
        """Test creación con campos de contrato"""
        fecha_inicio = datetime.utcnow()
        fecha_fin = fecha_inicio + timedelta(days=365)
        
        storage = Storage(
            tipo=StorageType.PEQUENO,
            capacidad_max=100,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            renovacion_automatica=True
        )
        
        test_db_session.add(storage)
        test_db_session.commit()
        
        assert storage.fecha_inicio == fecha_inicio
        assert storage.fecha_fin == fecha_fin
        assert storage.renovacion_automatica is True

    def test_esta_vigente(self, test_db_session):
        """Test método esta_vigente()"""
        now = datetime.utcnow()
        
        # Contrato vigente
        storage_vigente = Storage(
            tipo=StorageType.PEQUENO,
            capacidad_max=100,
            fecha_inicio=now - timedelta(days=30),
            fecha_fin=now + timedelta(days=30)
        )
        assert storage_vigente.esta_vigente() is True
        
        # Contrato vencido
        storage_vencido = Storage(
            tipo=StorageType.PEQUENO,
            capacidad_max=100,
            fecha_inicio=now - timedelta(days=60),
            fecha_fin=now - timedelta(days=30)
        )
        assert storage_vencido.esta_vigente() is False
        
        # Sin fecha de inicio
        storage_sin_fecha = Storage(
            tipo=StorageType.PEQUENO,
            capacidad_max=100
        )
        assert storage_sin_fecha.esta_vigente() is False

    def test_dias_restantes(self, test_db_session):
        """Test método dias_restantes()"""
        now = datetime.utcnow()
        
        # Contrato con días restantes
        storage_con_dias = Storage(
            tipo=StorageType.PEQUENO,
            capacidad_max=100,
            fecha_inicio=now - timedelta(days=30),
            fecha_fin=now + timedelta(days=15)
        )
        dias = storage_con_dias.dias_restantes()
        assert dias is not None
        assert 14 <= dias <= 15  # Permitir variación por milisegundos

    def test_contrato_serialization(self, test_db_session):
        """Test serialización campos contrato en to_dict()"""
        now = datetime.utcnow()
        fecha_inicio = now - timedelta(days=30)
        fecha_fin = now + timedelta(days=60)
        
        storage = Storage(
            tipo=StorageType.PEQUENO,
            capacidad_max=100,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            renovacion_automatica=True
        )
        
        storage_dict = storage.to_dict()
        
        assert 'fecha_inicio' in storage_dict
        assert 'fecha_fin' in storage_dict
        assert 'renovacion_automatica' in storage_dict
        
        assert storage_dict['fecha_inicio'] == fecha_inicio.isoformat()
        assert storage_dict['fecha_fin'] == fecha_fin.isoformat()
        assert storage_dict['renovacion_automatica'] is True