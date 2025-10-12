# ANÁLISIS CRÍTICO: MIGRACIÓN FLOAT → DECIMAL PARA MONTOS MONETARIOS

**Fecha**: 2025-10-02
**Agente**: database-performance-ai
**Severidad**: 🔴 CRÍTICA - Impacto financiero directo
**Estado**: ANÁLISIS COMPLETADO - PENDIENTE APROBACIÓN PARA IMPLEMENTACIÓN

---

## 📊 RESUMEN EJECUTIVO

Se ha detectado un **problema crítico de precisión financiera** en el sistema MeStore: múltiples tablas están usando el tipo de dato `FLOAT` para almacenar montos monetarios, lo que puede causar **errores de redondeo acumulativos** y **pérdida de precisión** en cálculos financieros.

### Impacto Estimado
- **13 campos monetarios** usando Float en lugar de Decimal
- **6 tablas críticas** afectadas (orders, order_items, order_transactions, admin_activity_log, inventory_audit, discrepancy_report)
- **Riesgo financiero**: Errores de redondeo en cálculos de totales, impuestos, descuentos y comisiones
- **Riesgo legal**: Discrepancias en auditorías financieras y reportes contables

---

## 🔍 CAMPOS AFECTADOS - INVENTARIO COMPLETO

### 1. **TABLA: orders** (CRÍTICO - Transacciones financieras)
| Campo | Tipo Actual | Tipo Requerido | Línea | Uso |
|-------|-------------|----------------|-------|-----|
| `subtotal` | Float | DECIMAL(12,2) | 35 | Subtotal antes de impuestos |
| `tax_amount` | Float | DECIMAL(12,2) | 36 | Monto de impuestos |
| `shipping_cost` | Float | DECIMAL(12,2) | 37 | Costo de envío |
| `discount_amount` | Float | DECIMAL(12,2) | 38 | Monto de descuento |
| `total_amount` | Float | DECIMAL(12,2) | 39 | **Total final (CRÍTICO)** |

**Riesgo**: Totales incorrectos en órdenes pueden causar cobros incorrectos a clientes.

### 2. **TABLA: order_items** (CRÍTICO - Líneas de pedido)
| Campo | Tipo Actual | Tipo Requerido | Línea | Uso |
|-------|-------------|----------------|-------|-----|
| `unit_price` | Float | DECIMAL(10,2) | 98 | Precio unitario del producto |
| `total_price` | Float | DECIMAL(10,2) | 100 | Total de la línea (qty × price) |

**Riesgo**: Cálculos de totales de línea incorrectos afectan el total de la orden.

### 3. **TABLA: order_transactions** (CRÍTICO - Pagos)
| Campo | Tipo Actual | Tipo Requerido | Línea | Uso |
|-------|-------------|----------------|-------|-----|
| `amount` | Float | DECIMAL(12,2) | 122 | **Monto de transacción de pago** |

**Riesgo**: Errores en montos de pagos pueden causar discrepancias con gateways de pago.

### 4. **TABLA: admin_activity_log** (ALTO - Auditoría)
| Campo | Tipo Actual | Tipo Requerido | Línea | Uso |
|-------|-------------|----------------|-------|-----|
| `old_price` | Float | DECIMAL(12,2) | 302 | Precio anterior (auditoría) |
| `new_price` | Float | DECIMAL(12,2) | 308 | Precio nuevo (auditoría) |
| `price_difference` | Float | DECIMAL(12,2) | 314 | Diferencia de precio |

**Riesgo**: Auditorías de cambios de precios con valores incorrectos.

### 5. **TABLA: inventory_audit** (MEDIO - Reportes de inventario)
| Campo | Tipo Actual | Tipo Requerido | Línea | Uso |
|-------|-------------|----------------|-------|-----|
| `valor_discrepancias` | Float | DECIMAL(12,2) | 43 | Valor de discrepancias |
| `valor_discrepancia` | Float | DECIMAL(12,2) | 93 | Valor individual de discrepancia |

**Riesgo**: Reportes de auditoría de inventario con valores monetarios incorrectos.

### 6. **TABLA: discrepancy_report** (MEDIO - Reportes)
| Campo | Tipo Actual | Tipo Requerido | Línea | Uso |
|-------|-------------|----------------|-------|-----|
| `valor_unitario_registrado` | Float | DECIMAL(12,2) | 190 | Valor unitario registrado |
| `valor_unitario_fisico` | Float | DECIMAL(12,2) | 196 | Valor unitario físico |
| `valor_total_discrepancia` | Float | DECIMAL(12,2) | 251 | Valor total de discrepancia |

