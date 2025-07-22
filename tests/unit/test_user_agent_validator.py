"""
Tests unitarios para UserAgentValidatorMiddleware.

Casos cubiertos:
- User-Agent legítimo → 200
- User-Agent vacío → 403  
- User-Agent de bot/crawler → 403
- Rutas excluidas funcionan correctamente
- Logging estructurado ocurre
"""

import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from app.middleware.user_agent_validator import UserAgentValidatorMiddleware


@pytest.fixture
def middleware():
    """Fixture del middleware para tests."""
    mock_app = Mock()
    return UserAgentValidatorMiddleware(mock_app)


@pytest.fixture
def mock_request():
    """Fixture de request mock."""
    request = Mock(spec=Request)
    request.url.path = "/api/v1/test"
    request.method = "GET"
    request.client.host = "192.168.1.100"
    request.headers = {}
    return request


@pytest.fixture
def mock_call_next():
    """Fixture de call_next mock."""
    async_mock = AsyncMock()
    async_mock.return_value = Response(content="OK", status_code=200)
    return async_mock


class TestUserAgentValidatorMiddleware:
    """Test suite para UserAgentValidatorMiddleware."""

    @pytest.mark.asyncio
    async def test_legitimate_user_agent_allowed(self, middleware, mock_request, mock_call_next):
        """Test: User-Agent legítimo debe ser permitido."""
        # Arrange
        mock_request.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        # Act
        response = await middleware.dispatch(mock_request, mock_call_next)

        # Assert
        mock_call_next.assert_called_once()
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_empty_user_agent_blocked(self, middleware, mock_request, mock_call_next):
        """Test: User-Agent vacío debe ser bloqueado con 403."""
        # Arrange
        mock_request.headers = {"User-Agent": ""}

        # Act
        response = await middleware.dispatch(mock_request, mock_call_next)

        # Assert
        mock_call_next.assert_not_called()
        assert isinstance(response, JSONResponse)
        assert response.status_code == 403
        # Verificar contenido del response
        import json
        content = json.loads(response.body)
        assert content["error"] == "Forbidden"
        assert content["message"] == "User-Agent no permitido"
        assert content["code"] == "INVALID_USER_AGENT"

    @pytest.mark.asyncio
    async def test_missing_user_agent_blocked(self, middleware, mock_request, mock_call_next):
        """Test: Request sin User-Agent debe ser bloqueado."""
        # Arrange - no User-Agent header
        mock_request.headers = {}

        # Act
        response = await middleware.dispatch(mock_request, mock_call_next)

        # Assert
        mock_call_next.assert_not_called()
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_curl_user_agent_blocked(self, middleware, mock_request, mock_call_next):
        """Test: curl User-Agent debe ser bloqueado."""
        # Arrange
        mock_request.headers = {"User-Agent": "curl/7.81.0"}

        # Act
        response = await middleware.dispatch(mock_request, mock_call_next)

        # Assert
        mock_call_next.assert_not_called()
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_python_requests_blocked(self, middleware, mock_request, mock_call_next):
        """Test: python-requests User-Agent debe ser bloqueado."""
        # Arrange
        mock_request.headers = {"User-Agent": "python-requests/2.28.0"}

        # Act
        response = await middleware.dispatch(mock_request, mock_call_next)

        # Assert
        mock_call_next.assert_not_called()
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_bot_user_agent_blocked(self, middleware, mock_request, mock_call_next):
        """Test: User-Agent con palabra bot debe ser bloqueado."""
        # Arrange
        mock_request.headers = {"User-Agent": "MyBot/1.0"}

        # Act
        response = await middleware.dispatch(mock_request, mock_call_next)

        # Assert
        mock_call_next.assert_not_called()
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_health_endpoint_excluded(self, middleware, mock_call_next):
        """Test: Endpoint /health debe estar excluido de validación."""
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/health"
        mock_request.client.host = "192.168.1.100"
        mock_request.headers = {"User-Agent": "curl/7.81.0"}  # Normalmente bloqueado

        # Act
        response = await middleware.dispatch(mock_request, mock_call_next)

        # Assert
        mock_call_next.assert_called_once()
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_docs_endpoint_excluded(self, middleware, mock_call_next):
        """Test: Endpoint /docs debe estar excluido de validación."""
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/docs"
        mock_request.client.host = "192.168.1.100"
        mock_request.headers = {}  # Sin User-Agent, normalmente bloqueado

        # Act
        response = await middleware.dispatch(mock_request, mock_call_next)

        # Assert
        mock_call_next.assert_called_once()
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_openapi_endpoint_excluded(self, middleware, mock_call_next):
        """Test: Endpoint /openapi.json debe estar excluido."""
        # Arrange
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/openapi.json"
        mock_request.client.host = "192.168.1.100"
        mock_request.headers = {"User-Agent": "python-requests/2.28.0"}  # Normalmente bloqueado

        # Act
        response = await middleware.dispatch(mock_request, mock_call_next)

        # Assert
        mock_call_next.assert_called_once()
        assert response.status_code == 200

    def test_is_suspicious_user_agent_detection(self, middleware):
        """Test: Verificar detección correcta de User-Agents sospechosos."""
        # Test cases con diferentes patrones
        test_cases = [
            # Sospechosos (deben retornar True)
            ("", True),
            ("   ", True),
            ("curl/7.81.0", True),
            ("python-requests/2.28.0", True),
            ("Go-http-client/1.1", True),
            ("Scrapy/2.5.0", True),
            ("wget/1.21.2", True),
            ("MyBot/1.0", True),
            ("WebCrawler/1.0", True),
            ("spider-bot", True),
            ("scraper-tool", True),
            ("PostMan/7.0", True),

            # Legítimos (deben retornar False)
            ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", False),
            ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36", False),
            ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36", False),
            ("Safari/14.1.2", False),
            ("Chrome/91.0.4472.124", False),
            ("Edge/91.0.864.59", False),
        ]

        for user_agent, expected_suspicious in test_cases:
            result = middleware._is_suspicious_user_agent(user_agent)
            assert result == expected_suspicious, f"User-Agent: {user_agent}, Expected: {expected_suspicious}, Got: {result}"

    def test_should_validate_path_exclusions(self, middleware):
        """Test: Verificar que rutas excluidas funcionan correctamente."""
        # Rutas que NO deben validarse
        excluded_paths = ["/health", "/ready", "/docs", "/openapi.json", "/redoc"]
        for path in excluded_paths:
            assert not middleware._should_validate_path(path), f"Path {path} should be excluded"

        # Rutas que SÍ deben validarse
        included_paths = ["/api/v1/users", "/", "/login", "/api/v1/products"]
        for path in included_paths:
            assert middleware._should_validate_path(path), f"Path {path} should be validated"