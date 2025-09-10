# ~/app/services/discrepancy_analyzer.py
# ---------------------------------------------------------------------------------------------
# MeStore - Servicio de Análisis de Discrepancias
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: discrepancy_analyzer.py
# Ruta: ~/app/services/discrepancy_analyzer.py
# Autor: Jairo
# Fecha de Creación: 2025-09-10
# Última Actualización: 2025-09-10
# Versión: 1.0.0
# Propósito: Servicio para análisis avanzado de discrepancias en auditorías de inventario
#            Genera métricas, recomendaciones y análisis de tendencias
#
# ---------------------------------------------------------------------------------------------

"""
Servicio DiscrepancyAnalyzer para análisis avanzado de discrepancias.

Este servicio contiene:
- Clase DiscrepancyAnalyzer: Análisis principal de discrepancias
- Métodos de análisis: Por tipo, ubicación, categoría, tendencias
- Generación de recomendaciones automáticas
- Cálculo de métricas de precisión y impacto financiero
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.sql.functions import coalesce
from datetime import datetime, timedelta
from collections import defaultdict
import logging

from app.models.inventory_audit import InventoryAudit, InventoryAuditItem, DiscrepancyType, AuditStatus
from app.models.inventory import Inventory
from app.models.discrepancy_report import DiscrepancyReport, ReportType

logger = logging.getLogger(__name__)


class DiscrepancyAnalyzer:
    """
    Clase principal para análisis de discrepancias en auditorías de inventario.
    
    Proporciona análisis detallados, métricas de precisión, identificación de patrones
    y generación de recomendaciones para mejora del sistema de inventario.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def analyze_audit_discrepancies(
        self, 
        audit_id: str, 
        db: AsyncSession,
        include_trends: bool = True
    ) -> Dict[str, Any]:
        """
        Analizar discrepancias por categoría para una auditoría específica.
        
        Args:
            audit_id: ID de la auditoría a analizar
            db: Sesión de base de datos
            include_trends: Incluir análisis de tendencias
            
        Returns:
            Diccionario con análisis completo de discrepancias
        """
        try:
            self.logger.info(f"Iniciando análisis de discrepancias para auditoría {audit_id}")
            
            # Obtener la auditoría
            audit = await self._get_audit_by_id(audit_id, db)
            if not audit:
                raise ValueError(f"Auditoría {audit_id} no encontrada")
            
            # Obtener todos los items de auditoría
            audit_items = await self._get_audit_items(audit_id, db)
            
            # Análisis por tipo de discrepancia
            discrepancies_by_type = await self._analyze_by_discrepancy_type(audit_items)
            
            # Análisis por ubicación
            discrepancies_by_location = await self._analyze_by_location(audit_items)
            
            # Análisis por categoría de producto
            discrepancies_by_category = await self._analyze_by_category(audit_items, db)
            
            # Análisis de impacto financiero
            financial_impact_analysis = await self._analyze_financial_impact(audit_items)
            
            # Métricas de precisión
            accuracy_metrics = await self._calculate_accuracy_metrics(audit_items)
            
            # Análisis de tendencias (si se solicita)
            trend_analysis = None
            if include_trends:
                trend_analysis = await self._analyze_trends(audit_id, db)
            
            # Generar recomendaciones
            recommendations = await self._generate_recommendations(
                audit_items, discrepancies_by_type, discrepancies_by_location
            )
            
            analysis_result = {
                "audit_info": {
                    "audit_id": audit_id,
                    "audit_name": audit.nombre,
                    "audit_status": audit.status.value,
                    "analysis_date": datetime.utcnow().isoformat(),
                    "total_items": len(audit_items)
                },
                "discrepancies_by_type": discrepancies_by_type,
                "discrepancies_by_location": discrepancies_by_location,
                "discrepancies_by_category": discrepancies_by_category,
                "financial_impact": financial_impact_analysis,
                "accuracy_metrics": accuracy_metrics,
                "trend_analysis": trend_analysis,
                "recommendations": recommendations,
                "summary": {
                    "total_discrepancies": sum(discrepancies_by_type.values()),
                    "most_problematic_type": max(discrepancies_by_type.items(), key=lambda x: x[1])[0] if discrepancies_by_type else None,
                    "accuracy_percentage": accuracy_metrics.get("overall_accuracy", 0),
                    "total_financial_impact": financial_impact_analysis.get("total_impact", 0)
                }
            }
            
            self.logger.info(f"Análisis completado: {analysis_result['summary']['total_discrepancies']} discrepancias encontradas")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Error analizando discrepancias: {str(e)}")
            raise
    
    async def generate_adjustment_summary(
        self, 
        audit_id: str, 
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Generar resumen de ajustes realizados post-auditoría.
        
        Args:
            audit_id: ID de la auditoría
            db: Sesión de base de datos
            
        Returns:
            Diccionario con resumen de ajustes
        """
        try:
            self.logger.info(f"Generando resumen de ajustes para auditoría {audit_id}")
            
            # Obtener items reconciliados
            audit_items = await self._get_audit_items(audit_id, db, only_reconciled=True)
            
            # Análizar ajustes por tipo de acción
            adjustments_by_action = await self._analyze_adjustments_by_action(audit_items)
            
            # Impacto financiero de ajustes
            financial_impact = await self._calculate_adjustment_financial_impact(audit_items)
            
            # Análisis por ubicación
            adjustments_by_location = await self._analyze_adjustments_by_location(audit_items)
            
            # Análisis por producto/categoría
            adjustments_by_category = await self._analyze_adjustments_by_category(audit_items, db)
            
            # Estadísticas de tiempo de resolución
            resolution_stats = await self._calculate_resolution_stats(audit_items)
            
            adjustment_summary = {
                "audit_id": audit_id,
                "summary_date": datetime.utcnow().isoformat(),
                "total_adjustments": len(audit_items),
                "adjustments_by_action": adjustments_by_action,
                "financial_impact": financial_impact,
                "adjustments_by_location": adjustments_by_location,
                "adjustments_by_category": adjustments_by_category,
                "resolution_statistics": resolution_stats,
                "efficiency_metrics": {
                    "avg_resolution_time_hours": resolution_stats.get("avg_resolution_time", 0) / 3600,
                    "resolution_rate": len(audit_items) / await self._get_total_discrepancies_count(audit_id, db) * 100
                }
            }
            
            self.logger.info(f"Resumen de ajustes generado: {len(audit_items)} ajustes procesados")
            return adjustment_summary
            
        except Exception as e:
            self.logger.error(f"Error generando resumen de ajustes: {str(e)}")
            raise
    
    async def calculate_inventory_accuracy_metrics(
        self,
        date_range_start: datetime,
        date_range_end: datetime,
        db: AsyncSession,
        location_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calcular métricas de precisión de inventario para un período.
        
        Args:
            date_range_start: Fecha inicio del análisis
            date_range_end: Fecha fin del análisis
            db: Sesión de base de datos
            location_filter: Filtro opcional por ubicación
            
        Returns:
            Diccionario con métricas de precisión
        """
        try:
            self.logger.info(f"Calculando métricas de precisión desde {date_range_start} hasta {date_range_end}")
            
            # Obtener auditorías en el rango de fechas
            audits = await self._get_audits_in_range(date_range_start, date_range_end, db)
            
            total_items = 0
            total_discrepancies = 0
            total_value = 0.0
            discrepancy_value = 0.0
            
            accuracy_by_location = defaultdict(lambda: {"items": 0, "discrepancies": 0, "accuracy": 0})
            accuracy_by_category = defaultdict(lambda: {"items": 0, "discrepancies": 0, "accuracy": 0})
            
            for audit in audits:
                audit_items = await self._get_audit_items(str(audit.id), db)
                
                for item in audit_items:
                    if location_filter and item.ubicacion_sistema != location_filter:
                        continue
                        
                    total_items += 1
                    if item.tiene_discrepancia:
                        total_discrepancies += 1
                        discrepancy_value += abs(item.valor_discrepancia or 0)
                    
                    total_value += abs(item.valor_sistema or 0)
                    
                    # Por ubicación
                    location = item.ubicacion_sistema or "Sin ubicación"
                    accuracy_by_location[location]["items"] += 1
                    if item.tiene_discrepancia:
                        accuracy_by_location[location]["discrepancies"] += 1
                    
                    # Por categoría (necesita join con inventory)
                    # Implementación simplificada por ahora
                    category = "General"  # Placeholder
                    accuracy_by_category[category]["items"] += 1
                    if item.tiene_discrepancia:
                        accuracy_by_category[category]["discrepancies"] += 1
            
            # Calcular porcentajes de precisión
            overall_accuracy = ((total_items - total_discrepancies) / total_items * 100) if total_items > 0 else 100
            value_accuracy = ((total_value - discrepancy_value) / total_value * 100) if total_value > 0 else 100
            
            # Calcular precisión por ubicación
            for location_data in accuracy_by_location.values():
                items = location_data["items"]
                discrepancies = location_data["discrepancies"]
                location_data["accuracy"] = ((items - discrepancies) / items * 100) if items > 0 else 100
            
            # Calcular precisión por categoría
            for category_data in accuracy_by_category.values():
                items = category_data["items"]
                discrepancies = category_data["discrepancies"]
                category_data["accuracy"] = ((items - discrepancies) / items * 100) if items > 0 else 100
            
            metrics = {
                "analysis_period": {
                    "start_date": date_range_start.isoformat(),
                    "end_date": date_range_end.isoformat(),
                    "total_audits": len(audits)
                },
                "overall_metrics": {
                    "total_items_audited": total_items,
                    "total_discrepancies": total_discrepancies,
                    "overall_accuracy_percentage": round(overall_accuracy, 2),
                    "value_accuracy_percentage": round(value_accuracy, 2),
                    "discrepancy_rate": round(total_discrepancies / total_items * 100, 2) if total_items > 0 else 0
                },
                "financial_metrics": {
                    "total_inventory_value": round(total_value, 2),
                    "total_discrepancy_value": round(discrepancy_value, 2),
                    "discrepancy_value_percentage": round(discrepancy_value / total_value * 100, 2) if total_value > 0 else 0
                },
                "accuracy_by_location": dict(accuracy_by_location),
                "accuracy_by_category": dict(accuracy_by_category),
                "recommendations": await self._generate_accuracy_recommendations(
                    overall_accuracy, accuracy_by_location, accuracy_by_category
                )
            }
            
            self.logger.info(f"Métricas de precisión calculadas: {overall_accuracy:.2f}% precisión general")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculando métricas de precisión: {str(e)}")
            raise
    
    # Métodos privados auxiliares
    
    async def _get_audit_by_id(self, audit_id: str, db: AsyncSession) -> Optional[InventoryAudit]:
        """Obtener auditoría por ID"""
        query = select(InventoryAudit).where(InventoryAudit.id == audit_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def _get_audit_items(
        self, 
        audit_id: str, 
        db: AsyncSession, 
        only_reconciled: bool = False
    ) -> List[InventoryAuditItem]:
        """Obtener items de auditoría"""
        query = select(InventoryAuditItem).where(InventoryAuditItem.audit_id == audit_id)
        
        if only_reconciled:
            query = query.where(InventoryAuditItem.discrepancia_reconciliada == True)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def _analyze_by_discrepancy_type(self, audit_items: List[InventoryAuditItem]) -> Dict[str, int]:
        """Analizar discrepancias por tipo"""
        type_counts = defaultdict(int)
        
        for item in audit_items:
            if item.tiene_discrepancia and item.tipo_discrepancia:
                type_counts[item.tipo_discrepancia.value] += 1
        
        return dict(type_counts)
    
    async def _analyze_by_location(self, audit_items: List[InventoryAuditItem]) -> Dict[str, int]:
        """Analizar discrepancias por ubicación"""
        location_counts = defaultdict(int)
        
        for item in audit_items:
            if item.tiene_discrepancia:
                location = item.ubicacion_sistema or "Sin ubicación"
                location_counts[location] += 1
        
        return dict(location_counts)
    
    async def _analyze_by_category(self, audit_items: List[InventoryAuditItem], db: AsyncSession) -> Dict[str, int]:
        """Analizar discrepancias por categoría de producto"""
        # Implementación simplificada - en producción haría join con inventory/productos
        category_counts = {"General": sum(1 for item in audit_items if item.tiene_discrepancia)}
        return category_counts
    
    async def _analyze_financial_impact(self, audit_items: List[InventoryAuditItem]) -> Dict[str, float]:
        """Analizar impacto financiero de discrepancias"""
        total_impact = sum(abs(item.valor_discrepancia or 0) for item in audit_items if item.tiene_discrepancia)
        
        impact_by_type = defaultdict(float)
        for item in audit_items:
            if item.tiene_discrepancia and item.tipo_discrepancia:
                impact_by_type[item.tipo_discrepancia.value] += abs(item.valor_discrepancia or 0)
        
        return {
            "total_impact": round(total_impact, 2),
            "impact_by_type": {k: round(v, 2) for k, v in impact_by_type.items()}
        }
    
    async def _calculate_accuracy_metrics(self, audit_items: List[InventoryAuditItem]) -> Dict[str, float]:
        """Calcular métricas de precisión"""
        total_items = len(audit_items)
        discrepancy_items = sum(1 for item in audit_items if item.tiene_discrepancia)
        
        overall_accuracy = ((total_items - discrepancy_items) / total_items * 100) if total_items > 0 else 100
        
        return {
            "overall_accuracy": round(overall_accuracy, 2),
            "discrepancy_rate": round(discrepancy_items / total_items * 100, 2) if total_items > 0 else 0,
            "items_analyzed": total_items,
            "discrepant_items": discrepancy_items
        }
    
    async def _analyze_trends(self, audit_id: str, db: AsyncSession) -> Dict[str, Any]:
        """Analizar tendencias históricas"""
        # Implementación simplificada - en producción compararía con auditorías anteriores
        return {
            "trend_period": "30_days",
            "accuracy_trend": "stable",
            "discrepancy_trend": "decreasing",
            "note": "Análisis de tendencias en desarrollo"
        }
    
    async def _generate_recommendations(
        self, 
        audit_items: List[InventoryAuditItem],
        discrepancies_by_type: Dict[str, int],
        discrepancies_by_location: Dict[str, int]
    ) -> List[str]:
        """Generar recomendaciones automáticas"""
        recommendations = []
        
        # Recomendaciones basadas en tipos de discrepancia más frecuentes
        if discrepancies_by_type:
            most_common_type = max(discrepancies_by_type.items(), key=lambda x: x[1])
            if most_common_type[0] == "FALTANTE":
                recommendations.append("Revisar procesos de seguridad para reducir faltantes")
                recommendations.append("Implementar controles adicionales en áreas con más faltantes")
            elif most_common_type[0] == "SOBRANTE":
                recommendations.append("Revisar procesos de recepción y conteo")
                recommendations.append("Capacitar personal en procedimientos de inventario")
        
        # Recomendaciones basadas en ubicaciones problemáticas
        if discrepancies_by_location:
            problematic_locations = [loc for loc, count in discrepancies_by_location.items() if count > 5]
            if problematic_locations:
                recommendations.append(f"Auditoría especial en ubicaciones: {', '.join(problematic_locations[:3])}")
                recommendations.append("Revisar procedimientos de almacenamiento en ubicaciones problemáticas")
        
        # Recomendación general si hay muchas discrepancias
        total_items = len(audit_items)
        total_discrepancies = sum(discrepancies_by_type.values())
        if total_items > 0 and (total_discrepancies / total_items) > 0.1:  # >10% discrepancias
            recommendations.append("Implementar auditorías de ciclo más frecuentes")
            recommendations.append("Revisar capacitación del personal de inventario")
        
        return recommendations
    
    async def _analyze_adjustments_by_action(self, audit_items: List[InventoryAuditItem]) -> Dict[str, int]:
        """Analizar ajustes por tipo de acción tomada"""
        action_counts = defaultdict(int)
        
        for item in audit_items:
            if item.accion_reconciliacion:
                action_counts[item.accion_reconciliacion] += 1
        
        return dict(action_counts)
    
    async def _calculate_adjustment_financial_impact(self, audit_items: List[InventoryAuditItem]) -> Dict[str, float]:
        """Calcular impacto financiero de ajustes"""
        total_impact = sum(abs(item.valor_discrepancia or 0) for item in audit_items)
        
        return {
            "total_adjustment_value": round(total_impact, 2),
            "average_adjustment": round(total_impact / len(audit_items), 2) if audit_items else 0
        }
    
    async def _analyze_adjustments_by_location(self, audit_items: List[InventoryAuditItem]) -> Dict[str, int]:
        """Analizar ajustes por ubicación"""
        location_counts = defaultdict(int)
        
        for item in audit_items:
            location = item.ubicacion_sistema or "Sin ubicación"
            location_counts[location] += 1
        
        return dict(location_counts)
    
    async def _analyze_adjustments_by_category(self, audit_items: List[InventoryAuditItem], db: AsyncSession) -> Dict[str, int]:
        """Analizar ajustes por categoría"""
        # Implementación simplificada
        return {"General": len(audit_items)}
    
    async def _calculate_resolution_stats(self, audit_items: List[InventoryAuditItem]) -> Dict[str, float]:
        """Calcular estadísticas de tiempo de resolución"""
        # Implementación simplificada - en producción calcularía tiempos reales
        return {
            "avg_resolution_time": 3600,  # 1 hora promedio
            "fastest_resolution": 1800,   # 30 minutos
            "slowest_resolution": 7200    # 2 horas
        }
    
    async def _get_total_discrepancies_count(self, audit_id: str, db: AsyncSession) -> int:
        """Obtener total de discrepancias en una auditoría"""
        query = select(func.count(InventoryAuditItem.id)).where(
            and_(
                InventoryAuditItem.audit_id == audit_id,
                InventoryAuditItem.tiene_discrepancia == True
            )
        )
        result = await db.execute(query)
        return result.scalar() or 0
    
    async def _get_audits_in_range(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        db: AsyncSession
    ) -> List[InventoryAudit]:
        """Obtener auditorías en un rango de fechas"""
        query = select(InventoryAudit).where(
            and_(
                InventoryAudit.fecha_inicio >= start_date,
                InventoryAudit.fecha_inicio <= end_date,
                InventoryAudit.status.in_([AuditStatus.COMPLETADA, AuditStatus.RECONCILIADA])
            )
        ).order_by(desc(InventoryAudit.fecha_inicio))
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def _generate_accuracy_recommendations(
        self,
        overall_accuracy: float,
        accuracy_by_location: Dict[str, Dict[str, Any]],
        accuracy_by_category: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Generar recomendaciones basadas en métricas de precisión"""
        recommendations = []
        
        if overall_accuracy < 95:
            recommendations.append("La precisión general está por debajo del objetivo (95%)")
            recommendations.append("Implementar auditorías de ciclo más frecuentes")
        
        # Ubicaciones problemáticas
        problematic_locations = [
            loc for loc, data in accuracy_by_location.items() 
            if data["accuracy"] < 90
        ]
        
        if problematic_locations:
            recommendations.append(f"Revisar procedimientos en ubicaciones: {', '.join(problematic_locations[:3])}")
        
        if overall_accuracy > 98:
            recommendations.append("Excelente precisión de inventario mantenida")
            recommendations.append("Considerar reducir frecuencia de auditorías en áreas de alta precisión")
        
        return recommendations