**Riesgo**: Reportes de discrepancias con valores monetarios imprecisos.

---

## ✅ CAMPOS YA CORRECTOS (No requieren migración)

### Models usando DECIMAL correctamente:
- ✅ **product.py**: `precio_venta`, `precio_costo`, `comision_mestocker` → DECIMAL(10,2)
- ✅ **transaction.py**: `monto`, `porcentaje_mestocker`, `monto_vendedor` → DECIMAL(12,2)
- ✅ **commission.py**: `order_amount`, `commission_rate`, `commission_amount`, `vendor_amount`, `platform_amount` → DECIMAL(10,2)
- ✅ **payout_request.py**: `monto_solicitado` → DECIMAL(12,2)

### Schemas Pydantic usando Decimal correctamente:
- ✅ **order.py**: Usa `Decimal` con validaciones `ge=0`
- ✅ **product.py**: Usa `Decimal` con rangos validados
- ✅ **commission.py**: Usa `Decimal` con validaciones financieras robustas

---

## ⚠️ PROBLEMAS DETECTADOS EN QUERIES Y SERVICIOS

### 1. **Operaciones matemáticas con Float en services**
```python
# commission_service.py - Línea 194-196 (YA CORRIGIÓ)
# Usa Decimal correctamente con ROUND_HALF_UP
commission_amount = (order_amount * commission_rate).quantize(
    Decimal('0.01'), rounding=ROUND_HALF_UP
)
```

### 2. **Conversión Float en to_dict() de modelos**
```python
# product.py - Línea 710-714
"precio_venta": float(self.precio_venta) if self.precio_venta else None,
"precio_costo": float(self.precio_costo) if self.precio_costo else None,
```
**Problema**: Conversión de Decimal → float pierde precisión en serialización.
**Solución**: Usar `str(self.precio_venta)` o configurar JSON encoder con Decimal.

### 3. **Comparaciones de igualdad potencialmente afectadas**
```python
# En queries que comparan montos exactos
WHERE total_amount = 150000.00  # Puede fallar con float
```
**Solución**: Usar rangos de comparación para float: `BETWEEN amount - 0.01 AND amount + 0.01`

---

## 📋 MIGRATION PLAN - PASO A PASO

### **FASE 1: PREPARACIÓN (1-2 días)**

#### 1.1 Validación Pre-Migración
```bash
# Script de validación de datos existentes
python scripts/validate_float_data_integrity.py
```

#### 1.2 Backup de Datos Críticos
```bash
# Backup de tablas afectadas
pg_dump -t orders -t order_items -t order_transactions > backup_monetary_tables.sql
```

#### 1.3 Análisis de Datos Actuales
```sql
-- Identificar valores con decimales > 2 dígitos
SELECT id, subtotal, ROUND(CAST(subtotal AS NUMERIC), 2) AS rounded
FROM orders
WHERE subtotal != ROUND(CAST(subtotal AS NUMERIC), 2);
```

### **FASE 2: MIGRATION SCRIPTS (1 día)**

