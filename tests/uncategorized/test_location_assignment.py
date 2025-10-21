import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy.orm import Session
from datetime import datetime

from app.services.location_assignment_service import (
    LocationAssignmentService, AssignmentStrategy, LocationCriteria, LocationScore
)
from app.services.product_verification_workflow import ProductVerificationWorkflow
from app.models.incoming_product_queue import IncomingProductQueue
from app.models.inventory import Inventory
from app.models.product import Product


class TestLocationAssignmentService:
    """Tests para el servicio de asignación de ubicaciones"""
    
    def setup_method(self):
        self.mock_db = Mock(spec=Session)
        self.service = LocationAssignmentService(self.mock_db)
    
    def test_initialization(self):
        """Test que el servicio se inicializa correctamente"""
        assert self.service.db == self.mock_db
        assert len(self.service.default_criteria) == 5
        
        # Verificar que tiene todas las estrategias por defecto
        strategies = [c.strategy for c in self.service.default_criteria]
        assert AssignmentStrategy.SIZE_OPTIMIZATION in strategies
        assert AssignmentStrategy.CLOSEST_TO_ENTRANCE in strategies
        assert AssignmentStrategy.PRODUCT_CATEGORY in strategies
        assert AssignmentStrategy.WEIGHT_DISTRIBUTION in strategies
        assert AssignmentStrategy.FIFO_ROTATION in strategies
    
    @pytest.mark.asyncio
    async def test_get_available_locations(self):
        """Test obtener ubicaciones disponibles"""
        # Mock inventario disponible
        mock_inventory_1 = Mock()
        mock_inventory_1.zona = 'A'
        mock_inventory_1.estante = '1'
        mock_inventory_1.posicion = '01'
        mock_inventory_1.deleted_at = None
        mock_inventory_1.id = 1
        mock_inventory_1.storage = None
        mock_inventory_1.cantidad_disponible.return_value = 5
        
        mock_inventory_2 = Mock()
        mock_inventory_2.zona = 'B'
        mock_inventory_2.estante = '2'
        mock_inventory_2.posicion = '01'
        mock_inventory_2.deleted_at = None
        mock_inventory_2.id = 2
        mock_inventory_2.storage = None
        mock_inventory_2.cantidad_disponible.return_value = 3
        
        mock_inventory = [mock_inventory_1, mock_inventory_2]
        
        self.mock_db.query.return_value.filter.return_value.all.return_value = mock_inventory
        
        locations = await self.service._get_available_locations()
        
        assert len(locations) == 2
        assert locations[0]['zona'] == 'A'
        assert locations[0]['estante'] == '1'
        assert locations[0]['available_capacity'] == 5
        assert locations[1]['zona'] == 'B'
        assert locations[1]['estante'] == '2'
        assert locations[1]['available_capacity'] == 3
    
    @pytest.mark.asyncio
    async def test_score_size_optimization(self):
        """Test algoritmo de optimización de tamaño"""
        location = {"available_capacity": 10}
        
        # Producto con utilización en el límite superior del óptimo (8/10 = 0.8)
        mock_product = Mock()
        mock_product.dimensiones = {"largo": 2, "ancho": 2, "alto": 2}  # volumen = 8
        
        score = await self.service._score_size_optimization(location, mock_product)
        assert score == 10.0  # Utilización óptima (0.8 está en el rango 0.6-0.8)
        
        # Producto que utiliza bien el espacio (7/10 = 0.7 está en rango óptimo 0.6-0.8)
        mock_product.dimensiones = {"largo": 2, "ancho": 2, "alto": 1.75}  # volumen = 7
        score = await self.service._score_size_optimization(location, mock_product)
        assert score == 10.0  # Utilización óptima
    
    @pytest.mark.asyncio
    async def test_score_entrance_proximity(self):
        """Test algoritmo de proximidad a entrada"""
        # Zona A - más cerca de entrada
        location_a = {"zona": "A", "estante": "1"}
        score = await self.service._score_entrance_proximity(location_a)
        assert score >= 10.0  # Zona A + estante bajo
        
        # Zona E - más lejos de entrada
        location_e = {"zona": "E", "estante": "5"}
        score = await self.service._score_entrance_proximity(location_e)
        assert score <= 4.0  # Zona E + estante alto
    
    @pytest.mark.asyncio
    async def test_score_category_grouping(self):
        """Test algoritmo de agrupación por categoría"""
        location = {"zona": "A"}
        mock_product = Mock()
        mock_product.categoria = "Electronics"
        
        # Mock productos similares en la zona
        mock_query = Mock()
        mock_query.join.return_value.filter.return_value.count.return_value = 3
        self.mock_db.query.return_value = mock_query
        
        score = await self.service._score_category_grouping(location, mock_product)
        assert score == 10.0  # Excelente agrupación
        
        # Sin productos similares
        mock_query.join.return_value.filter.return_value.count.return_value = 0
        score = await self.service._score_category_grouping(location, mock_product)
        assert score == 4.0  # Nueva área
    
    @pytest.mark.asyncio
    async def test_score_weight_distribution(self):
        """Test algoritmo de distribución de peso"""
        location = {"estante": "1"}  # Estante bajo
        
        # Producto pesado en estante bajo - perfecto
        mock_product = Mock()
        mock_product.peso = 15  # Pesado
        
        score = await self.service._score_weight_distribution(location, mock_product)
        assert score == 10.0
        
        # Producto pesado en estante alto - evitar
        location_high = {"estante": "5"}
        score = await self.service._score_weight_distribution(location_high, mock_product)
        assert score == 2.0
    
    @pytest.mark.asyncio
    async def test_assign_optimal_location_success(self):
        """Test asignación exitosa de ubicación óptima"""
        mock_product = Mock()
        mock_product.dimensiones = {"largo": 2, "ancho": 2, "alto": 2}
        mock_product.categoria = "Electronics"
        mock_product.peso = 5
        
        mock_queue_item = Mock()
        
        # Mock ubicaciones disponibles
        with patch.object(self.service, '_get_available_locations') as mock_get_locations:
            mock_get_locations.return_value = [
                {"zona": "A", "estante": "1", "posicion": "01", "available_capacity": 10, "inventory_id": 1}
            ]
            
            with patch.object(self.service, '_reserve_location') as mock_reserve:
                mock_reserve.return_value = True
                
                # Mock todas las consultas de base de datos que se usan en scoring
                mock_query = Mock()
                mock_query.join.return_value.filter.return_value.count.return_value = 2
                mock_query.filter.return_value.order_by.return_value.first.return_value = None
                self.mock_db.query.return_value = mock_query
                
                # Mock método _get_adjacent_zones
                with patch.object(self.service, '_get_adjacent_zones') as mock_adj:
                    mock_adj.return_value = ["B", "C"]
                    
                    result = await self.service.assign_optimal_location(mock_product, mock_queue_item)
                    
                    assert result is not None
                    assert result["zona"] == "A"
                    assert result["estante"] == "1"
                    assert result["posicion"] == "01"
                    assert "score" in result
                    assert "reasons" in result
    
    @pytest.mark.asyncio
    async def test_assign_optimal_location_no_locations(self):
        """Test cuando no hay ubicaciones disponibles"""
        mock_product = Mock()
        mock_queue_item = Mock()
        
        with patch.object(self.service, '_get_available_locations') as mock_get_locations:
            mock_get_locations.return_value = []
            
            result = await self.service.assign_optimal_location(mock_product, mock_queue_item)
            assert result is None
    
    @pytest.mark.asyncio
    async def test_reserve_location_success(self):
        """Test reserva exitosa de ubicación"""
        mock_location_score = LocationScore(
            zona="A", estante="1", posicion="01", score=10.0,
            reasons=["Test"], capacity_available=5
        )
        
        mock_product = Mock()
        mock_inventory = Mock()
        mock_inventory.cantidad_disponible.return_value = 5
        mock_inventory.cantidad_reservada = 0
        
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_inventory
        
        result = await self.service._reserve_location(mock_location_score, mock_product)
        
        assert result is True
        assert mock_inventory.cantidad_reservada == 1  # Incrementado en 1
        self.mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_assignment_analytics(self):
        """Test obtener analytics de asignación"""
        mock_inventory = [
            Mock(zona='A', deleted_at=None),
            Mock(zona='B', deleted_at=None)
        ]
        
        # Mock cantidad_disponible como método
        mock_inventory[0].cantidad_disponible.return_value = 5
        mock_inventory[1].cantidad_disponible.return_value = 3
        
        # Mock capacidad máxima  
        for inv in mock_inventory:
            inv.cantidad = 10
        
        self.mock_db.query.return_value.filter.return_value.all.return_value = mock_inventory
        
        analytics = await self.service.get_assignment_analytics()
        
        assert "zones_statistics" in analytics
        assert "total_locations" in analytics
        assert "total_capacity" in analytics
        assert "assignment_strategies" in analytics
        assert analytics["total_locations"] == 2


