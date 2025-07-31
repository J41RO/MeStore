# Corrección para override_get_db en conftest.py
import re

# Leer conftest.py
with open('tests/conftest.py', 'r') as f:
    content = f.read()

# Reemplazar la fixture problemática
old_fixture = """@pytest.fixture(scope="function")
def override_get_db(test_db_session: Session) -> Generator[None, None, None]:
    \"\"\"
    Fixture para override de dependencia get_db de FastAPI.

    Scope: function - Override por test individual.
    Effect: Redirige get_db() a la sesión de testing.
    Cleanup: Restaura dependencia original.
    \"\"\"
    def get_test_db() -> Generator[Session, None, None]:
        \"\"\"Dependencia de testing que retorna la sesión de test.\"\"\"
        try:
            yield test_db_session
        finally:
            pass  # Session cleanup manejado por test_db_session fixture

    # Override de la dependencia get_db
    app.dependency_overrides[get_db] = get_test_db

    yield

    # Limpiar override después del test
    app.dependency_overrides.clear()"""

new_fixture = """@pytest.fixture(scope="function")
async def override_get_db_async():
    \"\"\"
    Fixture async para override de dependencia get_db de FastAPI.
    
    Usa async_session en lugar de test_db_session sync.
    \"\"\"
    from sqlalchemy.ext.asyncio import AsyncSession
    
    async def get_test_db_async():
        \"\"\"Dependencia async de testing que retorna AsyncSession.\"\"\"
        # Crear sesión async para el test
        async with AsyncTestingSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()

    # Override de la dependencia get_db con versión async
    app.dependency_overrides[get_db] = get_test_db_async

    yield

    # Limpiar override después del test
    app.dependency_overrides.clear()"""

# Aplicar corrección
content = content.replace(old_fixture, new_fixture)

# Escribir archivo corregido
with open('tests/conftest.py', 'w') as f:
    f.write(content)

print("✅ Fixture override_get_db corregida para AsyncSession")