#### 2.1 Crear Migration Alembic
```python
# alembic/versions/2025_10_02_xxxx_float_to_decimal_monetary_fields.py

from alembic import op
import sqlalchemy as sa
from sqlalchemy import DECIMAL

def upgrade():
    # === ORDERS TABLE ===
    op.alter_column('orders', 'subtotal',
                    existing_type=sa.Float(),
                    type_=DECIMAL(12, 2),
                    existing_nullable=False,
                    postgresql_using='CAST(subtotal AS NUMERIC(12,2))')

    op.alter_column('orders', 'tax_amount',
                    existing_type=sa.Float(),
                    type_=DECIMAL(12, 2),
                    existing_nullable=False,
                    postgresql_using='CAST(tax_amount AS NUMERIC(12,2))')

    op.alter_column('orders', 'shipping_cost',
                    existing_type=sa.Float(),
                    type_=DECIMAL(12, 2),
                    existing_nullable=False,
                    postgresql_using='CAST(shipping_cost AS NUMERIC(12,2))')

    op.alter_column('orders', 'discount_amount',
                    existing_type=sa.Float(),
                    type_=DECIMAL(12, 2),
                    existing_nullable=False,
                    postgresql_using='CAST(discount_amount AS NUMERIC(12,2))')

    op.alter_column('orders', 'total_amount',
                    existing_type=sa.Float(),
                    type_=DECIMAL(12, 2),
                    existing_nullable=False,
                    postgresql_using='CAST(total_amount AS NUMERIC(12,2))')

    # === ORDER_ITEMS TABLE ===
    op.alter_column('order_items', 'unit_price',
                    existing_type=sa.Float(),
                    type_=DECIMAL(10, 2),
                    existing_nullable=False,
                    postgresql_using='CAST(unit_price AS NUMERIC(10,2))')

    op.alter_column('order_items', 'total_price',
                    existing_type=sa.Float(),
                    type_=DECIMAL(10, 2),
                    existing_nullable=False,
                    postgresql_using='CAST(total_price AS NUMERIC(10,2))')

    # === ORDER_TRANSACTIONS TABLE ===
    op.alter_column('order_transactions', 'amount',
                    existing_type=sa.Float(),
                    type_=DECIMAL(12, 2),
                    existing_nullable=False,
                    postgresql_using='CAST(amount AS NUMERIC(12,2))')

    # === ADMIN_ACTIVITY_LOG TABLE ===
    op.alter_column('admin_activity_log', 'old_price',
                    existing_type=sa.Float(),
                    type_=DECIMAL(12, 2),
                    existing_nullable=True,
                    postgresql_using='CAST(old_price AS NUMERIC(12,2))')

    op.alter_column('admin_activity_log', 'new_price',
                    existing_type=sa.Float(),
                    type_=DECIMAL(12, 2),
                    existing_nullable=True,
                    postgresql_using='CAST(new_price AS NUMERIC(12,2))')

    op.alter_column('admin_activity_log', 'price_difference',
                    existing_type=sa.Float(),
                    type_=DECIMAL(12, 2),
                    existing_nullable=True,
                    postgresql_using='CAST(price_difference AS NUMERIC(12,2))')

    # === INVENTORY_AUDIT TABLE ===
    op.alter_column('inventory_audit', 'valor_discrepancias',
                    existing_type=sa.Float(),
                    type_=DECIMAL(12, 2),
                    existing_nullable=True,
                    postgresql_using='CAST(valor_discrepancias AS NUMERIC(12,2))')

    op.alter_column('inventory_audit', 'valor_discrepancia',
                    existing_type=sa.Float(),
                    type_=DECIMAL(12, 2),
                    existing_nullable=True,
                    postgresql_using='CAST(valor_discrepancia AS NUMERIC(12,2))')

    # === DISCREPANCY_REPORT TABLE ===
    op.alter_column('discrepancy_report', 'valor_unitario_registrado',
                    existing_type=sa.Float(),
                    type_=DECIMAL(12, 2),
                    existing_nullable=True,
                    postgresql_using='CAST(valor_unitario_registrado AS NUMERIC(12,2))')

    op.alter_column('discrepancy_report', 'valor_unitario_fisico',
                    existing_type=sa.Float(),
                    type_=DECIMAL(12, 2),
                    existing_nullable=True,
                    postgresql_using='CAST(valor_unitario_fisico AS NUMERIC(12,2))')

    op.alter_column('discrepancy_report', 'valor_total_discrepancia',
                    existing_type=sa.Float(),
                    type_=DECIMAL(12, 2),
                    existing_nullable=True,
                    postgresql_using='CAST(valor_total_discrepancia AS NUMERIC(12,2))')


def downgrade():
    # Rollback: DECIMAL → Float (con pérdida de precisión)
    # === ORDERS TABLE ===
    op.alter_column('orders', 'subtotal',
                    existing_type=DECIMAL(12, 2),
                    type_=sa.Float(),
                    existing_nullable=False)

    op.alter_column('orders', 'tax_amount',
                    existing_type=DECIMAL(12, 2),
                    type_=sa.Float(),
                    existing_nullable=False)

    op.alter_column('orders', 'shipping_cost',
                    existing_type=DECIMAL(12, 2),
                    type_=sa.Float(),
                    existing_nullable=False)

    op.alter_column('orders', 'discount_amount',
                    existing_type=DECIMAL(12, 2),
                    type_=sa.Float(),
                    existing_nullable=False)

    op.alter_column('orders', 'total_amount',
                    existing_type=DECIMAL(12, 2),
                    type_=sa.Float(),
                    existing_nullable=False)

    # === ORDER_ITEMS TABLE ===
    op.alter_column('order_items', 'unit_price',
                    existing_type=DECIMAL(10, 2),
                    type_=sa.Float(),
                    existing_nullable=False)

    op.alter_column('order_items', 'total_price',
                    existing_type=DECIMAL(10, 2),
                    type_=sa.Float(),
                    existing_nullable=False)

    # === ORDER_TRANSACTIONS TABLE ===
    op.alter_column('order_transactions', 'amount',
                    existing_type=DECIMAL(12, 2),
                    type_=sa.Float(),
                    existing_nullable=False)

    # === ADMIN_ACTIVITY_LOG TABLE ===
    op.alter_column('admin_activity_log', 'old_price',
                    existing_type=DECIMAL(12, 2),
                    type_=sa.Float(),
                    existing_nullable=True)

    op.alter_column('admin_activity_log', 'new_price',
                    existing_type=DECIMAL(12, 2),
                    type_=sa.Float(),
                    existing_nullable=True)

    op.alter_column('admin_activity_log', 'price_difference',
                    existing_type=DECIMAL(12, 2),
                    type_=sa.Float(),
                    existing_nullable=True)

    # === INVENTORY_AUDIT TABLE ===
    op.alter_column('inventory_audit', 'valor_discrepancias',
                    existing_type=DECIMAL(12, 2),
                    type_=sa.Float(),
                    existing_nullable=True)

    op.alter_column('inventory_audit', 'valor_discrepancia',
                    existing_type=DECIMAL(12, 2),
                    type_=sa.Float(),
                    existing_nullable=True)

    # === DISCREPANCY_REPORT TABLE ===
    op.alter_column('discrepancy_report', 'valor_unitario_registrado',
                    existing_type=DECIMAL(12, 2),
                    type_=sa.Float(),
                    existing_nullable=True)

    op.alter_column('discrepancy_report', 'valor_unitario_fisico',
                    existing_type=DECIMAL(12, 2),
                    type_=sa.Float(),
                    existing_nullable=True)

    op.alter_column('discrepancy_report', 'valor_total_discrepancia',
                    existing_type=DECIMAL(12, 2),
                    type_=sa.Float(),
                    existing_nullable=True)
```