class TestProductVerificationWorkflowLocationIntegration:
    """Tests para la integración de asignación de ubicación en el workflow"""
    
    def setup_method(self):
        self.mock_db = Mock(spec=Session)
        self.mock_queue_item = Mock()
        self.mock_queue_item.id = 1
        self.mock_queue_item.tracking_number = "TEST001"
        self.mock_queue_item.verification_status = "QUALITY_CHECK"
        self.mock_queue_item.metadata = {}
        self.mock_queue_item.verification_notes = "Initial notes"
        
        self.workflow = ProductVerificationWorkflow(self.mock_db, self.mock_queue_item)
    
    @pytest.mark.asyncio
    async def test_auto_assign_location_success(self):
        """Test asignación automática exitosa"""
        mock_product = Mock()
        self.mock_queue_item.product = mock_product
        
        mock_assignment_result = {
            "zona": "A", "estante": "1", "posicion": "01",
            "score": 8.5, "reasons": ["Good fit"]
        }
        
        with patch.object(self.workflow.location_service, 'assign_optimal_location') as mock_assign:
            # Mock async method
            async def mock_assign_location(*args, **kwargs):
                return mock_assignment_result
            mock_assign.side_effect = mock_assign_location
            
            result = await self.workflow.auto_assign_location("inspector_123")
            
            assert result["success"] is True
            assert result["location"] == mock_assignment_result
            assert self.mock_queue_item.verification_status == "APPROVED"
            assert "assigned_location" in self.mock_queue_item.metadata
            self.mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_auto_assign_location_no_space(self):
        """Test cuando no hay espacio disponible"""
        mock_product = Mock()
        self.mock_queue_item.product = mock_product
        
        with patch.object(self.workflow.location_service, 'assign_optimal_location') as mock_assign:
            # Mock async method returning None
            async def mock_assign_location(*args, **kwargs):
                return None
            mock_assign.side_effect = mock_assign_location
            
            result = await self.workflow.auto_assign_location("inspector_123")
            
            assert result["success"] is False
            assert "No se encontraron ubicaciones disponibles" in result["message"]
    
    @pytest.mark.asyncio
    async def test_suggest_manual_locations(self):
        """Test sugerencias para asignación manual"""
        mock_suggestions = [
            {"zona": "A", "estante": "1", "posicion": "01", "capacity": 5, "recommendation": "Good zone"},
            {"zona": "B", "estante": "2", "posicion": "01", "capacity": 3, "recommendation": "Alternative"}
        ]
        
        with patch.object(self.workflow.location_service, '_get_available_locations') as mock_get:
            # Mock async method
            async def mock_get_locations():
                return [
                    {"zona": "A", "estante": "1", "posicion": "01", "available_capacity": 5},
                    {"zona": "B", "estante": "2", "posicion": "01", "available_capacity": 3}
                ]
            mock_get.side_effect = mock_get_locations
            
            suggestions = await self.workflow.suggest_manual_locations(2)
            
            assert len(suggestions) == 2
            assert suggestions[0]["zona"] == "A"
            assert suggestions[1]["zona"] == "B"
    
    def test_get_location_recommendation(self):
        """Test generación de recomendaciones de ubicación"""
        # Zona A - alta accesibilidad
        location_a = {"zona": "A", "available_capacity": 5}
        recommendation = self.workflow._get_location_recommendation(location_a)
        assert "fácil acceso" in recommendation
        
        # Zona B - intermedia
        location_b = {"zona": "B", "available_capacity": 8}
        recommendation = self.workflow._get_location_recommendation(location_b)
        assert "intermedia" in recommendation
        
        # Alta capacidad
        location_high_capacity = {"zona": "C", "available_capacity": 15}
        recommendation = self.workflow._get_location_recommendation(location_high_capacity)
        assert "Amplia capacidad" in recommendation


