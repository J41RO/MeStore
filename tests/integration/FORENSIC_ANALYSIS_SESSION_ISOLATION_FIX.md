# 🔬 ANÁLISIS FORENSE: Problema de Aislamiento de Sesión en Tests de Webhook
## Reporte del Integration Testing Specialist

**Fecha:** 2025-10-18
**Test Afectado:** `tests/integration/test_webhooks_wompi.py::test_approved_payment_updates_order`
**Síntoma:** ✅ PASA individualmente | ❌ FALLA en suite completa
**Error:** `assert <OrderStatus.PENDING: 'pending'> == <OrderStatus.CONFIRMED: 'confirmed'>`

---

## 🎯 DIAGNÓSTICO FORENSE

### **HALLAZGO CRÍTICO: Problema de Sincronización de Sesiones Async**

El test utiliza **DOS SESIONES SEPARADAS** que operan de forma independiente:

1. **Sesión del TEST** (`async_session`) - Crea orden, ejecuta queries de validación
2. **Sesión del WEBHOOK** (creada por `get_async_db`) - Procesa webhook, actualiza orden en BD

**PROBLEMA:** Estas sesiones NO comparten automáticamente los commits entre sí en SQLAlchemy async.

### **POR QUÉ FALLABA EN SUITE PERO PASABA INDIVIDUALMENTE**

#### Ejecución Individual (PASA ✅):
```
1. Base de datos vacía/limpia
2. Test crea orden PENDING (session.commit())
3. Webhook actualiza orden a CONFIRMED (session.commit() en sesión separada)
4. Test hace session.commit() → ve cambios (por suerte)
5. Re-query → orden CONFIRMED ✅
```

#### Ejecución en Suite (FALLA ❌):
```
1. Tests anteriores dejan estado residual en sesiones
2. Test crea orden PENDING
3. Webhook actualiza orden a CONFIRMED (en su PROPIA sesión)
4. Test hace session.commit() → pero la sesión tiene CACHE VIEJO
5. Re-query → orden sigue PENDING ❌ (lee desde identity map cached)
```

---

## 🔍 EVIDENCIA DEL CÓDIGO

### **Fixture Original (PROBLEMÁTICO)**
```python
@pytest.fixture
async def test_order(async_session: AsyncSession):
    # ... crear buyer ...
    async_session.add(buyer)
    await async_session.commit()  # ⚠️ Commit simple

    # ... crear orden ...
    async_session.add(order)
    await async_session.commit()  # ⚠️ Commit simple
    await async_session.refresh(order)
    return order  # ⚠️ Objeto attached a sesión que puede tener cache viejo
```

**PROBLEMA:**
- No limpia transacciones pendientes de tests anteriores
- No garantiza que la sesión esté en estado limpio
- El objeto retornado está "attached" a una sesión que puede tener estado residual

### **Test Original (PROBLEMÁTICO)**
```python
async def test_approved_payment_updates_order(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_order: Order,
    valid_webhook_payload: dict
):
    valid_webhook_payload["data"]["reference"] = test_order.order_number

    with patch("app.core.config.settings.WOMPI_WEBHOOK_SECRET", ""):
        response = await async_client.post(
            "/api/v1/webhooks/wompi",
            json=valid_webhook_payload
        )

    assert response.status_code == 200

    # ⚠️ PROBLEMA: Solo hace commit, NO expira cache
    await async_session.commit()

    # ⚠️ PROBLEMA: Re-query puede leer desde identity map cached
    result = await async_session.execute(
        select(Order).where(Order.id == test_order.id)
    )
    updated_order = result.scalar_one()

    assert updated_order.status == OrderStatus.CONFIRMED  # ❌ FALLA
```

**PROBLEMA:**
- `session.commit()` NO expira objetos cached
- SQLAlchemy mantiene "identity map" con objetos en memoria
- La re-query puede retornar objeto cached en lugar de fresh query

---

## ✅ SOLUCIÓN IMPLEMENTADA: Session Synchronization Fix

