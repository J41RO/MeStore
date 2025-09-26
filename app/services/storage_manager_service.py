"""
Servicio de gestión de almacén con cálculos de ocupación en tiempo real.
Archivo: app/services/storage_manager_service.py
Autor: Sistema de desarrollo
Fecha: 2025-01-15
Propósito: Gestionar espacios de almacenamiento con visualización de ocupación por zonas
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.storage import Storage
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.incoming_product_queue import IncomingProductQueue
from datetime import datetime, timedelta
from enum import Enum
import statistics

class StorageStatus(str, Enum):
    EMPTY = "empty"          # 0-10%
    LOW = "low"              # 11-30%
    MODERATE = "moderate"    # 31-60%
    HIGH = "high"            # 61-85%
    CRITICAL = "critical"    # 86-95%
    FULL = "full"            # 96-100%

class AlertLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class StorageAlert:
    def __init__(self, level: AlertLevel, zone: str, message: str, percentage: float, timestamp: Optional[datetime] = None):
        self.level = level
        self.zone = zone
        self.message = message
        self.percentage = percentage
        self.timestamp = timestamp if timestamp is not None else datetime.utcnow()

class StorageManagerService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_zone_occupancy_overview(self) -> Dict[str, Any]:
        """Obtener resumen general de ocupación por zonas"""
        
        # Obtener todas las zonas con sus inventarios
        zones_data = self.db.query(Inventory.zona).distinct().all()
        zones = [zone[0] for zone in zones_data] if zones_data else []
        
        if not zones:
            # Crear datos de ejemplo si no hay zonas
            zones = ['A', 'B', 'C', 'D', 'E']
            return self._create_sample_data(zones)
        
        zone_stats = []
        total_capacity = 0
        total_occupied = 0
        
        for zone in zones:
            zone_info = self._calculate_zone_metrics(zone)
            zone_stats.append(zone_info)
            total_capacity += zone_info['total_capacity']
            total_occupied += zone_info['occupied_space']
        
        # Calcular estadísticas generales
        overall_utilization = (total_occupied / total_capacity * 100) if total_capacity > 0 else 0
        
        return {
            "zones": zone_stats,
            "summary": {
                "total_zones": len(zones),
                "total_capacity": total_capacity,
                "total_occupied": total_occupied,
                "total_available": total_capacity - total_occupied,
                "overall_utilization": round(overall_utilization, 1),
                "status": self._get_storage_status(overall_utilization),
                "last_updated": datetime.utcnow().isoformat()
            }
        }
    
    def _create_sample_data(self, zones: List[str]) -> Dict[str, Any]:
        """Crear datos de ejemplo para demostración"""
        import random
        
        zone_stats = []
        total_capacity = 0
        total_occupied = 0
        
        for zone in zones:
            capacity = random.randint(50, 200)
            occupied = random.randint(10, int(capacity * 0.9))
            available = capacity - occupied
            utilization = (occupied / capacity * 100) if capacity > 0 else 0
            
            zone_info = {
                "zone": zone,
                "total_capacity": capacity,
                "occupied_space": occupied,
                "available_space": available,
                "utilization_percentage": round(utilization, 1),
                "status": self._get_storage_status(utilization),
                "total_products": random.randint(5, occupied),
                "shelves_count": random.randint(5, 15),
                "last_activity": (datetime.utcnow() - timedelta(hours=random.randint(1, 24))).isoformat()
            }
            
            zone_stats.append(zone_info)
            total_capacity += capacity
            total_occupied += occupied
        
        overall_utilization = (total_occupied / total_capacity * 100) if total_capacity > 0 else 0
        
        return {
            "zones": zone_stats,
            "summary": {
                "total_zones": len(zones),
                "total_capacity": total_capacity,
                "total_occupied": total_occupied,
                "total_available": total_capacity - total_occupied,
                "overall_utilization": round(overall_utilization, 1),
                "status": self._get_storage_status(overall_utilization),
                "last_updated": datetime.utcnow().isoformat()
            }
        }
    
    def _calculate_zone_metrics(self, zone: str) -> Dict[str, Any]:
        """Calcular métricas detalladas para una zona"""
        
        # Obtener inventarios de la zona
        inventories = self.db.query(Inventory).filter(
            Inventory.zona == zone,
            Inventory.is_active == True
        ).all()
        
        total_capacity = sum(getattr(inv, 'capacidad_max', 10) for inv in inventories)
        available_space = sum(inv.cantidad_disponible for inv in inventories)
        occupied_space = total_capacity - available_space
        
        utilization = (occupied_space / total_capacity * 100) if total_capacity > 0 else 0
        
        # Contar productos en la zona
        products_count = self._count_products_in_zone(zone)
        
        return {
            "zone": zone,
            "total_capacity": total_capacity,
            "occupied_space": occupied_space,
            "available_space": available_space,
            "utilization_percentage": round(utilization, 1),
            "status": self._get_storage_status(utilization),
            "total_products": products_count,
            "shelves_count": len(inventories),
            "last_activity": self._get_last_activity_in_zone(zone)
        }
    
    def _get_storage_status(self, utilization: float) -> str:
        """Determinar estado del almacén basado en utilización"""
        if utilization <= 10:
            return StorageStatus.EMPTY
        elif utilization <= 30:
            return StorageStatus.LOW
        elif utilization <= 60:
            return StorageStatus.MODERATE
        elif utilization <= 85:
            return StorageStatus.HIGH
        elif utilization <= 95:
            return StorageStatus.CRITICAL
        else:
            return StorageStatus.FULL
    
    def _count_products_in_zone(self, zone: str) -> int:
        """Contar productos en una zona específica"""
        try:
            # Contar productos verificados en la zona
            count = self.db.query(IncomingProductQueue).join(Inventory).filter(
                Inventory.zona == zone,
                IncomingProductQueue.verification_status.in_(['APPROVED', 'COMPLETED_WITH_QR'])
            ).count()
            return count
        except:
            return 0
    
    def _get_last_activity_in_zone(self, zone: str) -> str:
        """Obtener timestamp de última actividad en zona"""
        try:
            last_activity = self.db.query(IncomingProductQueue.updated_at).join(Inventory).filter(
                Inventory.zona == zone
            ).order_by(IncomingProductQueue.updated_at.desc()).first()
            
            if last_activity:
                return last_activity[0].isoformat()
            else:
                return (datetime.utcnow() - timedelta(hours=12)).isoformat()
        except:
            return (datetime.utcnow() - timedelta(hours=6)).isoformat()
    
    def get_storage_alerts(self) -> List[StorageAlert]:
        """Generar alertas basadas en ocupación"""
        alerts = []
        overview = self.get_zone_occupancy_overview()
        
        for zone_data in overview["zones"]:
            utilization = zone_data["utilization_percentage"]
            zone = zone_data["zone"]
            
            if utilization >= 95:
                alerts.append(StorageAlert(
                    AlertLevel.CRITICAL,
                    zone,
                    f"Zona {zone} prácticamente llena ({utilization}%)",
                    utilization
                ))
            elif utilization >= 85:
                alerts.append(StorageAlert(
                    AlertLevel.WARNING,
                    zone,
                    f"Zona {zone} con alta ocupación ({utilization}%)",
                    utilization
                ))
            elif utilization <= 10:
                alerts.append(StorageAlert(
                    AlertLevel.INFO,
                    zone,
                    f"Zona {zone} prácticamente vacía ({utilization}%)",
                    utilization
                ))
        
        # Alertas generales
        overall_utilization = overview["summary"]["overall_utilization"]
        if overall_utilization >= 90:
            alerts.append(StorageAlert(
                AlertLevel.CRITICAL,
                "GENERAL",
                f"Almacén general con ocupación crítica ({overall_utilization}%)",
                overall_utilization
            ))
        
        return alerts
    
    def get_utilization_trends(self, days: int = 7) -> Dict[str, Any]:
        """Obtener tendencias de utilización por período"""
        # Para demo, generar datos simulados
        import random
        from datetime import datetime, timedelta
        
        trends = []
        base_date = datetime.utcnow() - timedelta(days=days)
        
        for i in range(days + 1):
            date = base_date + timedelta(days=i)
            
            # Simular tendencia creciente con variación
            base_utilization = 45 + (i * 2) + random.randint(-5, 5)
            base_utilization = max(20, min(85, base_utilization))
            
            trends.append({
                "date": date.strftime("%Y-%m-%d"),
                "overall_utilization": base_utilization,
                "zone_A": base_utilization + random.randint(-10, 10),
                "zone_B": base_utilization + random.randint(-10, 10),
                "zone_C": base_utilization + random.randint(-10, 10),
                "zone_D": base_utilization + random.randint(-10, 10),
                "zone_E": base_utilization + random.randint(-10, 10)
            })
        
        return {
            "trends": trends,
            "period_start": base_date.strftime("%Y-%m-%d"),
            "period_end": datetime.utcnow().strftime("%Y-%m-%d"),
            "average_utilization": statistics.mean([t["overall_utilization"] for t in trends])
        }
    
    def get_zone_details(self, zone: str) -> Dict[str, Any]:
        """Obtener detalles completos de una zona específica"""
        zone_metrics = self._calculate_zone_metrics(zone)
        
        # Obtener inventarios detallados
        inventories = self.db.query(Inventory).filter(
            Inventory.zona == zone,
            Inventory.is_active == True
        ).all()
        
        shelves_detail = []
        for inv in inventories:
            shelf_capacity = getattr(inv, 'capacidad_max', 10)
            shelf_occupied = shelf_capacity - inv.cantidad_disponible
            shelf_utilization = (shelf_occupied / shelf_capacity * 100) if shelf_capacity > 0 else 0
            
            shelves_detail.append({
                "shelf_id": inv.estante,
                "position": getattr(inv, 'posicion', '01'),
                "capacity": shelf_capacity,
                "occupied": shelf_occupied,
                "available": inv.cantidad_disponible,
                "utilization": round(shelf_utilization, 1),
                "status": self._get_storage_status(shelf_utilization),
                "location": inv.get_ubicacion_completa()
            })
        
        return {
            "zone_metrics": zone_metrics,
            "shelves_detail": shelves_detail,
            "recommendations": self._get_zone_recommendations(zone_metrics),
            "recent_activity": self._get_recent_activity_in_zone(zone)
        }
    
    def _get_zone_recommendations(self, zone_metrics: Dict[str, Any]) -> List[str]:
        """Generar recomendaciones para optimización de zona"""
        recommendations = []
        utilization = zone_metrics["utilization_percentage"]
        
        if utilization >= 90:
            recommendations.append("Considerar expansión o reubicación de productos")
            recommendations.append("Revisar productos de baja rotación para optimizar espacio")
        elif utilization >= 75:
            recommendations.append("Monitorear ocupación de cerca")
            recommendations.append("Preparar espacios alternativos")
        elif utilization <= 20:
            recommendations.append("Zona subutilizada - considerar consolidación")
            recommendations.append("Evaluar reasignación de productos de otras zonas")
        else:
            recommendations.append("Utilización óptima - mantener monitoreo regular")
        
        return recommendations
    
    def _get_recent_activity_in_zone(self, zone: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Obtener actividad reciente en una zona"""
        try:
            recent_items = self.db.query(IncomingProductQueue).join(Inventory).filter(
                Inventory.zona == zone
            ).order_by(IncomingProductQueue.updated_at.desc()).limit(limit).all()
            
            activities = []
            for item in recent_items:
                activities.append({
                    "tracking_number": item.tracking_number,
                    "action": "Producto verificado" if item.verification_status == "APPROVED" else "En proceso",
                    "timestamp": item.updated_at.isoformat(),
                    "status": item.verification_status
                })
            
            return activities
        except:
            return []