class TestLocationAssignmentEndpoints:
    """Tests para los endpoints de asignación de ubicación"""
    
    @pytest.fixture
    def client(self):
        from app.main import app
        from fastapi.testclient import TestClient
        return TestClient(app)
    
    def test_auto_assign_endpoint_exists(self, client):
        """Test que el endpoint de asignación automática existe"""
        # Intentar acceder sin autenticación para verificar que existe
        response = client.post("/api/v1/admin/incoming-products/1/location/auto-assign")
        # Esperamos 401/403 (no autorizado) no 404 (no encontrado)
        assert response.status_code in [401, 403, 422]  # 422 para validación de parámetros
    
    def test_location_suggestions_endpoint_exists(self, client):
        """Test que el endpoint de sugerencias existe"""
        response = client.get("/api/v1/admin/incoming-products/1/location/suggestions")
        assert response.status_code in [401, 403, 422]
    
    def test_manual_assign_endpoint_exists(self, client):
        """Test que el endpoint de asignación manual existe"""
        response = client.post("/api/v1/admin/incoming-products/1/location/manual-assign")
        assert response.status_code in [401, 403, 422]
    
    def test_warehouse_availability_endpoint_exists(self, client):
        """Test que el endpoint de disponibilidad existe"""
        response = client.get("/api/v1/admin/warehouse/availability")
        assert response.status_code in [401, 403, 422]
    
    def test_assignment_analytics_endpoint_exists(self, client):
        """Test que el endpoint de analytics existe"""
        response = client.get("/api/v1/admin/location-assignment/analytics")
        assert response.status_code in [401, 403, 422]