### **Fix #1: Fixture `test_order` - Session Cleanup**
```python
@pytest.fixture
async def test_order(async_session: AsyncSession):
    """Create a test order for webhook testing."""
    from app.models.user import User, UserType
    from app.core.types import generate_uuid

    # CRITICAL FIX: Ensure session is completely clean before creating test data
    # This prevents contamination from previous tests in the suite
    if async_session.in_transaction():
        await async_session.rollback()  # 🔧 Limpia transacciones pendientes

    # Explicitly begin a new transaction for test data creation
    await async_session.begin()  # 🔧 Nueva transacción limpia

    # Create test buyer with unique email
    unique_id = generate_uuid()[:8]
    buyer = User(
        id=f"test-buyer-webhook-{unique_id}",
        email=f"buyer-webhook-{unique_id}@test.com",
        password_hash="fake_hash",
        nombre="Test",
        apellido="Buyer",
        user_type=UserType.BUYER,
        is_active=True
    )
    async_session.add(buyer)
    await async_session.flush()  # 🔧 Flush en lugar de commit (mantiene transacción)

    # Create order with unique order number
    order = Order(
        order_number=f"TEST-ORDER-{unique_id}",
        buyer_id=buyer.id,
        total_amount=50000.0,
        subtotal=50000.0,
        tax_amount=0.0,
        shipping_cost=0.0,
        discount_amount=0.0,
        status=OrderStatus.PENDING,
        shipping_name="Test Customer",
        shipping_phone="+57 300 123 4567",
        shipping_email="customer@test.com",
        shipping_address="Calle 123 #45-67",
        shipping_city="Bogotá",
        shipping_state="Cundinamarca",
        shipping_country="CO"
    )
    async_session.add(order)
    await async_session.flush()  # 🔧 Flush para asignar IDs sin commit

    # NOW commit to database so webhook can see it
    await async_session.commit()  # 🔧 Commit final para persistencia

    # Refresh to ensure we have latest state
    await async_session.refresh(order)  # 🔧 Refresh para estado actualizado

    return order
```

**MEJORAS:**
1. ✅ Limpia transacciones pendientes antes de crear datos
2. ✅ Usa `begin()` explícito para nueva transacción limpia
3. ✅ Usa `flush()` en lugar de `commit()` para mantener transacción abierta
4. ✅ Commit final garantiza que webhook puede ver datos

### **Fix #2: Test `test_approved_payment_updates_order` - Cache Expiration**
```python
@pytest.mark.asyncio
async def test_approved_payment_updates_order(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_order: Order,
    valid_webhook_payload: dict
):
    """Test that APPROVED status updates order to confirmed."""
    valid_webhook_payload["data"]["reference"] = test_order.order_number

    # CRITICAL: Save order ID BEFORE any session operations
    # After expire_all(), the test_order object becomes detached and cannot access attributes
    order_id = test_order.id  # 🔧 Guardar ID antes de expire

    # Skip signature verification for test
    with patch("app.core.config.settings.WOMPI_WEBHOOK_SECRET", ""):
        response = await async_client.post(
            "/api/v1/webhooks/wompi",
            json=valid_webhook_payload
        )

    assert response.status_code == 200

    # CRITICAL SESSION SYNCHRONIZATION FIX:
    # The webhook endpoint commits in its own separate session.
    # To see those changes, we must:
    # 1. Expire ALL cached objects to force fresh database queries
    async_session.expire_all()  # 🔧 Expira TODOS los objetos cached

    # 2. Commit any pending transaction state (even if empty)
    # This ensures we're reading from the latest committed database state
    if async_session.in_transaction():
        await async_session.commit()  # 🔧 Commit para sincronización

    # 3. Re-fetch order with a fresh query to get latest committed state from database
    # Use the order_id we saved BEFORE expire_all()
    result = await async_session.execute(
        select(Order).where(Order.id == order_id)  # 🔧 Usar ID guardado
    )
    updated_order = result.scalar_one()

    assert updated_order.status == OrderStatus.CONFIRMED  # ✅ PASA
    assert updated_order.confirmed_at is not None  # ✅ PASA
```

**MEJORAS:**
1. ✅ Guarda `order_id` ANTES de `expire_all()` (objeto se vuelve detached)
2. ✅ Llama `expire_all()` para forzar fresh queries (invalida identity map)
3. ✅ Hace `commit()` para sincronizar con commits de webhook
4. ✅ Re-query usa ID guardado (objeto detached ya no tiene atributos accesibles)

---

## 🧪 VALIDACIÓN DEL FIX

### **Test Individual**
```bash
$ pytest tests/integration/test_webhooks_wompi.py::test_approved_payment_updates_order -xvs
```
**Resultado:** ✅ **PASSED** (0.28s)

### **Suite Completa**
```bash
$ pytest tests/integration/test_webhooks_wompi.py -x
```
**Resultado:** ✅ **18 passed** (16.86s)