### **FASE 3: ACTUALIZACIÓN DE MODELOS (2-3 horas)**

#### 3.1 Actualizar app/models/order.py
```python
# Cambiar todas las definiciones de Float a DECIMAL
from sqlalchemy import DECIMAL

# Línea 35-39
subtotal = Column(DECIMAL(12, 2), nullable=False, default=0.0)
tax_amount = Column(DECIMAL(12, 2), nullable=False, default=0.0)
shipping_cost = Column(DECIMAL(12, 2), nullable=False, default=0.0)
discount_amount = Column(DECIMAL(12, 2), nullable=False, default=0.0)
total_amount = Column(DECIMAL(12, 2), nullable=False)

# Línea 98, 100
unit_price = Column(DECIMAL(10, 2), nullable=False)
total_price = Column(DECIMAL(10, 2), nullable=False)

# Línea 122
amount = Column(DECIMAL(12, 2), nullable=False)
```

#### 3.2 Actualizar app/models/admin_activity_log.py
```python
# Línea 302, 308, 314
old_price = Column(DECIMAL(12, 2), nullable=True)
new_price = Column(DECIMAL(12, 2), nullable=True)
price_difference = Column(DECIMAL(12, 2), nullable=True)
```

#### 3.3 Actualizar app/models/inventory_audit.py
```python
# Línea 43, 93
valor_discrepancias = Column(DECIMAL(12, 2), default=0.0)
valor_discrepancia = Column(DECIMAL(12, 2), nullable=True)
```

#### 3.4 Actualizar app/models/discrepancy_report.py
```python
# Línea 190, 196, 251
valor_unitario_registrado = Column(DECIMAL(12, 2), nullable=True)
valor_unitario_fisico = Column(DECIMAL(12, 2), nullable=True)
valor_total_discrepancia = Column(DECIMAL(12, 2), nullable=True)
```

### **FASE 4: TESTING EXHAUSTIVO (1-2 días)**

