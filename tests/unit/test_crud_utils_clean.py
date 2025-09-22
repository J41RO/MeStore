"""
Test CRUD Utils - Versión limpia que funciona
"""

import pytest
from sqlalchemy.orm import Session
from app.models.user import User, UserType


class TestCRUDClean:
    """Tests CRUD que funcionan correctamente"""
    
    def test_crud_imports(self):
        """Test que imports funcionan"""
        from app.utils.crud import CRUDOperations, CRUDBase
        from app.utils.database import DatabaseUtils
        
        assert CRUDOperations is not None
        assert CRUDBase is not None
        assert DatabaseUtils is not None
        
    def test_user_basic_crud(self, test_db_session: Session):
        """Test CRUD básico con User"""
        # Crear usuario directamente
        user = User(
            nombre="CRUD",
            apellido="Test",
            email="crud.test@example.com",
            password_hash="hash123",
            user_type=UserType.BUYER
        )
        
        # Guardar en DB
        test_db_session.add(user)
        test_db_session.commit()
        test_db_session.refresh(user)
        
        # Verificar
        assert user.id is not None
        assert user.nombre == "CRUD"
        assert user.deleted_at is None
        
    def test_soft_delete_field(self):
        """Test que campo deleted_at existe"""
        user = User(
            nombre="SoftDelete",
            apellido="Field",
            email="softdelete.field@example.com",
            password_hash="hash123",
            user_type=UserType.VENDOR
        )
        
        assert hasattr(user, 'deleted_at')
        assert user.deleted_at is None