### **Ejecución Múltiple (Verificación de Estabilidad)**
```bash
$ for i in {1..3}; do pytest tests/integration/test_webhooks_wompi.py -x; done
```
**Resultado:** ✅ **18 passed** en cada ejecución (sin flakiness)

---

## 📚 LECCIONES APRENDIDAS

### **Principios de Session Management en Async SQLAlchemy**

1. **Identity Map**: SQLAlchemy mantiene cache de objetos en sesión
   - `session.execute(select(...))` puede retornar objeto cached
   - Solución: `session.expire_all()` invalida cache

2. **Session Isolation**: Cada sesión es independiente
   - Webhook usa su propia sesión (`get_async_db`)
   - Test usa su propia sesión (`async_session`)
   - NO comparten commits automáticamente

3. **Object State Management**:
   - **Transient**: Objeto nuevo, no en sesión
   - **Pending**: En sesión, no committeado
   - **Persistent**: Committeado, attached a sesión
   - **Detached**: Committeado, NO attached (después de `expire_all()`)

4. **Best Practices para Integration Tests**:
   ```python
   # ✅ CORRECTO: Expira cache antes de re-query
   session.expire_all()
   await session.commit()
   result = await session.execute(select(Model).where(...))

   # ❌ INCORRECTO: Re-query sin expirar cache
   await session.commit()
   result = await session.execute(select(Model).where(...))  # Puede retornar cached
   ```

### **Patrones de Testing con Múltiples Sesiones**

Cuando un test involucra **múltiples sesiones async** (test + endpoint):

1. ✅ **Guardar IDs** antes de `expire_all()`
2. ✅ **Llamar `expire_all()`** antes de re-query
3. ✅ **Commit explícito** para sincronización
4. ✅ **Usar IDs guardados** para re-query (objetos detached)
5. ✅ **Limpiar transacciones** en fixtures antes de crear datos

---

## 🎯 CONCLUSIÓN

**RAÍZ DEL PROBLEMA:** Falta de sincronización entre sesiones async independientes + cache de identity map de SQLAlchemy.

**SOLUCIÓN:** Session synchronization con `expire_all()` + commit + fresh query usando IDs guardados.

**IMPACTO:**
- ✅ Test pasa consistentemente en ejecución individual
- ✅ Test pasa consistentemente en suite completa
- ✅ No hay flakiness (verificado con múltiples ejecuciones)
- ✅ Solución quirúrgica (NO modifica lógica de negocio)
- ✅ Solución mínima e invasiva (solo fixtures + cleanup)

**ARCHIVOS MODIFICADOS:**
- `/home/admin-jairo/MeStore/tests/integration/test_webhooks_wompi.py`
  - Fixture `test_order` (líneas 30-85)
  - Test `test_approved_payment_updates_order` (líneas 256-298)

**TIPO DE FIX:** Infrastructure (testing) - NO business logic

---

## 📋 RECOMENDACIONES

### **Para Futuros Tests de Webhooks**

Usar este patrón en TODOS los tests que involucren webhooks:

```python
@pytest.mark.asyncio
async def test_webhook_updates_model(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_model: Model,
    webhook_payload: dict
):
    # 1. Guardar IDs ANTES de operaciones de sesión
    model_id = test_model.id

    # 2. Ejecutar webhook
    response = await async_client.post("/webhook", json=webhook_payload)
    assert response.status_code == 200

    # 3. Sincronización de sesión (CRITICAL)
    async_session.expire_all()
    if async_session.in_transaction():
        await async_session.commit()

    # 4. Re-query usando IDs guardados
    result = await async_session.execute(
        select(Model).where(Model.id == model_id)
    )
    updated_model = result.scalar_one()

    # 5. Asserts con objeto fresh
    assert updated_model.status == ExpectedStatus
```

### **Para Fixtures de Datos de Test**

Siempre limpiar sesión antes de crear datos:

```python
@pytest.fixture
async def test_data(async_session: AsyncSession):
    # Limpiar transacciones pendientes
    if async_session.in_transaction():
        await async_session.rollback()

    # Nueva transacción limpia
    await async_session.begin()

    # Crear datos con flush
    data = Model(...)
    async_session.add(data)
    await async_session.flush()

    # Commit final
    await async_session.commit()
    await async_session.refresh(data)

    return data
```

---

**Firma Digital:** Integration Testing Specialist
**Timestamp:** 2025-10-18T19:40:00Z
**Status:** ✅ RESUELTO - VERIFICADO - DOCUMENTADO
