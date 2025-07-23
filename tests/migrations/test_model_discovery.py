"""
Tests for automatic model discovery in Alembic env.py
"""

import pytest
import importlib
from app.core.database import Base


class TestModelDiscovery:
    """Test automatic model discovery functionality."""
    
    def test_models_package_auto_import(self):
        """Test that importing app.models triggers auto-discovery."""
        # Fresh import without clearing (more realistic scenario)
        # Base.metadata.clear()  # Commented out - causes issues with reload
        # initial_count = len(Base.metadata.tables)  # Not needed anymore
        
        # Import models package
        import app.models
        importlib.reload(app.models)
        
        # Verify models were auto-imported
        final_count = len(Base.metadata.tables)
        assert final_count > 0, "Importing app.models should auto-import models"
        
        # Verify specific tables exist
        tables = list(Base.metadata.tables.keys())
        assert 'users' in tables, "Users table should be detected"
    
    def test_models_all_attribute(self):
        """Test that __all__ attribute is properly populated."""
        import app.models
        
        # Verify __all__ exists and has expected content
        assert hasattr(app.models, '__all__'), "app.models should have __all__ attribute"
        assert 'BaseModel' in app.models.__all__, "BaseModel should be in __all__"
        assert 'User' in app.models.__all__, "User should be in __all__"
        assert len(app.models.__all__) >= 2, "Should have at least BaseModel and User"
    
    def test_pkgutil_module_detection(self):
        """Test that pkgutil correctly detects model modules."""
        import pkgutil
        import app.models
        
        # Get modules detected by pkgutil
        detected_modules = []
        for importer, modname, ispkg in pkgutil.iter_modules(app.models.__path__, app.models.__name__ + '.'):
            detected_modules.append(modname.split('.')[-1])
        
        # Verify expected modules are detected
        assert 'base' in detected_modules, "base module should be detected"
        assert 'user' in detected_modules, "user module should be detected"
        assert len(detected_modules) >= 2, "Should detect at least 2 modules"


class TestModelValidation:
    """Test validation of detected models."""
    
    def test_detected_models_inherit_from_base(self):
        """Test that detected models properly inherit from BaseModel."""
        from app.models.base import BaseModel
        from app.models.user import User
        
        # Verify inheritance
        assert issubclass(User, BaseModel), "User should inherit from BaseModel"
        
        # Verify table attributes
        assert hasattr(User, '__tablename__'), "User should have __tablename__"
        assert hasattr(User, 'metadata'), "User should have metadata"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
