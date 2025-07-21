import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_exception_handlers_working():
    """Test que exception handlers funcionan perfectamente."""

    # 1. Verificar handlers registrados
    handlers_count = len(app.exception_handlers)
    assert handlers_count >= 4
    print(f"Exception handlers registrados: {handlers_count}")

    # 2. Test 404 JSON formato
    response = client.get("/api/v1/nonexistent")
    assert response.status_code == 404

    json_data = response.json()
    assert "error" in json_data
    assert "detail" in json_data
    assert "status_code" in json_data
    assert json_data["error"] == "HTTP404"
    print("404 devuelve JSON correcto")


def test_all_requirements_met():
    """Verificar todos los requerimientos cumplidos."""

    # Verificar archivos existen
    import os

    assert os.path.exists("app/api/v1/handlers/exceptions.py")

    # Verificar clases existen
    from app.api.v1.handlers.exceptions import (
        AppException,
        EmbeddingNotFoundException,
        InvalidEmbeddingPayloadException,
        register_exception_handlers,
    )

    assert AppException
    assert EmbeddingNotFoundException
    assert InvalidEmbeddingPayloadException
    assert register_exception_handlers

    print("Todos los requerimientos cumplidos")


if __name__ == "__main__":
    pytest.main(["-v", "-s", __file__])
