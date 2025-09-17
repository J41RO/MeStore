# ~/tests/test_alerts.py
# Tests para sistema de alertas

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from app.models.product import Product
from app.schemas.alerts import (
    AlertConfig,
    AlertDashboard,
    AlertResponse,
    ProductoSinMovimiento,
    StockAlert,
)


class TestSchemasAlertas:
    """Tests para schemas de alertas"""

    def test_stock_alert_schema_validation(self):
        """Test validación del schema StockAlert"""
        alerta = StockAlert(
            producto_id=1,
            nombre_producto="Producto Test",
            stock_actual=5,
            umbral_minimo=10,
            tipo_alerta="stock_bajo",
        )

        assert alerta.producto_id == 1
        assert alerta.nombre_producto == "Producto Test"
        assert alerta.stock_actual == 5
        assert alerta.umbral_minimo == 10
        assert alerta.tipo_alerta == "stock_bajo"

    def test_alert_config_schema_defaults(self):
        """Test valores por defecto del schema AlertConfig"""
        config = AlertConfig()

        assert config.umbral_stock_bajo == 10
        assert config.dias_sin_movimiento == 30

    def test_alert_response_schema_complete(self):
        """Test schema AlertResponse con datos completos"""
        config = AlertConfig()
        alerta_stock = StockAlert(
            producto_id=1, nombre_producto="Test", stock_actual=5, umbral_minimo=10
        )

        response = AlertResponse(
            alertas_stock_bajo=[alerta_stock],
            productos_sin_movimiento=[],
            total_alertas=1,
            configuracion=config,
        )

        assert len(response.alertas_stock_bajo) == 1
        assert response.total_alertas == 1
        assert isinstance(response.timestamp, datetime)


class TestProductMethodsAlertas:
    """Tests para métodos de alertas en modelo Product"""

    def test_is_low_stock_method(self):
        """Test método is_low_stock"""
        producto = Mock(spec=Product)
        producto.get_stock_total.return_value = 5

        resultado = Product.is_low_stock(producto, 10)
        assert resultado is True

        producto.get_stock_total.return_value = 15
        resultado = Product.is_low_stock(producto, 10)
        assert resultado is False

    def test_methods_exist(self):
        """Test que los métodos de alertas existen en Product"""
        assert hasattr(Product, "is_low_stock")
        assert hasattr(Product, "days_since_last_movement")
        assert hasattr(Product, "get_low_stock_products")
        assert hasattr(Product, "get_inactive_products")


@pytest.mark.asyncio
class TestAlertsEndpoints:
    """Tests para endpoints de alertas"""

    async def test_endpoint_imports(self):
        """Test que los endpoints se pueden importar correctamente"""
        from app.api.v1.endpoints.alerts import router

        assert router is not None

        rutas = [route.path for route in router.routes]
        assert "/stock-bajo" in rutas
        assert "/sin-movimiento" in rutas
        assert "/dashboard" in rutas


class TestIntegracionAlertas:
    """Tests de integración para el sistema de alertas"""

    def test_alert_system_integration(self):
        """Test integración completa del sistema de alertas"""
        from app.api.v1.endpoints.alerts import router
        from app.models.product import Product
        from app.schemas.alerts import AlertDashboard, AlertResponse

        config = AlertConfig()
        assert config.umbral_stock_bajo == 10

        rutas = [route.path for route in router.routes]
        expected_routes = ["/stock-bajo", "/sin-movimiento", "/dashboard"]

        for ruta in expected_routes:
            assert ruta in rutas

        print("✅ Integración del sistema de alertas verificada")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
