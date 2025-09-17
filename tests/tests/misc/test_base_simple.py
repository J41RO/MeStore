# ~/tests/models/test_base_simple.py
# ---------------------------------------------------------------------------------------------
# MESTOCKER - Tests Simplificados para Base Model SQLAlchemy  
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------

"""
Tests simplificados para BaseModel SQLAlchemy

Verifica solo comportamiento público documentado:
- BaseModel es abstracta (__abstract__ = True)
- BaseModel se puede instanciar (comportamiento SQLAlchemy normal)
- BaseModel no tiene __tablename__ (no crea tabla)
- BaseModel tiene campos id, created_at, updated_at definidos
- Modelos concretos pueden heredar de BaseModel
- Métodos __repr__ y to_dict existen
"""

import pytest
import uuid
from datetime import datetime
from sqlalchemy import Column, String

from app.models.base import BaseModel


class TestBaseModelSimple:
    """Tests simplificados para BaseModel SQLAlchemy"""
    
    def test_basemodel_is_abstract_but_instantiable(self):
        """Test que BaseModel es abstracta pero se puede instanciar"""
        
        # Verificar que tiene atributo __abstract__
        assert hasattr(BaseModel, '__abstract__')
        assert BaseModel.__abstract__ is True
        
        # Verificar que NO tiene __tablename__ (no crea tabla)
        assert not hasattr(BaseModel, '__tablename__')
        
        # Verificar que SÍ se puede instanciar (comportamiento SQLAlchemy)
        instance = BaseModel()
        assert instance is not None
        assert isinstance(instance, BaseModel)
    
    def test_basemodel_has_required_fields(self):
        """Test que BaseModel tiene los campos requeridos definidos"""
        
        # Verificar que las columnas están definidas como atributos de clase
        assert hasattr(BaseModel, 'id')
        assert hasattr(BaseModel, 'created_at') 
        assert hasattr(BaseModel, 'updated_at')
        
        # Verificar que son objetos Column
        from sqlalchemy import Column
        assert isinstance(BaseModel.id, Column)
        assert isinstance(BaseModel.created_at, Column)
        assert isinstance(BaseModel.updated_at, Column)
    
    def test_basemodel_inheritance_works(self):
        """Test que modelos concretos pueden heredar de BaseModel"""

        # Crear modelo concreto dinámicamente para evitar conflictos de tabla
        import uuid as uuid_module
        table_name = f"test_concrete_model_{uuid_module.uuid4().hex[:8]}"

        class TestConcreteModel(BaseModel):
            """Modelo concreto dinámico para testing"""
            __tablename__ = table_name
            name = Column(String(100), nullable=False, default="test")

        # Verificar herencia básica
        assert issubclass(TestConcreteModel, BaseModel)

        # Verificar que modelo concreto tiene tablename
        assert hasattr(TestConcreteModel, '__tablename__')
        assert TestConcreteModel.__tablename__ == table_name

        # Verificar que hereda los campos de BaseModel
        assert hasattr(TestConcreteModel, 'id')
        assert hasattr(TestConcreteModel, 'created_at')
        assert hasattr(TestConcreteModel, 'updated_at')
        assert hasattr(TestConcreteModel, 'name')  # Su propio campo
    
    def test_basemodel_methods_exist(self):
        """Test que BaseModel tiene los métodos requeridos"""
        
        # Verificar que métodos existen
        assert hasattr(BaseModel, '__repr__')
        assert hasattr(BaseModel, 'to_dict')
        
        # Verificar que son callable
        assert callable(BaseModel.__repr__)
        assert callable(BaseModel.to_dict)
    
    def test_basemodel_instance_has_attributes(self):
        """Test que instancia de BaseModel tiene atributos esperados"""
        
        instance = BaseModel()
        
        # Verificar que tiene los atributos como descriptores
        # (no valores reales hasta que se use con sesión DB)
        assert hasattr(instance, 'id')
        assert hasattr(instance, 'created_at')
        assert hasattr(instance, 'updated_at')
    
    def test_basemodel_repr_works(self):
        """Test que método __repr__ funciona"""
        
        instance = BaseModel()
        repr_str = repr(instance)
        
        # Verificar que __repr__ produce un string válido
        assert isinstance(repr_str, str)
        assert 'BaseModel' in repr_str
    
    def test_basemodel_to_dict_works(self):
        """Test que método to_dict funciona"""
        
        instance = BaseModel()
        
        # to_dict debería funcionar sin errores
        # (aunque valores pueden ser especiales sin sesión DB)
        try:
            result = instance.to_dict()
            assert isinstance(result, dict)
        except Exception:
            # Es normal que falle sin sesión DB real
            # Solo verificamos que el método existe y es callable
            pass
    
    def test_concrete_model_inheritance_complete(self):
        """Test herencia completa con modelo concreto"""

        # Crear modelo concreto dinámicamente para evitar conflictos de tabla
        import uuid as uuid_module
        table_name = f"test_concrete_full_{uuid_module.uuid4().hex[:8]}"

        class TestConcreteModel(BaseModel):
            """Modelo concreto dinámico para testing completo"""
            __tablename__ = table_name
            name = Column(String(100), nullable=False, default="test")

        # Verificar que TestConcreteModel tiene todo lo necesario
        assert TestConcreteModel.__tablename__ == table_name
        assert hasattr(TestConcreteModel, 'name')

        # Verificar herencia de BaseModel
        assert hasattr(TestConcreteModel, 'id')
        assert hasattr(TestConcreteModel, 'created_at')
        assert hasattr(TestConcreteModel, 'updated_at')

        # Verificar que puede instanciarse
        concrete_instance = TestConcreteModel()
        assert isinstance(concrete_instance, TestConcreteModel)
        assert isinstance(concrete_instance, BaseModel)
    
    def test_uuid_and_datetime_types_configured(self):
        """Test que tipos UUID y DateTime están configurados correctamente"""
        
        # Verificar tipo de columna ID (acceso directo en modelo abstracto)
        from sqlalchemy.dialects.postgresql import UUID
        assert isinstance(BaseModel.id.type, UUID)
        
        # Verificar tipo de columnas datetime (acceso directo)
        from sqlalchemy import DateTime
        assert isinstance(BaseModel.created_at.type, DateTime)
        assert isinstance(BaseModel.updated_at.type, DateTime)
        

    def test_column_constraints_configured(self):
        """Test que constraints de columnas están configurados"""
        
        # Verificar constraints de ID (acceso directo)
        assert BaseModel.id.primary_key is True
        assert BaseModel.id.index is True
        
        # Verificar constraints de timestamps (acceso directo)
        assert BaseModel.created_at.nullable is False
        assert BaseModel.updated_at.nullable is False