#### 4.1 Tests de Integridad de Datos
```python
# tests/test_float_to_decimal_migration.py

def test_order_total_calculation_precision():
    """Verificar precisión en cálculo de totales"""
    order = Order(
        subtotal=Decimal('150.75'),
        tax_amount=Decimal('28.64'),
        shipping_cost=Decimal('15.50'),
        discount_amount=Decimal('10.00')
    )

    expected_total = Decimal('184.89')
    calculated_total = order.subtotal + order.tax_amount + order.shipping_cost - order.discount_amount

    assert calculated_total == expected_total
    assert str(calculated_total) == '184.89'


def test_commission_calculation_with_decimal():
    """Verificar cálculos de comisión con Decimal"""
    order_amount = Decimal('150000.00')
    commission_rate = Decimal('0.05')

    commission_amount = (order_amount * commission_rate).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )

    assert commission_amount == Decimal('7500.00')
    assert str(commission_amount) == '7500.00'


def test_payment_transaction_precision():
    """Verificar precisión en transacciones de pago"""
    transaction = OrderTransaction(
        amount=Decimal('184.89')
    )

    # No debe haber pérdida de precisión
    assert transaction.amount == Decimal('184.89')
    assert str(transaction.amount) == '184.89'
```

#### 4.2 Tests de Regresión en APIs
```python
# Verificar que APIs existentes funcionen con Decimal
def test_create_order_with_decimal_amounts():
    response = client.post("/api/v1/orders/", json={
        "buyer_id": "test-uuid",
        "subtotal": 150.75,
        "tax_amount": 28.64,
        "shipping_cost": 15.50,
        "discount_amount": 10.00,
        "total_amount": 184.89
    })

    assert response.status_code == 200
    assert response.json()["total_amount"] == "184.89"
```

### **FASE 5: DEPLOYMENT (1 día)**

#### 5.1 Staging Environment
```bash
# 1. Backup de staging
pg_dump staging_db > staging_backup_pre_migration.sql

# 2. Aplicar migration
alembic upgrade head

# 3. Verificar datos
python scripts/verify_decimal_conversion.py

# 4. Smoke tests
pytest tests/test_float_to_decimal_migration.py -v
```

#### 5.2 Production Deployment
```bash
# VENTANA DE MANTENIMIENTO REQUERIDA: 1-2 horas

# 1. Backup completo de producción
pg_dump production_db > production_backup_$(date +%Y%m%d).sql

# 2. Modo maintenance
# Activar página de mantenimiento

# 3. Aplicar migration
alembic upgrade head

# 4. Verificación post-migration
python scripts/verify_decimal_conversion.py --env production

# 5. Smoke tests en producción
pytest tests/critical_decimal_tests.py -v

# 6. Monitoreo de logs
tail -f /var/log/mestore/api.log | grep -i "decimal\|precision"

# 7. Desactivar modo maintenance
```

---

## ⚙️ CÓDIGO ADICIONAL REQUERIDO

### 1. **Script de Validación Pre-Migration**
```python
# scripts/validate_float_data_integrity.py

import asyncio
from decimal import Decimal
from sqlalchemy import select, func
from app.database import AsyncSessionLocal
from app.models.order import Order, OrderItem, OrderTransaction

async def validate_float_precision():
    async with AsyncSessionLocal() as db:
        # Verificar valores con más de 2 decimales
        result = await db.execute(
            select(Order.id, Order.total_amount)
            .where(
                func.round(Order.total_amount, 2) != Order.total_amount
            )
        )

        problematic_orders = result.all()

        if problematic_orders:
            print(f"⚠️  Encontradas {len(problematic_orders)} órdenes con precisión > 2 decimales")
            for order_id, amount in problematic_orders:
                print(f"  - Order {order_id}: {amount}")
        else:
            print("✅ Todos los valores tienen precisión <= 2 decimales")

if __name__ == "__main__":
    asyncio.run(validate_float_precision())
```

