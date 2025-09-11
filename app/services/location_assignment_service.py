from typing import List, Optional, Dict, Any, Tuple
from enum import Enum
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
import math
import random

from app.models.inventory import Inventory
from app.models.storage import Storage
from app.models.product import Product
from app.models.incoming_product_queue import IncomingProductQueue

class AssignmentStrategy(str, Enum):
    CLOSEST_TO_ENTRANCE = "closest_to_entrance"
    PRODUCT_CATEGORY = "product_category"
    SIZE_OPTIMIZATION = "size_optimization"
    FIFO_ROTATION = "fifo_rotation"
    WEIGHT_DISTRIBUTION = "weight_distribution"
    RANDOM_AVAILABLE = "random_available"

class LocationCriteria(BaseModel):
    strategy: AssignmentStrategy
    weight: float = 1.0
    enabled: bool = True

class LocationScore(BaseModel):
    zona: str
    estante: str
    posicion: str
    score: float
    reasons: List[str]
    capacity_available: float
    distance_to_entrance: Optional[float] = None

class LocationAssignmentService:
    def __init__(self, db: Session):
        self.db = db
        self.default_criteria = [
            LocationCriteria(strategy=AssignmentStrategy.SIZE_OPTIMIZATION, weight=3.0),
            LocationCriteria(strategy=AssignmentStrategy.CLOSEST_TO_ENTRANCE, weight=2.0),
            LocationCriteria(strategy=AssignmentStrategy.PRODUCT_CATEGORY, weight=2.5),
            LocationCriteria(strategy=AssignmentStrategy.WEIGHT_DISTRIBUTION, weight=1.5),
            LocationCriteria(strategy=AssignmentStrategy.FIFO_ROTATION, weight=1.0)
        ]
    
    async def assign_optimal_location(
        self,
        product: Product,
        queue_item: IncomingProductQueue,
        criteria: Optional[List[LocationCriteria]] = None
    ) -> Optional[Dict[str, str]]:
        """Asignar ubicación óptima para un producto"""
        
        if not criteria:
            criteria = self.default_criteria
        
        # Obtener ubicaciones disponibles
        available_locations = await self._get_available_locations()
        
        if not available_locations:
            return None
        
        # Calcular puntuación para cada ubicación
        scored_locations = []
        for location in available_locations:
            score = await self._calculate_location_score(
                location, product, queue_item, criteria
            )
            scored_locations.append(score)
        
        # Ordenar por puntuación y seleccionar la mejor
        best_location = max(scored_locations, key=lambda x: x.score)
        
        # Reservar la ubicación
        success = await self._reserve_location(best_location, product)
        
        if success:
            return {
                "zona": best_location.zona,
                "estante": best_location.estante,
                "posicion": best_location.posicion,
                "score": best_location.score,
                "reasons": best_location.reasons
            }
        
        return None
    
    async def _get_available_locations(self) -> List[Dict[str, Any]]:
        """Obtener todas las ubicaciones disponibles"""
        
        # Consultar inventario con espacios disponibles
        # cantidad_disponible() = cantidad - cantidad_reservada
        available_inventory = self.db.query(Inventory).filter(
            (Inventory.cantidad - Inventory.cantidad_reservada) > 0,
            Inventory.deleted_at.is_(None)  # is_active() check
        ).all()
        
        locations = []
        for inv in available_inventory:
            # Obtener información del storage asociado
            storage = inv.storage if hasattr(inv, 'storage') else None
            
            locations.append({
                "zona": inv.zona,
                "estante": inv.estante,
                "posicion": getattr(inv, 'posicion', '01'),
                "available_capacity": inv.cantidad_disponible(),
                "storage_info": storage,
                "current_products": getattr(inv, 'productos_actuales', 0),
                "inventory_id": inv.id
            })
        
        return locations
    
    async def _calculate_location_score(
        self,
        location: Dict[str, Any],
        product: Product,
        queue_item: IncomingProductQueue,
        criteria: List[LocationCriteria]
    ) -> LocationScore:
        """Calcular puntuación de una ubicación para un producto"""
        
        total_score = 0.0
        reasons = []
        
        for criterion in criteria:
            if not criterion.enabled:
                continue
                
            strategy_score = 0.0
            
            if criterion.strategy == AssignmentStrategy.SIZE_OPTIMIZATION:
                strategy_score = await self._score_size_optimization(location, product)
                reasons.append(f"Optimización tamaño: {strategy_score:.1f}")
                
            elif criterion.strategy == AssignmentStrategy.CLOSEST_TO_ENTRANCE:
                strategy_score = await self._score_entrance_proximity(location)
                reasons.append(f"Proximidad entrada: {strategy_score:.1f}")
                
            elif criterion.strategy == AssignmentStrategy.PRODUCT_CATEGORY:
                strategy_score = await self._score_category_grouping(location, product)
                reasons.append(f"Agrupación categoría: {strategy_score:.1f}")
                
            elif criterion.strategy == AssignmentStrategy.WEIGHT_DISTRIBUTION:
                strategy_score = await self._score_weight_distribution(location, product)
                reasons.append(f"Distribución peso: {strategy_score:.1f}")
                
            elif criterion.strategy == AssignmentStrategy.FIFO_ROTATION:
                strategy_score = await self._score_fifo_rotation(location)
                reasons.append(f"Rotación FIFO: {strategy_score:.1f}")
            
            total_score += strategy_score * criterion.weight
        
        return LocationScore(
            zona=location["zona"],
            estante=location["estante"],
            posicion=location["posicion"],
            score=total_score,
            reasons=reasons,
            capacity_available=location["available_capacity"]
        )
    
    async def _score_size_optimization(self, location: Dict[str, Any], product: Product) -> float:
        """Puntuación basada en optimización de espacio"""
        if not product.dimensiones:
            return 5.0  # Puntuación neutral
        
        # Calcular aprovechamiento del espacio
        available_capacity = location["available_capacity"]
        product_volume = self._calculate_product_volume(product)
        
        if product_volume <= 0:
            return 5.0
        
        # Preferir ubicaciones que se aprovechen bien pero no se llenen completamente
        utilization = min(product_volume / available_capacity, 1.0) if available_capacity > 0 else 0
        
        if 0.6 <= utilization <= 0.8:  # Utilización óptima
            return 10.0
        elif 0.4 <= utilization < 0.6:  # Buena utilización
            return 8.0
        elif 0.8 < utilization <= 1.0:  # Alta utilización
            return 6.0
        else:  # Baja utilización
            return 3.0
    
    async def _score_entrance_proximity(self, location: Dict[str, Any]) -> float:
        """Puntuación basada en proximidad a la entrada"""
        # Asumir que zonas A están más cerca de la entrada
        zona = location["zona"].upper()
        estante = location["estante"]
        
        zone_scores = {
            'A': 10.0, 'B': 8.0, 'C': 6.0, 'D': 4.0, 'E': 2.0
        }
        
        base_score = zone_scores.get(zona[0] if zona else 'E', 2.0)
        
        # Estantes más bajos son más accesibles
        try:
            estante_num = int(estante.split('-')[0]) if '-' in estante else int(estante)
            if estante_num <= 2:
                base_score += 2.0
            elif estante_num <= 4:
                base_score += 1.0
        except (ValueError, IndexError):
            pass
        
        return min(base_score, 10.0)
    
    async def _score_category_grouping(self, location: Dict[str, Any], product: Product) -> float:
        """Puntuación basada en agrupación por categorías"""
        if not product.categoria:
            return 5.0
        
        # Buscar productos similares en la misma zona
        similar_products = self.db.query(Inventory).join(Product).filter(
            Product.categoria == product.categoria,
            Inventory.zona == location["zona"],
            (Inventory.cantidad - Inventory.cantidad_reservada) > 0
        ).count()
        
        if similar_products > 0:
            return 10.0  # Excelente agrupación
        
        # Buscar en zonas adyacentes
        adjacent_zones = self._get_adjacent_zones(location["zona"])
        for adj_zone in adjacent_zones:
            similar_in_adjacent = self.db.query(Inventory).join(Product).filter(
                Product.categoria == product.categoria,
                Inventory.zona == adj_zone,
                (Inventory.cantidad - Inventory.cantidad_reservada) > 0
            ).count()
            
            if similar_in_adjacent > 0:
                return 7.0  # Buena agrupación
        
        return 4.0  # Nueva área para esta categoría
    
    async def _score_weight_distribution(self, location: Dict[str, Any], product: Product) -> float:
        """Puntuación basada en distribución de peso"""
        if not hasattr(product, 'peso') or not product.peso:
            return 5.0
        
        try:
            peso = float(product.peso)
            estante_num = int(location["estante"].split('-')[0]) if '-' in location["estante"] else int(location["estante"])
            
            # Productos pesados en estantes bajos
            if peso > 10:  # Producto pesado
                if estante_num <= 2:
                    return 10.0  # Perfecto
                elif estante_num <= 4:
                    return 6.0   # Aceptable
                else:
                    return 2.0   # Evitar
            
            # Productos ligeros pueden ir en cualquier lado
            elif peso < 2:
                return 8.0  # Buen para cualquier estante
            
            # Productos de peso medio
            else:
                if estante_num <= 4:
                    return 8.0
                else:
                    return 5.0
                    
        except (ValueError, AttributeError):
            return 5.0
    
    async def _score_fifo_rotation(self, location: Dict[str, Any]) -> float:
        """Puntuación basada en rotación FIFO"""
        # Buscar productos más antiguos en la ubicación
        try:
            oldest_product = self.db.query(Inventory).filter(
                Inventory.zona == location["zona"],
                Inventory.estante == location["estante"],
                (Inventory.cantidad - Inventory.cantidad_reservada) > 0
            ).order_by(Inventory.created_at.asc()).first()
            
            if not oldest_product:
                return 8.0  # Ubicación nueva, buena para FIFO
            
            # Calcular días desde el producto más antiguo
            days_old = (datetime.utcnow() - oldest_product.created_at).days
            
            if days_old > 30:
                return 3.0  # Productos muy antiguos, evitar
            elif days_old > 14:
                return 6.0  # Productos algo antiguos
            else:
                return 8.0  # Productos recientes, OK para FIFO
                
        except Exception:
            return 5.0
    
    def _calculate_product_volume(self, product: Product) -> float:
        """Calcular volumen del producto"""
        if not product.dimensiones:
            return 1.0  # Volumen por defecto
        
        try:
            dims = product.dimensiones
            if isinstance(dims, dict):
                return dims.get('largo', 1) * dims.get('ancho', 1) * dims.get('alto', 1)
            return 1.0
        except:
            return 1.0
    
    def _get_adjacent_zones(self, zona: str) -> List[str]:
        """Obtener zonas adyacentes"""
        zone_map = {
            'A': ['B'],
            'B': ['A', 'C'],
            'C': ['B', 'D'],
            'D': ['C', 'E'],
            'E': ['D']
        }
        return zone_map.get(zona.upper(), [])
    
    async def _reserve_location(self, location: LocationScore, product: Product) -> bool:
        """Reservar ubicación para el producto"""
        try:
            # Buscar el registro de inventario
            inventory = self.db.query(Inventory).filter(
                Inventory.zona == location.zona,
                Inventory.estante == location.estante
            ).first()
            
            if inventory and inventory.cantidad_disponible() > 0:
                # Reducir capacidad disponible (reservar una unidad)
                inventory.cantidad_reservada += 1
                
                # Crear relación producto-inventario si no existe
                if hasattr(product, 'ubicaciones_inventario'):
                    product.ubicaciones_inventario.append(inventory)
                
                self.db.commit()
                return True
                
        except Exception as e:
            self.db.rollback()
            print(f"Error reservando ubicación: {e}")
            
        return False
    
    async def get_assignment_analytics(self) -> Dict[str, Any]:
        """Obtener analytics del sistema de asignación"""
        try:
            # Estadísticas de utilización por zona
            zones_stats = {}
            all_inventory = self.db.query(Inventory).filter(Inventory.deleted_at.is_(None)).all()
            
            for inv in all_inventory:
                zona = inv.zona
                if zona not in zones_stats:
                    zones_stats[zona] = {
                        "total_locations": 0,
                        "occupied_locations": 0,
                        "available_capacity": 0,
                        "total_capacity": 0
                    }
                
                zones_stats[zona]["total_locations"] += 1
                available_qty = inv.cantidad_disponible()
                total_capacity = getattr(inv, 'cantidad', 10)
                
                zones_stats[zona]["available_capacity"] += available_qty
                zones_stats[zona]["total_capacity"] += total_capacity
                
                if available_qty < total_capacity:
                    zones_stats[zona]["occupied_locations"] += 1
            
            # Calcular eficiencia
            for zona, stats in zones_stats.items():
                if stats["total_capacity"] > 0:
                    stats["utilization_rate"] = round(
                        ((stats["total_capacity"] - stats["available_capacity"]) / stats["total_capacity"]) * 100, 1
                    )
                else:
                    stats["utilization_rate"] = 0
            
            return {
                "zones_statistics": zones_stats,
                "total_locations": sum(z["total_locations"] for z in zones_stats.values()),
                "total_capacity": sum(z["total_capacity"] for z in zones_stats.values()),
                "total_available": sum(z["available_capacity"] for z in zones_stats.values()),
                "assignment_strategies": [strategy.value for strategy in AssignmentStrategy]
            }
            
        except Exception as e:
            print(f"Error getting analytics: {e}")
            return {}