class TestAssignmentStrategyEnum:
    """Tests para el enum de estrategias de asignación"""
    
    def test_all_strategies_defined(self):
        """Test que todas las estrategias están definidas"""
        strategies = list(AssignmentStrategy)
        
        assert AssignmentStrategy.CLOSEST_TO_ENTRANCE in strategies
        assert AssignmentStrategy.PRODUCT_CATEGORY in strategies
        assert AssignmentStrategy.SIZE_OPTIMIZATION in strategies
        assert AssignmentStrategy.FIFO_ROTATION in strategies
        assert AssignmentStrategy.WEIGHT_DISTRIBUTION in strategies
        assert AssignmentStrategy.RANDOM_AVAILABLE in strategies
        
        # Verificar que hay exactamente 6 estrategias
        assert len(strategies) == 6
    
    def test_strategy_values(self):
        """Test que los valores de las estrategias son correctos"""
        assert AssignmentStrategy.CLOSEST_TO_ENTRANCE.value == "closest_to_entrance"
        assert AssignmentStrategy.PRODUCT_CATEGORY.value == "product_category"
        assert AssignmentStrategy.SIZE_OPTIMIZATION.value == "size_optimization"
        assert AssignmentStrategy.FIFO_ROTATION.value == "fifo_rotation"
        assert AssignmentStrategy.WEIGHT_DISTRIBUTION.value == "weight_distribution"
        assert AssignmentStrategy.RANDOM_AVAILABLE.value == "random_available"


class TestLocationCriteriaAndScore:
    """Tests para modelos de criterios y puntuación"""
    
    def test_location_criteria_creation(self):
        """Test creación de criterios de ubicación"""
        criteria = LocationCriteria(
            strategy=AssignmentStrategy.SIZE_OPTIMIZATION,
            weight=2.5,
            enabled=True
        )
        
        assert criteria.strategy == AssignmentStrategy.SIZE_OPTIMIZATION
        assert criteria.weight == 2.5
        assert criteria.enabled is True
    
    def test_location_score_creation(self):
        """Test creación de puntuación de ubicación"""
        score = LocationScore(
            zona="A",
            estante="1",
            posicion="01",
            score=8.5,
            reasons=["Good size fit", "Near entrance"],
            capacity_available=5.0,
            distance_to_entrance=10.5
        )
        
        assert score.zona == "A"
        assert score.estante == "1"
        assert score.posicion == "01"
        assert score.score == 8.5
        assert len(score.reasons) == 2
        assert score.capacity_available == 5.0
        assert score.distance_to_entrance == 10.5


# Configuración de pytest para tests async
@pytest.fixture(scope="session")
def event_loop():
    """Crear event loop para tests async"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    # Ejecutar tests
    pytest.main([__file__, "-v", "--tb=short", "--cov=app.services.location_assignment_service", "--cov-report=html"])