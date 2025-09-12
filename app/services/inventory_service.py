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
    
    @staticmethod
    async def validate_location_availability(
        zona: str, 
        estante: str, 
        posicion: str, 
        exclude_inventory_id: Optional[UUID],
        db: AsyncSession
    ) -> dict:
        '''Valida si una ubicación está disponible para asignar un producto'''
        
        # Buscar si hay algún producto en esa ubicación (excluyendo el item actual si se proporciona)
        query = select(Inventory).where(
            and_(
                Inventory.zona == zona.upper(),
                Inventory.estante == estante.upper(),
                Inventory.posicion == posicion.upper(),
                Inventory.cantidad > 0  # Solo ubicaciones con stock
            )
        )
        
        # Excluir el item actual si se está reasignando
        if exclude_inventory_id:
            query = query.where(Inventory.id != exclude_inventory_id)
        
        result = await db.execute(query)
        existing_item = result.scalar_one_or_none()
        
        location_code = f"{zona.upper()}-{estante.upper()}-{posicion.upper()}"
        
        if existing_item:
            return {
                'available': False,
                'location_code': location_code,
                'occupied_by': {
                    'inventory_id': str(existing_item.id),
                    'product_id': str(existing_item.product_id) if existing_item.product_id else None,
                    'cantidad': existing_item.cantidad,
                    'status': existing_item.status.value
                },
                'error': f"La ubicación {location_code} ya está ocupada"
            }
        
        return {
            'available': True,
            'location_code': location_code,
            'error': None
        }
    
    @staticmethod
    async def get_available_locations_in_zone(
        zona: str,
        db: AsyncSession,
        limit: int = 50
    ) -> List[dict]:
        '''Obtiene ubicaciones disponibles en una zona específica'''
        
        # Buscar todas las ubicaciones ocupadas en la zona
        occupied_query = select(
            Inventory.zona,
            Inventory.estante, 
            Inventory.posicion
        ).where(
            and_(
                Inventory.zona == zona.upper(),
                Inventory.cantidad > 0
            )
        ).distinct()
        
        result = await db.execute(occupied_query)
        occupied_locations = result.fetchall()
        
        occupied_set = set()
        for loc in occupied_locations:
            occupied_set.add(f"{loc.zona}-{loc.estante}-{loc.posicion}")
        
        # Generar ubicaciones sugeridas disponibles (esto es un ejemplo básico)
        # En un sistema real, tendríamos un catálogo de ubicaciones físicas
        available_locations = []
        
        # Sugerir ubicaciones estándar para la zona
        zone_mapping = {
            'WAREHOUSE_A': {'aisles': ['A1', 'A2', 'A3'], 'shelves': ['01', '02', '03'], 'positions': ['01', '02', '03', '04']},
            'WAREHOUSE_B': {'aisles': ['B1', 'B2'], 'shelves': ['01', '02'], 'positions': ['01', '02']},
            'DISPLAY_AREA': {'aisles': ['D1'], 'shelves': ['01'], 'positions': ['01', '02', '03']},
            'STORAGE_ROOM': {'aisles': ['S1'], 'shelves': ['01', '02'], 'positions': ['01', '02']}
        }
        
        zone_config = zone_mapping.get(zona.upper(), {
            'aisles': ['A1'], 'shelves': ['01'], 'positions': ['01', '02']
        })
        
        count = 0
        for aisle in zone_config['aisles']:
            for shelf in zone_config['shelves']:
                for position in zone_config['positions']:
                    if count >= limit:
                        break
                    
                    location_code = f"{zona.upper()}-{aisle}-{shelf}-{position}"
                    if location_code not in occupied_set:
                        available_locations.append({
                            'zone': zona.upper(),
                            'aisle': aisle,
                            'shelf': shelf,
                            'position': position,
                            'location_code': location_code,
                            'capacity': 100,  # Capacidad por defecto
                            'type': 'standard'  # Tipo de ubicación
                        })
                        count += 1
                if count >= limit:
                    break
            if count >= limit:
                break
        
        return available_locations
    
    @staticmethod
    async def validate_location_format(zona: str, estante: str, posicion: str) -> dict:
        '''Valida el formato de una ubicación según las reglas de negocio'''
        
        errors = []
        
        # Validar zona
        if not zona or not zona.strip():
            errors.append("La zona es requerida")
        elif not zona.isalnum():
            errors.append("La zona debe ser alfanumérica")
        elif len(zona) > 10:
            errors.append("La zona no puede tener más de 10 caracteres")
        
        # Validar estante
        if not estante or not estante.strip():
            errors.append("El estante es requerido")
        elif not estante.replace('-', '').isalnum():
            errors.append("El estante debe contener solo números, letras y guiones")
        elif len(estante) > 20:
            errors.append("El estante no puede tener más de 20 caracteres")
        
        # Validar posición
        if not posicion or not posicion.strip():
            errors.append("La posición es requerida")
        elif not posicion.replace('-', '').isalnum():
            errors.append("La posición debe contener solo números, letras y guiones")
        elif len(posicion) > 20:
            errors.append("La posición no puede tener más de 20 caracteres")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'formatted_location': {
                'zona': zona.upper().strip() if zona else '',
                'estante': estante.upper().strip() if estante else '',
                'posicion': posicion.upper().strip() if posicion else ''
            }
        }