### 2. **Script de Verificación Post-Migration**
```python
# scripts/verify_decimal_conversion.py

import asyncio
from sqlalchemy import inspect
from app.database import AsyncSessionLocal, engine

async def verify_decimal_types():
    async with engine.begin() as conn:
        inspector = inspect(conn)

        # Verificar tipos de columnas
        tables_to_check = {
            'orders': ['subtotal', 'tax_amount', 'shipping_cost', 'discount_amount', 'total_amount'],
            'order_items': ['unit_price', 'total_price'],
            'order_transactions': ['amount'],
            'admin_activity_log': ['old_price', 'new_price', 'price_difference'],
            'inventory_audit': ['valor_discrepancias', 'valor_discrepancia'],
            'discrepancy_report': ['valor_unitario_registrado', 'valor_unitario_fisico', 'valor_total_discrepancia']
        }

        errors = []

        for table_name, columns in tables_to_check.items():
            table_columns = inspector.get_columns(table_name)

            for column in columns:
                col_info = next((c for c in table_columns if c['name'] == column), None)

                if col_info:
                    col_type = str(col_info['type'])
                    if 'NUMERIC' not in col_type and 'DECIMAL' not in col_type:
                        errors.append(f"❌ {table_name}.{column}: Expected DECIMAL, got {col_type}")
                    else:
                        print(f"✅ {table_name}.{column}: {col_type}")

        if errors:
            print("\n🚨 ERRORES ENCONTRADOS:")
            for error in errors:
                print(f"  {error}")
            return False
        else:
            print("\n✅ TODAS LAS COLUMNAS MIGRARON CORRECTAMENTE A DECIMAL")
            return True

if __name__ == "__main__":
    success = asyncio.run(verify_decimal_types())
    exit(0 if success else 1)
```

---

## 🎯 PLAN DE TESTING DETALLADO

### Test Suite 1: Precision Tests
```python
# tests/test_decimal_precision.py

class TestDecimalPrecision:
    def test_order_calculations_no_precision_loss(self):
        """Verificar que cálculos de orden no pierdan precisión"""
        subtotal = Decimal('1234.56')
        tax = Decimal('98.76')
        shipping = Decimal('15.00')
        discount = Decimal('50.00')

        total = subtotal + tax + shipping - discount
        assert total == Decimal('1298.32')

    def test_commission_rounding_consistent(self):
        """Verificar redondeo consistente en comisiones"""
        amount = Decimal('150000.00')
        rate = Decimal('0.05')

        commission = (amount * rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        assert commission == Decimal('7500.00')

    def test_bulk_calculation_precision(self):
        """Verificar precisión en cálculos masivos"""
        items = [
            {'price': Decimal('10.99'), 'qty': 3},
            {'price': Decimal('25.50'), 'qty': 2},
            {'price': Decimal('5.75'), 'qty': 5}
        ]

        total = sum(
            (item['price'] * item['qty']).quantize(Decimal('0.01'))
            for item in items
        )

        expected = Decimal('111.72')  # 32.97 + 51.00 + 28.75
        assert total == expected
```

### Test Suite 2: API Integration Tests
```python
# tests/test_order_api_decimal.py

class TestOrderAPIWithDecimal:
    def test_create_order_preserves_precision(self, client):
        """Verificar que API preserve precisión en creación"""
        order_data = {
            "subtotal": "150.75",
            "tax_amount": "28.64",
            "shipping_cost": "15.50",
            "discount_amount": "10.00"
        }

        response = client.post("/api/v1/orders/", json=order_data)
        assert response.status_code == 201

        # Verificar precisión exacta
        data = response.json()
        assert data["subtotal"] == "150.75"
        assert data["tax_amount"] == "28.64"

    def test_payment_transaction_decimal_accuracy(self, client):
        """Verificar precisión en transacciones de pago"""
        payment_data = {
            "amount": "184.89",
            "currency": "COP"
        }

        response = client.post("/api/v1/payments/", json=payment_data)
        data = response.json()

        # No debe haber redondeo
        assert data["amount"] == "184.89"
```

### Test Suite 3: Database Migration Tests
```python
# tests/test_migration_float_to_decimal.py

class TestFloatToDecimalMigration:
    def test_migration_preserves_data(self, db):
        """Verificar que migration preserve datos existentes"""
        # Setup: Crear orden con Float
        order = Order(
            total_amount=184.89,
            subtotal=150.75
        )
        db.add(order)
        db.commit()

        # Aplicar migration (simulado)
        # ...

        # Verificar que datos se mantengan
        db.refresh(order)
        assert str(order.total_amount) == "184.89"
        assert str(order.subtotal) == "150.75"

    def test_rollback_migration_safe(self, db):
        """Verificar que rollback sea seguro"""
        # Test de downgrade migration
        # ...
```

---

