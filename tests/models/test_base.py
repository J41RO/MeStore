# ~/tests/models/test_base.py
# ---------------------------------------------------------------------------------------------
# MESTOCKER - Tests para Base Model
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
"""
Tests completos para BaseModel

Cubre:
- Inicialización de la clase
- Métodos to_dict(), update_timestamp(), __repr__()
- Comportamiento de timestamps
- Herencia por otras clases
- Casos límite y edge cases
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
import time

from app.models.base import BaseModel


class TestBaseModel:
    """Suite completa de tests para BaseModel"""
    
    def test_initialization(self):
        """Test de inicialización básica"""
        # Capturar tiempo antes de crear instancia
        before_creation = datetime.utcnow()
        
        # Crear instancia
        model = BaseModel()
        
        # Capturar tiempo después de crear instancia
        after_creation = datetime.utcnow()
        
        # Verificar que timestamps están en rango esperado
        assert before_creation <= model.created_at <= after_creation
        assert before_creation <= model.updated_at <= after_creation
        
        # Verificar que ambos timestamps son iguales en inicialización
        assert model.created_at == model.updated_at
        
        # Verificar tipos
        assert isinstance(model.created_at, datetime)
        assert isinstance(model.updated_at, datetime)
    
    def test_to_dict_basic(self):
        """Test de conversión a diccionario básica"""
        model = BaseModel()
        
        result = model.to_dict()
        
        # Verificar estructura del diccionario
        assert isinstance(result, dict)
        assert "created_at" in result
        assert "updated_at" in result
        assert len(result) == 2
        
        # Verificar que los valores son strings ISO format
        assert isinstance(result["created_at"], str)
        assert isinstance(result["updated_at"], str)
        
        # Verificar que se pueden parsear de vuelta a datetime
        parsed_created = datetime.fromisoformat(result["created_at"])
        parsed_updated = datetime.fromisoformat(result["updated_at"])
        
        assert isinstance(parsed_created, datetime)
        assert isinstance(parsed_updated, datetime)
    
    def test_to_dict_timestamp_format(self):
        """Test del formato específico de timestamps en to_dict"""
        # Crear modelo con timestamp conocido
        model = BaseModel()
        
        # Usar timestamp específico para verificar formato
        known_time = datetime(2025, 7, 19, 12, 30, 45, 123456)
        model.created_at = known_time
        model.updated_at = known_time
        
        result = model.to_dict()
        
        # Verificar formato ISO exacto
        expected_iso = "2025-07-19T12:30:45.123456"
        assert result["created_at"] == expected_iso
        assert result["updated_at"] == expected_iso
    
    def test_update_timestamp(self):
        """Test de actualización de timestamp"""
        model = BaseModel()
        
        # Capturar created_at original
        original_created = model.created_at
        original_updated = model.updated_at
        
        # Esperar un poco para asegurar diferencia en timestamp
        time.sleep(0.01)
        
        # Actualizar timestamp
        model.update_timestamp()
        
        # Verificar que created_at no cambió
        assert model.created_at == original_created
        
        # Verificar que updated_at sí cambió
        assert model.updated_at > original_updated
        assert model.updated_at > model.created_at
    
    def test_update_timestamp_multiple_calls(self):
        """Test de múltiples llamadas a update_timestamp"""
        model = BaseModel()
        
        # Hacer múltiples actualizaciones
        first_update = model.updated_at
        
        time.sleep(0.01)
        model.update_timestamp()
        second_update = model.updated_at
        
        time.sleep(0.01)
        model.update_timestamp()
        third_update = model.updated_at
        
        # Verificar progresión temporal
        assert first_update < second_update < third_update
        
        # Verificar que created_at nunca cambió
        assert model.created_at == first_update
    
    def test_repr_method(self):
        """Test del método __repr__"""
        model = BaseModel()
        
        repr_str = repr(model)
        
        # Verificar formato básico
        assert repr_str.startswith("BaseModel(")
        assert repr_str.endswith(")")
        assert "created_at=" in repr_str
        
        # Verificar que contiene el timestamp
        assert str(model.created_at) in repr_str
        
        # Verificar que es una representación válida
        assert "BaseModel" in repr_str
    
    def test_repr_with_custom_timestamp(self):
        """Test de __repr__ con timestamp personalizado"""
        model = BaseModel()
        
        # Establecer timestamp específico
        custom_time = datetime(2025, 1, 1, 0, 0, 0)
        model.created_at = custom_time
        
        repr_str = repr(model)
        
        # Verificar que contiene el timestamp personalizado
        assert "2025-01-01 00:00:00" in repr_str
    
    def test_inheritance_behavior(self):
        """Test de comportamiento con herencia"""
        
        # Crear clase que hereda de BaseModel
        class TestChildModel(BaseModel):
            def __init__(self, name: str):
                super().__init__()
                self.name = name
            
            def to_dict(self):
                base_dict = super().to_dict()
                base_dict["name"] = self.name
                return base_dict
        
        # Crear instancia de clase hija
        child = TestChildModel("test_name")
        
        # Verificar que hereda comportamiento base
        assert hasattr(child, 'created_at')
        assert hasattr(child, 'updated_at')
        assert isinstance(child.created_at, datetime)
        
        # Verificar que to_dict funciona con herencia
        child_dict = child.to_dict()
        assert "created_at" in child_dict
        assert "updated_at" in child_dict
        assert "name" in child_dict
        assert child_dict["name"] == "test_name"
        
        # Verificar que update_timestamp funciona
        original_updated = child.updated_at
        time.sleep(0.01)
        child.update_timestamp()
        assert child.updated_at > original_updated
        
        # Verificar __repr__
        repr_str = repr(child)
        assert "TestChildModel(" in repr_str
    
    def test_multiple_instances_independence(self):
        """Test de independencia entre múltiples instancias"""
        model1 = BaseModel()
        time.sleep(0.01)
        model2 = BaseModel()
        
        # Verificar que tienen timestamps diferentes
        assert model1.created_at != model2.created_at
        assert model1.updated_at != model2.updated_at
        
        # Verificar que actualizar uno no afecta al otro
        original_model1_updated = model1.updated_at
        time.sleep(0.01)
        model2.update_timestamp()
        
        assert model1.updated_at == original_model1_updated
        assert model2.updated_at > model1.updated_at
    
    @patch('app.models.base.datetime')
    def test_mocked_datetime_utcnow(self, mock_datetime):
        """Test con datetime mockeado para control preciso"""
        # Configurar mock
        fixed_time = datetime(2025, 7, 19, 10, 30, 45)
        mock_datetime.utcnow.return_value = fixed_time
        
        # Crear modelo
        model = BaseModel()
        
        # Verificar que usa el tiempo mockeado
        assert model.created_at == fixed_time
        assert model.updated_at == fixed_time
        
        # Verificar llamadas al mock
        assert mock_datetime.utcnow.call_count == 1  # Una sola llamada optimizada
    
    @patch('app.models.base.datetime')
    def test_update_timestamp_with_mock(self, mock_datetime):
        """Test de update_timestamp con mock para control preciso"""
        # Configurar tiempos específicos
        initial_time = datetime(2025, 7, 19, 10, 0, 0)
        updated_time = datetime(2025, 7, 19, 11, 0, 0)
        
        # Primera llamada (inicialización)
        mock_datetime.utcnow.return_value = initial_time
        model = BaseModel()
        
        # Segunda llamada (update)
        mock_datetime.utcnow.return_value = updated_time
        model.update_timestamp()
        
        # Verificar timestamps
        assert model.created_at == initial_time
        assert model.updated_at == updated_time
        
        # Verificar número de llamadas
        assert mock_datetime.utcnow.call_count == 2  # 1 en init + 1 en update
    
    def test_edge_case_rapid_succession(self):
        """Test de caso límite: creación rápida en sucesión"""
        models = []
        
        # Crear múltiples modelos rápidamente
        for _ in range(5):
            models.append(BaseModel())
        
        # Verificar que todos tienen timestamps únicos o muy cercanos
        timestamps = [m.created_at for m in models]
        
        # Todos deberían ser instancias válidas de datetime
        for ts in timestamps:
            assert isinstance(ts, datetime)
        
        # Los timestamps deberían estar en orden no decreciente
        for i in range(1, len(timestamps)):
            assert timestamps[i] >= timestamps[i-1]
    
    def test_to_dict_immutability(self):
        """Test de que to_dict no afecta el modelo original"""
        model = BaseModel()
        original_created = model.created_at
        original_updated = model.updated_at
        
        # Obtener diccionario
        result = model.to_dict()
        
        # Modificar el diccionario
        result["created_at"] = "modified"
        result["updated_at"] = "modified"
        result["new_field"] = "added"
        
        # Verificar que el modelo original no cambió
        assert model.created_at == original_created
        assert model.updated_at == original_updated
        assert not hasattr(model, 'new_field')
    
    def test_model_attributes_exist(self):
        """Test de que todos los atributos esperados existen"""
        model = BaseModel()
        
        # Verificar que tiene todos los atributos esperados
        assert hasattr(model, 'created_at')
        assert hasattr(model, 'updated_at')
        
        # Verificar que tiene todos los métodos esperados
        assert hasattr(model, 'to_dict')
        assert hasattr(model, 'update_timestamp')
        assert hasattr(model, '__repr__')
        
        # Verificar que son callables
        assert callable(model.to_dict)
        assert callable(model.update_timestamp)
        assert callable(model.__repr__)
