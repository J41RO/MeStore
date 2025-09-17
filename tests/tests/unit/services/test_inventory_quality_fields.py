"""
Tests específicos para campos de calidad en modelo Inventory.

Tests para:
- Enum CondicionProducto (5 valores)
- Campo condicion_producto con default NUEVO
- Campo notas_almacen nullable
- Métodos de business logic de calidad
- Método agregar_nota_almacen con timestamps
- Serialización to_dict con campos de calidad
"""

import pytest
import uuid
from datetime import datetime
from app.models.inventory import Inventory, CondicionProducto, InventoryStatus


class TestInventoryQualityFields:
    """Test suite para campos de calidad en Inventory"""

    def test_condicion_producto_enum_values(self):
        """Test que CondicionProducto tiene los 5 valores correctos"""
        valores_esperados = {
            "NUEVO", "USADO_EXCELENTE", "USADO_BUENO", 
            "USADO_REGULAR", "DAÑADO"
        }
        valores_reales = {c.value for c in CondicionProducto}
        assert valores_reales == valores_esperados
        assert len(list(CondicionProducto)) == 5

    def test_inventory_default_condition_nuevo(self):
        """Test que nuevo inventory tiene condición NUEVO por defecto"""
        inventory = Inventory(
            product_id=uuid.uuid4(),
            zona="A", estante="001", posicion="01",
            cantidad=100
        )
        assert inventory.condicion_producto == CondicionProducto.NUEVO
        assert inventory.es_producto_nuevo() == True
        assert inventory.obtener_nivel_calidad() == 5

    def test_notas_almacen_nullable(self):
        """Test que notas_almacen puede ser None"""
        inventory = Inventory(
            product_id=uuid.uuid4(),
            zona="A", estante="001", posicion="01",
            cantidad=100
        )
        assert inventory.notas_almacen is None
        assert inventory.tiene_notas() == False

    def test_es_producto_nuevo_method(self):
        """Test método es_producto_nuevo()"""
        inventory = Inventory(
            product_id=uuid.uuid4(),
            zona="A", estante="001", posicion="01",
            cantidad=100,
            condicion_producto=CondicionProducto.NUEVO
        )
        assert inventory.es_producto_nuevo() == True
        
        inventory.condicion_producto = CondicionProducto.USADO_EXCELENTE
        assert inventory.es_producto_nuevo() == False

    def test_es_producto_usado_method(self):
        """Test método es_producto_usado()"""
        inventory = Inventory(
            product_id=uuid.uuid4(),
            zona="A", estante="001", posicion="01",
            cantidad=100
        )
        
        # NUEVO no es usado
        inventory.condicion_producto = CondicionProducto.NUEVO
        assert inventory.es_producto_usado() == False
        
        # DAÑADO no es usado (es categoría separada)
        inventory.condicion_producto = CondicionProducto.DAÑADO
        assert inventory.es_producto_usado() == False
        
        # Todos los USADO_* sí son usados
        for condicion in [CondicionProducto.USADO_EXCELENTE, 
                         CondicionProducto.USADO_BUENO, 
                         CondicionProducto.USADO_REGULAR]:
            inventory.condicion_producto = condicion
            assert inventory.es_producto_usado() == True

    def test_requiere_inspeccion_method(self):
        """Test método requiere_inspeccion()"""
        inventory = Inventory(
            product_id=uuid.uuid4(),
            zona="A", estante="001", posicion="01",
            cantidad=100
        )
        
        # Solo USADO_REGULAR y DAÑADO requieren inspección
        inventory.condicion_producto = CondicionProducto.USADO_REGULAR
        assert inventory.requiere_inspeccion() == True
        
        inventory.condicion_producto = CondicionProducto.DAÑADO
        assert inventory.requiere_inspeccion() == True
        
        # Los demás no requieren inspección
        for condicion in [CondicionProducto.NUEVO, 
                         CondicionProducto.USADO_EXCELENTE,
                         CondicionProducto.USADO_BUENO]:
            inventory.condicion_producto = condicion
            assert inventory.requiere_inspeccion() == False

    def test_es_vendible_method(self):
        """Test método es_vendible()"""
        inventory = Inventory(
            product_id=uuid.uuid4(),
            zona="A", estante="001", posicion="01",
            cantidad=100
        )
        
        # Solo DAÑADO no es vendible
        inventory.condicion_producto = CondicionProducto.DAÑADO
        assert inventory.es_vendible() == False
        
        # Todos los demás sí son vendibles
        for condicion in [CondicionProducto.NUEVO,
                         CondicionProducto.USADO_EXCELENTE,
                         CondicionProducto.USADO_BUENO,
                         CondicionProducto.USADO_REGULAR]:
            inventory.condicion_producto = condicion
            assert inventory.es_vendible() == True

    def test_obtener_condicion_descripcion_method(self):
        """Test método obtener_condicion_descripcion()"""
        inventory = Inventory(
            product_id=uuid.uuid4(),
            zona="A", estante="001", posicion="01",
            cantidad=100
        )
        
        descripciones_esperadas = {
            CondicionProducto.NUEVO: "Producto nuevo",
            CondicionProducto.USADO_EXCELENTE: "Usado - Excelente estado",
            CondicionProducto.USADO_BUENO: "Usado - Buen estado",
            CondicionProducto.USADO_REGULAR: "Usado - Estado regular",
            CondicionProducto.DAÑADO: "Producto dañado"
        }
        
        for condicion, descripcion in descripciones_esperadas.items():
            inventory.condicion_producto = condicion
            assert inventory.obtener_condicion_descripcion() == descripcion

    def test_obtener_nivel_calidad_method(self):
        """Test método obtener_nivel_calidad() con ranking 1-5"""
        inventory = Inventory(
            product_id=uuid.uuid4(),
            zona="A", estante="001", posicion="01",
            cantidad=100
        )
        
        niveles_esperados = {
            CondicionProducto.DAÑADO: 1,
            CondicionProducto.USADO_REGULAR: 2,
            CondicionProducto.USADO_BUENO: 3,
            CondicionProducto.USADO_EXCELENTE: 4,
            CondicionProducto.NUEVO: 5
        }
        
        for condicion, nivel in niveles_esperados.items():
            inventory.condicion_producto = condicion
            assert inventory.obtener_nivel_calidad() == nivel

    def test_agregar_nota_almacen_method(self):
        """Test método agregar_nota_almacen() con timestamps"""
        inventory = Inventory(
            product_id=uuid.uuid4(),
            zona="A", estante="001", posicion="01",
            cantidad=100
        )
        user_id = uuid.uuid4()
        
        # Primera nota
        inventory.agregar_nota_almacen("Producto verificado", user_id)
        assert inventory.tiene_notas() == True
        assert "Producto verificado" in inventory.notas_almacen
        # Verificar formato de timestamp (fecha actual)
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        # Verificar que hay timestamp con formato [YYYY-MM-DD HH:MM]
        import re
        timestamp_pattern = r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}\]'
        assert re.search(timestamp_pattern, inventory.notas_almacen), f"No timestamp found in: {inventory.notas_almacen}"
        assert inventory.updated_by_id == user_id
        
        # Segunda nota (acumulativa)
        nota_anterior = inventory.notas_almacen
        inventory.agregar_nota_almacen("Revisión adicional", user_id)
        assert "Producto verificado" in inventory.notas_almacen
        assert "Revisión adicional" in inventory.notas_almacen
        assert inventory.notas_almacen != nota_anterior  # Cambió

    def test_to_dict_includes_quality_fields(self):
        """Test que to_dict() incluye todos los campos de calidad"""
        inventory = Inventory(
            product_id=uuid.uuid4(),
            zona="A", estante="001", posicion="01",
            cantidad=100,
            condicion_producto=CondicionProducto.USADO_BUENO
        )
        inventory.agregar_nota_almacen("Test note")
        
        dict_data = inventory.to_dict()
        
        # Verificar campos de calidad específicos
        campos_calidad_esperados = [
            "condicion_producto", "condicion_descripcion", 
            "nivel_calidad", "notas_almacen",
            "es_nuevo", "es_vendible", 
            "requiere_inspeccion", "tiene_notas"
        ]
        
        for campo in campos_calidad_esperados:
            assert campo in dict_data, f"Campo {campo} faltante en to_dict()"
        
        # Verificar valores correctos
        assert dict_data["condicion_producto"] == "USADO_BUENO"
        assert dict_data["condicion_descripcion"] == "Usado - Buen estado"
        assert dict_data["nivel_calidad"] == 3
        assert dict_data["es_nuevo"] == False
        assert dict_data["es_vendible"] == True
        assert dict_data["requiere_inspeccion"] == False
        assert dict_data["tiene_notas"] == True

    def test_repr_includes_condition(self):
        """Test que __repr__ incluye condición del producto"""
        inventory = Inventory(
            product_id=uuid.uuid4(),
            zona="A", estante="001", posicion="01",
            cantidad=100,
            condicion_producto=CondicionProducto.USADO_EXCELENTE,
            status=InventoryStatus.DISPONIBLE
        )
        
        repr_str = repr(inventory)
        assert "A-001-01" in repr_str  # Ubicación
        assert "DISPONIBLE" in repr_str  # Status
        assert "USADO_EXCELENTE" in repr_str  # Condición
        assert "100/100" in repr_str  # Cantidad disponible/total

    def test_business_logic_integration(self):
        """Test integración de business logic completa"""
        inventory = Inventory(
            product_id=uuid.uuid4(),
            zona="A", estante="001", posicion="01",
            cantidad=100,
            condicion_producto=CondicionProducto.DAÑADO
        )
        
        # Producto dañado no es vendible pero puede estar en inventario
        assert inventory.es_vendible() == False
        assert inventory.requiere_inspeccion() == True
        assert inventory.es_producto_usado() == False  # Dañado es categoría separada
        assert inventory.obtener_nivel_calidad() == 1  # Peor calidad
        
        # Puede tener notas explicando el daño
        inventory.agregar_nota_almacen("Producto con daño en esquina superior derecha")
        assert inventory.tiene_notas() == True
        assert "daño" in inventory.notas_almacen