## 📈 MÉTRICAS DE ÉXITO

### KPIs Post-Migración
1. **Precisión Financiera**: 100% de cálculos con precisión de 2 decimales
2. **Integridad de Datos**: 0 registros con valores incorrectos
3. **Performance**: No degradación > 5% en queries de órdenes
4. **Cobertura de Tests**: >90% en cálculos financieros

### Monitoreo Post-Deployment
```sql
-- Query de monitoreo diario
SELECT
    COUNT(*) as total_orders,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_order_value,
    MIN(total_amount) as min_order,
    MAX(total_amount) as max_order
FROM orders
WHERE created_at >= CURRENT_DATE
AND total_amount = ROUND(total_amount::numeric, 2);
```

---

## ⚠️ RIESGOS Y MITIGACIÓN

### Riesgo 1: Pérdida de Datos Durante Migración
**Probabilidad**: BAJA
**Impacto**: CRÍTICO
**Mitigación**:
- Backups completos antes de migration
- Testing exhaustivo en staging
- Rollback plan documentado

### Riesgo 2: Performance Degradation
**Probabilidad**: MEDIA
**Impacto**: MEDIO
**Mitigación**:
- Índices optimizados para columnas DECIMAL
- Monitoreo de query performance
- Cache warming post-migration

### Riesgo 3: Incompatibilidad con APIs Legacy
**Probabilidad**: BAJA
**Impacto**: ALTO
**Mitigación**:
- Mantener serialización compatible con Float en JSON
- Documentar cambios en API changelog
- Versionamiento de API si necesario

---

## 📝 CHECKLIST DE IMPLEMENTACIÓN

### Pre-Migración
- [ ] Backup completo de base de datos producción
- [ ] Backup completo de base de datos staging
- [ ] Validación de datos con precisión > 2 decimales
- [ ] Revisión de code review por database-architect-ai
- [ ] Aprobación de master-orchestrator

### Migración
- [ ] Crear migration script Alembic
- [ ] Actualizar modelos SQLAlchemy (6 archivos)
- [ ] Ejecutar migration en staging
- [ ] Verificar tipos de datos post-migration
- [ ] Run full test suite

### Testing
- [ ] Tests unitarios de precisión (>10 tests)
- [ ] Tests de integración API (>5 tests)
- [ ] Tests de performance (benchmarks)
- [ ] Tests de regresión completos

### Deployment
- [ ] Aplicar migration en producción
- [ ] Verificar tipos de columnas
- [ ] Ejecutar smoke tests críticos
- [ ] Monitoreo de logs por 48 horas
- [ ] Validación de reportes financieros

### Post-Deployment
- [ ] Actualizar documentación de base de datos
- [ ] Comunicar cambios a equipo de desarrollo
- [ ] Actualizar guías de desarrollo
- [ ] Archivar scripts de migration

---

## 📞 AGENTES RESPONSABLES

### Aprobación Requerida
- **database-architect-ai**: Diseño de schema y migration
- **system-architect-ai**: Impacto en arquitectura general
- **security-backend-ai**: Validación de integridad financiera
- **tdd-specialist**: Estrategia de testing
- **master-orchestrator**: Aprobación final

### Consulta Opcional
- **backend-framework-ai**: Actualización de servicios
- **api-architect-ai**: Impacto en APIs

---

## 🚀 PRÓXIMOS PASOS RECOMENDADOS

1. **INMEDIATO**: Obtener aprobación de agentes responsables
2. **DÍA 1**: Crear migration script y actualizar modelos
3. **DÍA 2**: Testing exhaustivo en staging
4. **DÍA 3**: Deployment en producción (ventana de mantenimiento)
5. **DÍA 4-5**: Monitoreo intensivo y validación

---

## 📚 REFERENCIAS

- **SQLAlchemy DECIMAL Documentation**: https://docs.sqlalchemy.org/en/14/core/type_basics.html#sqlalchemy.types.DECIMAL
- **Python Decimal Module**: https://docs.python.org/3/library/decimal.html
- **PostgreSQL NUMERIC Type**: https://www.postgresql.org/docs/current/datatype-numeric.html
- **Financial Calculations Best Practices**: IEEE 754 floating-point vs fixed-point arithmetic

---

**Documento generado por**: database-performance-ai
**Fecha**: 2025-10-02
**Versión**: 1.0
**Estado**: PENDIENTE APROBACIÓN
