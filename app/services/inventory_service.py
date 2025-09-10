from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.inventory import Inventory
from app.models.inventory_audit import InventoryAudit, InventoryAuditItem

class InventoryService:
    '''Servicio para lógica de negocio de inventario y auditorías'''
    
    @staticmethod
    async def compare_physical_vs_system(audit_id: UUID, db: AsyncSession) -> dict:
        '''Compara cantidades físicas vs sistema y detecta discrepancias'''
        # Obtener auditoría y sus items
        audit_query = select(InventoryAudit).where(InventoryAudit.id == audit_id)
        audit_result = await db.execute(audit_query)
        audit = audit_result.scalar_one_or_none()
        
        if not audit:
            raise ValueError(f'Auditoría {audit_id} no encontrada')
        
        # Obtener items de auditoría con datos del inventario
        items_query = select(InventoryAuditItem).where(InventoryAuditItem.audit_id == audit_id)
        items_result = await db.execute(items_query)
        audit_items = items_result.scalars().all()
        
        # Procesar comparación para cada item
        discrepancies = []
        total_items = len(audit_items)
        items_with_discrepancies = 0
        
        for item in audit_items:
            if item.conteo_completado and item.tiene_discrepancia:
                discrepancy_data = {
                    'item_id': str(item.id),
                    'inventory_id': str(item.inventory_id),
                    'cantidad_sistema': item.cantidad_sistema,
                    'cantidad_fisica': item.cantidad_fisica,
                    'diferencia': item.diferencia_cantidad,
                    'tipo_discrepancia': item.tipo_discrepancia.value if item.tipo_discrepancia else None,
                    'ubicacion_sistema': item.ubicacion_sistema,
                    'ubicacion_fisica': item.ubicacion_fisica
                }
                discrepancies.append(discrepancy_data)
                items_with_discrepancies += 1
        
        # Actualizar estadísticas de la auditoría
        audit.total_items_auditados = total_items
        audit.discrepancies_found = items_with_discrepancies
        await db.commit()
        
        return {
            'audit_id': str(audit_id),
            'total_items': total_items,
            'items_with_discrepancies': items_with_discrepancies,
            'discrepancies': discrepancies,
            'completion_rate': (total_items - sum(1 for item in audit_items if not item.conteo_completado)) / total_items * 100 if total_items > 0 else 0
        }