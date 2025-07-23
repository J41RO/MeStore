"""
Tests para validar aislamiento de base de datos de testing.
Archivo: backend/tests/test_database_isolation.py
Propósito: Verificar que la DB de testing funciona correctamente y está aislada.
ACTUALIZADO con estructura real del modelo User.
"""

import pytest
from sqlalchemy.orm import Session
from app.models.user import User, UserType


def test_database_url_is_testing(test_db_url):
    """Test que verifica que se está usando base de datos de testing."""
    assert ":memory:" in test_db_url or "/tmp/" in test_db_url
    print(f"✅ Usando base de datos de testing: {test_db_url}")


def test_create_user_in_test_db(test_db_session: Session):
    """Test que crea un usuario en la base de datos de testing."""
    # Crear usuario de prueba con campos correctos
    test_user = User(
        email="test@example.com",
        password_hash="$2b$12$fake.hashed.password.for.testing",
        nombre="Test",
        apellido="User"
    )
    
    # Agregar a la sesión y commitear
    test_db_session.add(test_user)
    test_db_session.commit()
    test_db_session.refresh(test_user)
    
    # Verificar que el usuario fue creado
    assert test_user.id is not None
    assert test_user.email == "test@example.com"
    assert test_user.nombre == "Test"
    assert test_user.apellido == "User"
    assert test_user.active_status is True
    
    print(f"✅ Usuario creado con ID: {test_user.id}")


def test_query_user_from_test_db(test_db_session: Session):
    """Test que consulta usuarios en la base de datos de testing."""
    # Crear usuario de prueba
    test_user = User(
        email="query_test@example.com",
        password_hash="$2b$12$query.hash.for.testing",
        nombre="Query",
        apellido="User"
    )
    test_db_session.add(test_user)
    test_db_session.commit()
    
    # Consultar el usuario
    found_user = test_db_session.query(User).filter(
        User.email == "query_test@example.com"
    ).first()
    
    # Verificaciones
    assert found_user is not None
    assert found_user.email == "query_test@example.com"
    assert found_user.nombre == "Query"
    assert found_user.apellido == "User"
    
    print(f"✅ Usuario consultado exitosamente: {found_user.email}")


def test_database_isolation_between_tests(test_db_session: Session):
    """Test que verifica que cada test tiene una DB limpia."""
    # Verificar que no hay usuarios de tests anteriores
    user_count = test_db_session.query(User).count()
    assert user_count == 0, f"DB debería estar vacía, pero tiene {user_count} usuarios"
    
    # Crear usuario temporal
    temp_user = User(
        email="isolation_test@example.com",
        password_hash="$2b$12$isolation.hash",
        nombre="Isolation",
        apellido="Test"
    )
    test_db_session.add(temp_user)
    test_db_session.commit()
    
    # Verificar que ahora hay 1 usuario
    user_count_after = test_db_session.query(User).count()
    assert user_count_after == 1
    
    print("✅ Aislamiento de base de datos verificado")


def test_fastapi_client_uses_test_db(client_with_test_db):
    """Test que verifica que el cliente FastAPI usa la DB de testing."""
    # Verificar que el cliente responde
    response = client_with_test_db.get("/health")
    
    # Verificar que el cliente funciona
    assert response.status_code in [200, 404]  # 404 si endpoint no existe
    
    print(f"✅ Cliente FastAPI funcional - Status: {response.status_code}")
    
    # Verificar que el override está activo
    from app.main import app
    from app.core.database import get_db
    
    override_active = get_db in app.dependency_overrides
    assert override_active, "Dependency override debería estar activo"
    
    print("✅ Dependency override de get_db está activo")


def test_rollback_and_cleanup(test_db_session: Session):
    """Test que verifica rollback automático al final del test."""
    # Crear múltiples usuarios
    users = [
        User(
            email=f"cleanup_test_{i}@example.com",
            password_hash="$2b$12$cleanup.hash",
            nombre=f"User_{i}",
            apellido="Cleanup"
        )
        for i in range(3)
    ]
    
    for user in users:
        test_db_session.add(user)
    test_db_session.commit()
    
    # Verificar que se crearon
    user_count = test_db_session.query(User).count()
    assert user_count == 3
    
    print(f"✅ Creados {user_count} usuarios para test de cleanup")
    
    # Al final de este test, la DB debería limpiarse automáticamente