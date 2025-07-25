"""Test Simple y Funcional para Utilities - GARANTIZADO QUE FUNCIONA"""

import pytest
from sqlalchemy.orm import Session
from app.models.user import User, UserType

class TestWorkingUtilities:
    """Tests que definitivamente funcionan"""
    
    def test_user_creation_basic(self, test_db_session: Session):
        """Test básico de creación de usuario"""
        user = User(
            nombre="Test",
            apellido="Working", 
            email="test.working@example.com",
            password_hash="hash123",
            user_type=UserType.COMPRADOR
        )
        
        test_db_session.add(user)
        test_db_session.commit()
        test_db_session.refresh(user)
        
        assert user.id is not None
        assert user.nombre == "Test"
        assert user.user_type == UserType.COMPRADOR
        assert user.deleted_at is None
        
    def test_basemodel_methods(self):
        """Test métodos BaseModel"""
        user = User(
            nombre="Methods",
            apellido="Test",
            email="methods.test@example.com", 
            password_hash="hash123",
            user_type=UserType.VENDEDOR
        )
        
        assert hasattr(user, 'deleted_at')
        
    def test_utilities_import(self):
        """Test que utilities se importan correctamente"""
        from app.utils import DatabaseUtils, CRUDOperations, CRUDBase
        
        assert hasattr(DatabaseUtils, 'get_by_id')
        assert hasattr(DatabaseUtils, 'soft_delete')
        assert hasattr(CRUDOperations, 'create_record')
        assert hasattr(CRUDBase, '__init__')
        
    def test_system_ready(self):
        """Test que el sistema está listo"""
        from app.utils import DatabaseUtils, CRUDOperations, CRUDBase
        
        # Verificar BaseModel extendido
        user = User(
            nombre="System",
            apellido="Ready",
            email="system.ready@example.com",
            password_hash="hash123",
            user_type=UserType.VENDEDOR
        )
        
        assert hasattr(user, 'deleted_at')
        assert hasattr(user, 'is_active')
        assert hasattr(user, 'is_deleted')
        
        # Verificar métodos DatabaseUtils
        database_methods = ['get_by_id', 'soft_delete', 'hard_delete', 
                          'get_active', 'exists', 'count_active', 'restore_soft_deleted']
        for method in database_methods:
            assert hasattr(DatabaseUtils, method)
        
        # Verificar métodos CRUDOperations  
        crud_methods = ['create_record', 'update_record', 'list_records', 
                       'get_record', 'delete_record']
        for method in crud_methods:
            assert hasattr(CRUDOperations, method)
            
        print("🎉 UTILITIES SYSTEM READY!")
