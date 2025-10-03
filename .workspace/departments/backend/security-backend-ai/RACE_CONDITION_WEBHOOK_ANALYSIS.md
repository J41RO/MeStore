# 🔴 BUG CRÍTICO #3: RACE CONDITION EN WEBHOOKS DE PAGOS
## Análisis Técnico de Seguridad

**Fecha**: 2025-10-02
**Analista**: SecurityBackendAI
**Severidad**: 🔴 CRÍTICA
**Impacto**: Alto - Potencial duplicación de pagos, pérdida financiera
**Probabilidad**: Media - Ocurre bajo carga concurrente

---

## 📋 EXECUTIVE SUMMARY

Se ha identificado una **race condition crítica** en el sistema de webhooks de pagos que puede causar:

1. **Procesamiento duplicado de pagos** - Múltiples confirmaciones de una misma transacción
2. **Inconsistencia de estados** - Órdenes en estados contradictorios
3. **Pérdida de datos** - Sobrescritura de información de transacciones
4. **Riesgo financiero** - Posible doble despacho de productos

**Archivos afectados**:
- `/home/admin-jairo/MeStore/app/api/v1/endpoints/webhooks.py` (815 líneas)
- `/home/admin-jairo/MeStore/app/services/payments/payu_service.py` (692 líneas)
- `/home/admin-jairo/MeStore/app/services/payments/efecty_service.py` (543 líneas)
- `/home/admin-jairo/MeStore/app/models/order.py` (192 líneas)
- `/home/admin-jairo/MeStore/app/models/payment.py` (190 líneas)

---

## 🔍 ANÁLISIS DETALLADO

### 1. PUNTO CRÍTICO: FUNCIÓN `update_order_from_webhook()` (Líneas 174-301)

#### 🚨 Problema Identificado:

```python
# CÓDIGO ACTUAL - VULNERABILIDAD RACE CONDITION
async def update_order_from_webhook(
    db: AsyncSession,
    transaction_data: Dict[str, Any],
    wompi_transaction_id: str
) -> WebhookProcessingResult:
    try:
        # 1. ❌ NO HAY LOCK - Consulta sin protección concurrente
        result = await db.execute(
            select(Order)
            .where(Order.order_number == order_reference)
            .options(selectinload(Order.transactions))
        )
        order = result.scalar_one_or_none()

        # 2. ❌ WINDOW DE RACE CONDITION AQUÍ
        # Si llegan 2 webhooks simultáneos del mismo pago:
        # - Ambos leen el mismo estado inicial
        # - Ambos crean transacciones separadas
        # - Ambos actualizan la orden (último gana)

        # 3. ❌ NO HAY VALIDACIÓN DE ESTADO PREVIO
        for txn in order.transactions:
            if txn.gateway_transaction_id == wompi_transaction_id:
                transaction = txn
                break

        if not transaction:
            # ❌ VULNERABILIDAD: Puede crear duplicado si ya existe pero no fue leído
            transaction = OrderTransaction(...)
            db.add(transaction)

        # 4. ❌ ACTUALIZACIÓN SIN LOCK
        order.status = order_status
        order.updated_at = datetime.utcnow()

        # 5. Commit sin verificación de conflictos
        await db.commit()
```

#### 💥 Escenario de Ataque:

```
T0: Payment gateway (Wompi/PayU) confirma pago #12345
T1: Webhook #1 llega al servidor → Process A inicia
T2: Webhook #2 llega al servidor (retry) → Process B inicia
T3: Process A lee order status = PENDING
T4: Process B lee order status = PENDING (mismo estado!)
T5: Process A crea Transaction #1
T6: Process B crea Transaction #2 (DUPLICADO!)
T7: Process A actualiza order → CONFIRMED
T8: Process B actualiza order → CONFIRMED (sobrescribe cambios de A)
T9: Base de datos tiene 2 transacciones del mismo pago
```

### 2. IDEMPOTENCY CHECK - IMPLEMENTACIÓN DÉBIL

#### 📍 Líneas 111-136 - `check_event_already_processed()`

```python
async def check_event_already_processed(
    db: AsyncSession,
    event_id: str
) -> bool:
    """Check if webhook event has already been processed (idempotency)."""
    try:
        result = await db.execute(
            select(WebhookEvent).where(WebhookEvent.event_id == event_id)
        )
        existing_event = result.scalar_one_or_none()
        return existing_event is not None  # ✅ CORRECTO pero...
    except Exception as e:
        logger.error(f"Error checking event idempotency: {str(e)}")
        return False  # ❌ ERROR: Retorna False en error = permite duplicados
```

#### 🚨 Problemas:

1. **No es atómico**: Entre el check y el insert hay un gap temporal
2. **Falla insegura**: Si Redis/DB falla, permite procesar duplicados
3. **No usa eventos de DB**: La inserción de WebhookEvent es DESPUÉS del procesamiento

**Flujo actual vulnerable**:
```
1. Check si event_id existe → FALSE (no existe aún)
2. Procesar webhook → Actualiza orden
3. Guardar WebhookEvent → Marca como procesado

🚨 Si llegan 2 requests entre paso 1 y 3:
   - Ambos pasan el check
   - Ambos procesan
   - Ambos crean registros
```

### 3. AUSENCIA DE DATABASE LOCKS

#### 🔍 Búsqueda de locks realizada:

```bash
grep -r "for_update|with_for_update|LOCK|SELECT.*FOR UPDATE" app/
# RESULTADO: 0 coincidencias en archivos de pago
```

**Conclusión**: ❌ **NO hay ningún tipo de locking pesimista en el código**

### 4. VALIDACIÓN DE TRANSICIONES DE ESTADO

#### 📍 Línea 230 - Mapeo de estados sin validación:

```python
# Map Wompi status to internal statuses
order_status, payment_status = map_wompi_status_to_order_status(wompi_status)

# ❌ NO HAY VALIDACIÓN DE TRANSICIÓN VÁLIDA
# Ejemplo de transición inválida permitida:
# CONFIRMED → PENDING (si llega webhook tardío de PENDING)
```

**Estado esperado vs permitido**:
```
✅ ESPERADO:
PENDING → CONFIRMED → SHIPPED → DELIVERED

❌ ACTUALMENTE PERMITIDO:
CONFIRMED → PENDING (webhook retrasado)
SHIPPED → CANCELLED (webhook fuera de orden)
DELIVERED → PENDING (reintento antiguo)
```

### 5. ANÁLISIS DE PAYU/EFECTY WEBHOOKS

#### PayU Webhook (líneas 599-712):

```python
async def update_order_from_payu_webhook(
    db: AsyncSession,
    payload_dict: Dict[str, Any]
) -> WebhookProcessingResult:
    # ❌ MISMOS PROBLEMAS QUE WOMPI:
    # 1. No lock en consulta
    # 2. No validación de transición
    # 3. Puede crear transacciones duplicadas
```

#### Efecty Service (archivo separado):

```python
# Efecty es diferente: genera códigos de pago manual
# ⚠️ RIESGO DIFERENTE: Confirmación manual puede duplicarse
def generate_payment_confirmation_data(...):
    # No hay protección contra doble confirmación
    # Admin puede confirmar el mismo código 2 veces
```

---

## 🔥 IMPACTO DE SEGURIDAD

### Riesgos Financieros:

1. **Duplicación de comisiones**:
   - Vendor recibe comisión 2 veces por mismo pago
   - MeStore pierde margen de ganancia

2. **Doble despacho de productos**:
   - Sistema cree que pago fue confirmado 2 veces
   - Envía producto duplicado

3. **Fraude por timing attack**:
   - Atacante envía webhooks simultáneos
   - Explota race condition para duplicar beneficios

### Riesgos Operacionales:

1. **Inconsistencia en reportes**:
   - Dashboard muestra montos incorrectos
   - Reconciliación bancaria falla

2. **Pérdida de auditoría**:
   - No se puede determinar qué transacción es válida
   - Problemas legales con contabilidad

3. **Problemas de soporte**:
   - Clientes ven estados contradictorios
   - Difícil debugging de problemas

### Riesgos de Compliance:

1. **PCI DSS**: Violación de integridad de transacciones
2. **SOX**: Controles financieros inadecuados
3. **GDPR**: Integridad de datos de pago comprometida

---

## 🛡️ PROPUESTA DE SOLUCIÓN

### FASE 1: IMPLEMENTACIÓN DE LOCKS OPTIMISTAS (Prioridad Alta)

#### Solución con PostgreSQL Row-Level Locking:

```python
# NUEVO CÓDIGO SEGURO CON LOCKS
async def update_order_from_webhook(
    db: AsyncSession,
    transaction_data: Dict[str, Any],
    wompi_transaction_id: str
) -> WebhookProcessingResult:
    try:
        # 1. ✅ ADQUIRIR LOCK PESIMISTA EN LA ORDEN
        result = await db.execute(
            select(Order)
            .where(Order.order_number == order_reference)
            .options(selectinload(Order.transactions))
            .with_for_update()  # 🔒 LOCK ROW HASTA COMMIT
        )
        order = result.scalar_one_or_none()

        if not order:
            return WebhookProcessingResult(success=False, ...)

        # 2. ✅ VALIDAR TRANSICIÓN DE ESTADO
        order_status, payment_status = map_wompi_status_to_order_status(wompi_status)

        if not is_valid_state_transition(order.status, order_status):
            logger.warning(
                f"Invalid state transition blocked: {order.status} → {order_status}"
            )
            return WebhookProcessingResult(
                success=False,
                status="invalid_state_transition",
                message=f"Cannot transition from {order.status} to {order_status}"
            )

        # 3. ✅ BUSCAR TRANSACCIÓN EXISTENTE CON LOCK
        transaction = await db.execute(
            select(OrderTransaction)
            .where(
                OrderTransaction.order_id == order.id,
                OrderTransaction.gateway_transaction_id == wompi_transaction_id
            )
            .with_for_update()
        ).scalar_one_or_none()

        if transaction:
            # ✅ Actualizar existente solo si estado cambió
            if transaction.status != payment_status:
                transaction.status = payment_status
                transaction.gateway_response = json.dumps(transaction_data)
                transaction.processed_at = datetime.utcnow()
                logger.info(f"Updated existing transaction {transaction.id}")
            else:
                logger.info(f"Transaction {transaction.id} already in correct state")
                return WebhookProcessingResult(
                    success=True,
                    status="already_processed",
                    message="Transaction already in target state"
                )
        else:
            # ✅ Crear nueva transacción
            transaction = OrderTransaction(
                transaction_reference=f"TXN-{order.order_number}-{wompi_transaction_id[:10]}",
                order_id=order.id,
                amount=amount_in_cents / 100.0 if amount_in_cents else order.total_amount,
                currency="COP",
                status=payment_status,
                payment_method_type=payment_method_type or "unknown",
                gateway="wompi",
                gateway_transaction_id=wompi_transaction_id,
                gateway_response=json.dumps(transaction_data),
                processed_at=datetime.utcnow()
            )
            db.add(transaction)
            logger.info(f"Created new transaction for order {order.id}")

        # 4. ✅ Actualizar estado de orden con validación
        old_status = order.status
        order.status = order_status
        order.updated_at = datetime.utcnow()

        if payment_status == PaymentStatus.APPROVED and not order.confirmed_at:
            order.confirmed_at = datetime.utcnow()
            logger.info(f"Order {order.id} confirmed at {order.confirmed_at}")

        # 5. ✅ Commit atómico - Lock se libera aquí
        await db.commit()
        await db.refresh(order)

        logger.info(
            f"Order {order.id} updated: {old_status} → {order_status}, "
            f"Payment: {payment_status}, Wompi TXN: {wompi_transaction_id}"
        )

        return WebhookProcessingResult(
            success=True,
            event_id=wompi_transaction_id,
            order_id=order.id,
            transaction_id=wompi_transaction_id,
            status="processed",
            message="Order updated successfully",
            updated_order_status=order_status.value
        )

    except IntegrityError as e:
        await db.rollback()
        logger.error(f"Integrity error (possible duplicate): {str(e)}")
        return WebhookProcessingResult(
            success=False,
            status="duplicate_transaction",
            message="Transaction already exists"
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating order from webhook: {str(e)}", exc_info=True)
        return WebhookProcessingResult(
            success=False,
            event_id=wompi_transaction_id,
            status="error",
            message=f"Database error: {str(e)}"
        )
```

### FASE 2: IDEMPOTENCY KEY ATÓMICO

```python
# NUEVO MÉTODO: Idempotency check con inserción atómica
async def ensure_webhook_idempotency(
    db: AsyncSession,
    event_id: str,
    event_type: str,
    raw_payload: Dict[str, Any]
) -> Tuple[bool, Optional[WebhookEvent]]:
    """
    Ensure webhook is processed only once using atomic insert.

    Returns:
        Tuple[bool, Optional[WebhookEvent]]:
            (is_duplicate, existing_event_if_duplicate)
    """
    try:
        # Intentar crear evento PRIMERO (idempotency key)
        webhook_event = WebhookEvent(
            event_id=event_id,  # UNIQUE constraint en DB
            event_type=WebhookEventType.TRANSACTION_UPDATED,
            event_status=WebhookEventStatus.PROCESSING,
            raw_payload=raw_payload,
            created_at=datetime.utcnow()
        )

        db.add(webhook_event)

        try:
            # ✅ Commit intentará insertar
            # Si event_id ya existe, lanzará IntegrityError
            await db.flush()  # Flush sin commit completo

            # ✅ Éxito: Primera vez procesando este evento
            return False, None

        except IntegrityError:
            # ✅ Duplicate detectado por constraint de DB
            await db.rollback()

            # Obtener evento existente
            result = await db.execute(
                select(WebhookEvent).where(WebhookEvent.event_id == event_id)
            )
            existing = result.scalar_one()

            logger.info(
                f"Webhook {event_id} already processed at {existing.created_at}"
            )

            return True, existing

    except Exception as e:
        await db.rollback()
        logger.error(f"Error in idempotency check: {str(e)}")
        # ✅ Fail-secure: Asumir duplicado si hay error
        raise
```

### FASE 3: MÁQUINA DE ESTADOS VÁLIDOS

```python
# NUEVO ARCHIVO: app/models/order_state_machine.py

from enum import Enum
from typing import Set, Dict

class OrderStateMachine:
    """
    State machine para validar transiciones de orden.
    Previene transiciones inválidas causadas por webhooks desordenados.
    """

    # Mapeo de transiciones válidas
    VALID_TRANSITIONS: Dict[OrderStatus, Set[OrderStatus]] = {
        OrderStatus.PENDING: {
            OrderStatus.CONFIRMED,
            OrderStatus.CANCELLED
        },
        OrderStatus.CONFIRMED: {
            OrderStatus.PROCESSING,
            OrderStatus.CANCELLED
        },
        OrderStatus.PROCESSING: {
            OrderStatus.SHIPPED,
            OrderStatus.CANCELLED
        },
        OrderStatus.SHIPPED: {
            OrderStatus.DELIVERED,
            OrderStatus.CANCELLED  # Cancelación excepcional
        },
        OrderStatus.DELIVERED: {
            OrderStatus.REFUNDED  # Solo refund después de entrega
        },
        OrderStatus.CANCELLED: set(),  # Estado terminal
        OrderStatus.REFUNDED: set()    # Estado terminal
    }

    @classmethod
    def is_valid_transition(
        cls,
        current_state: OrderStatus,
        new_state: OrderStatus
    ) -> bool:
        """
        Validate if state transition is allowed.

        Args:
            current_state: Current order status
            new_state: Proposed new status

        Returns:
            bool: True if transition is valid
        """
        # Idempotent: Same state always allowed
        if current_state == new_state:
            return True

        # Check valid transitions map
        allowed_states = cls.VALID_TRANSITIONS.get(current_state, set())
        return new_state in allowed_states

    @classmethod
    def get_allowed_transitions(
        cls,
        current_state: OrderStatus
    ) -> Set[OrderStatus]:
        """Get all allowed next states from current state."""
        return cls.VALID_TRANSITIONS.get(current_state, set())

    @classmethod
    def is_terminal_state(cls, state: OrderStatus) -> bool:
        """Check if state is terminal (no further transitions)."""
        return len(cls.VALID_TRANSITIONS.get(state, set())) == 0
```

### FASE 4: MECANISMO DE RETRY SEGURO

```python
# NUEVO CÓDIGO EN WEBHOOKS.PY

@router.post("/wompi", response_model=WebhookResponse, status_code=status.HTTP_200_OK)
async def wompi_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> WebhookResponse:
    """Handle Wompi payment webhook notifications with race condition protection."""

    body = await request.body()
    body_str = body.decode('utf-8')
    signature = request.headers.get("X-Event-Signature") or request.headers.get("X-Signature")

    # 1. ✅ Verificar firma PRIMERO
    signature_valid = False
    if settings.WOMPI_WEBHOOK_SECRET:
        signature_valid = verify_wompi_signature(body, signature, settings.WOMPI_WEBHOOK_SECRET)
        if not signature_valid:
            logger.warning("Wompi webhook signature verification failed")
            return WebhookResponse(status="ok")  # Always 200 per spec

    # 2. ✅ Parsear payload
    try:
        payload_dict = json.loads(body_str)
        event_data = WompiWebhookEvent(**payload_dict)
    except Exception as e:
        logger.error(f"Error parsing webhook payload: {str(e)}")
        return WebhookResponse(status="ok")

    transaction_data = event_data.data
    wompi_transaction_id = transaction_data.get("id", "unknown")

    # 3. ✅ IDEMPOTENCY CHECK ATÓMICO
    try:
        is_duplicate, existing_event = await ensure_webhook_idempotency(
            db=db,
            event_id=wompi_transaction_id,
            event_type=event_data.event,
            raw_payload=payload_dict
        )

        if is_duplicate:
            logger.info(
                f"Duplicate webhook {wompi_transaction_id} received. "
                f"Original processed at {existing_event.created_at}"
            )
            # ✅ Return 200 OK - No procesamos duplicado
            return WebhookResponse(status="ok")

    except Exception as e:
        logger.error(f"Idempotency check failed: {str(e)}")
        # ✅ Fail-secure: No procesar si no podemos verificar
        return WebhookResponse(status="ok")

    # 4. ✅ Procesar webhook CON LOCKS
    try:
        processing_result = await update_order_from_webhook(
            db=db,
            transaction_data=transaction_data,
            wompi_transaction_id=wompi_transaction_id
        )

        # 5. ✅ Actualizar estado del webhook event
        await db.execute(
            update(WebhookEvent)
            .where(WebhookEvent.event_id == wompi_transaction_id)
            .values(
                event_status=WebhookEventStatus.PROCESSED if processing_result.success else WebhookEventStatus.FAILED,
                processed_at=datetime.utcnow(),
                processing_error=None if processing_result.success else processing_result.message,
                signature=signature,
                signature_validated=signature_valid
            )
        )
        await db.commit()

        if processing_result.success:
            logger.info(
                f"Webhook processed successfully: "
                f"Order {processing_result.order_id} → {processing_result.updated_order_status}"
            )
        else:
            logger.error(
                f"Webhook processing failed: "
                f"{processing_result.status} - {processing_result.message}"
            )

    except Exception as e:
        logger.error(f"Unexpected error processing webhook: {str(e)}", exc_info=True)
        # Always return 200 OK per Wompi spec

    return WebhookResponse(status="ok")
```

---

## 🧪 TEST CASES PARA VALIDACIÓN

### Test 1: Webhooks Simultáneos (Race Condition)

```python
# tests/security/test_webhook_race_condition.py

import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.endpoints.webhooks import update_order_from_webhook
from app.models.order import Order, OrderStatus, PaymentStatus

@pytest.mark.asyncio
async def test_concurrent_webhooks_same_payment(db: AsyncSession):
    """
    Test que 2 webhooks simultáneos del mismo pago NO creen transacciones duplicadas.

    Escenario:
    - Payment gateway envía webhook de confirmación
    - Por retry/delay, segundo webhook llega antes de completar primero
    - Sistema debe procesar solo UNA vez
    """
    # Setup: Crear orden en estado PENDING
    order = Order(
        order_number="ORD-12345",
        status=OrderStatus.PENDING,
        total_amount=100.0,
        buyer_id="user-123",
        shipping_name="Test User",
        shipping_phone="123456",
        shipping_address="Test Address",
        shipping_city="Bogota",
        shipping_state="Cundinamarca"
    )
    db.add(order)
    await db.commit()

    # Datos del webhook (mismo payment ID)
    webhook_data = {
        "id": "wompi-txn-12345",
        "reference": "ORD-12345",
        "status": "APPROVED",
        "amount_in_cents": 10000,
        "payment_method_type": "CARD"
    }

    # ✅ TEST: Ejecutar 2 webhooks en paralelo
    results = await asyncio.gather(
        update_order_from_webhook(db, webhook_data, "wompi-txn-12345"),
        update_order_from_webhook(db, webhook_data, "wompi-txn-12345"),
        return_exceptions=True
    )

    # ✅ VALIDACIONES

    # 1. Ambos requests deben completar (no error)
    assert len(results) == 2
    assert all(isinstance(r, WebhookProcessingResult) for r in results)

    # 2. Uno debe tener éxito, otro debe detectar duplicado
    success_count = sum(1 for r in results if r.success and r.status == "processed")
    duplicate_count = sum(1 for r in results if r.status == "already_processed" or r.status == "duplicate_transaction")

    assert success_count == 1, "Solo un webhook debe procesar exitosamente"
    assert duplicate_count == 1, "El segundo debe detectar duplicado"

    # 3. Verificar que solo hay 1 transacción en DB
    await db.refresh(order)
    assert len(order.transactions) == 1, "NO debe haber transacciones duplicadas"

    # 4. Verificar estado final correcto
    assert order.status == OrderStatus.CONFIRMED
    assert order.transactions[0].status == PaymentStatus.APPROVED
    assert order.transactions[0].gateway_transaction_id == "wompi-txn-12345"

    # 5. Verificar WebhookEvent unique
    webhook_events = await db.execute(
        select(WebhookEvent).where(WebhookEvent.event_id == "wompi-txn-12345")
    )
    events = webhook_events.scalars().all()
    assert len(events) == 1, "Solo debe haber 1 webhook event registrado"


@pytest.mark.asyncio
async def test_webhooks_out_of_order(db: AsyncSession):
    """
    Test que webhooks que llegan fuera de orden NO causen transiciones inválidas.

    Escenario:
    - Webhook APPROVED llega primero → orden CONFIRMED
    - Webhook PENDING llega después (retrasado)
    - Sistema NO debe regresar orden a PENDING
    """
    # Setup
    order = Order(
        order_number="ORD-67890",
        status=OrderStatus.PENDING,
        total_amount=200.0,
        buyer_id="user-456",
        shipping_name="Test User 2",
        shipping_phone="789012",
        shipping_address="Test Address 2",
        shipping_city="Medellin",
        shipping_state="Antioquia"
    )
    db.add(order)
    await db.commit()

    # 1. Webhook APPROVED llega primero
    approved_webhook = {
        "id": "wompi-txn-67890-approved",
        "reference": "ORD-67890",
        "status": "APPROVED",
        "amount_in_cents": 20000,
        "payment_method_type": "PSE"
    }

    result1 = await update_order_from_webhook(db, approved_webhook, "wompi-txn-67890-approved")
    assert result1.success
    await db.refresh(order)
    assert order.status == OrderStatus.CONFIRMED

    # 2. Webhook PENDING llega después (retrasado)
    pending_webhook = {
        "id": "wompi-txn-67890-pending",
        "reference": "ORD-67890",
        "status": "PENDING",
        "amount_in_cents": 20000,
        "payment_method_type": "PSE"
    }

    result2 = await update_order_from_webhook(db, pending_webhook, "wompi-txn-67890-pending")

    # ✅ VALIDACIÓN: Transición inválida debe ser bloqueada
    assert result2.success == False, "Webhook PENDING después de APPROVED debe fallar"
    assert result2.status == "invalid_state_transition"

    # ✅ Estado NO debe cambiar
    await db.refresh(order)
    assert order.status == OrderStatus.CONFIRMED, "Estado no debe regresar a PENDING"
```

### Test 2: Idempotency Keys

```python
@pytest.mark.asyncio
async def test_idempotency_key_enforcement(db: AsyncSession):
    """
    Test que idempotency key previene procesamiento duplicado.
    """
    event_id = "unique-event-12345"
    event_type = "transaction.updated"
    payload = {"data": {"id": "test"}}

    # Primera llamada: debe insertarse
    is_dup1, existing1 = await ensure_webhook_idempotency(db, event_id, event_type, payload)
    assert is_dup1 == False
    assert existing1 is None

    # Segunda llamada: debe detectar duplicado
    is_dup2, existing2 = await ensure_webhook_idempotency(db, event_id, event_type, payload)
    assert is_dup2 == True
    assert existing2 is not None
    assert existing2.event_id == event_id
```

### Test 3: Database Lock Timeout

```python
@pytest.mark.asyncio
async def test_database_lock_timeout_handling(db: AsyncSession):
    """
    Test que locks de DB se manejan correctamente y no causan deadlocks.
    """
    # Simular procesamiento lento que mantiene lock
    # Verificar que segundo request espera o falla gracefully
    pass  # TODO: Implementar
```

---

## 📊 PLAN DE IMPLEMENTACIÓN

### Sprint 1 (3 días) - CRÍTICO
- [ ] Implementar `with_for_update()` en queries de orden
- [ ] Implementar `ensure_webhook_idempotency()` atómico
- [ ] Agregar `OrderStateMachine` con validación de transiciones
- [ ] Unit tests básicos

### Sprint 2 (2 días) - ALTO
- [ ] Implementar mismos locks en PayU webhook
- [ ] Implementar validación de estado en Efecty
- [ ] Integration tests de race condition
- [ ] Load tests con webhooks concurrentes

### Sprint 3 (2 días) - MEDIO
- [ ] Monitoring de locks de DB (timeout alerts)
- [ ] Dashboard de webhooks duplicados detectados
- [ ] Documentación para equipo de QA
- [ ] Runbook de troubleshooting

### Sprint 4 (1 día) - BAJO
- [ ] Performance optimization de locks
- [ ] Índices de DB para mejorar lock performance
- [ ] Alertas automáticas para anomalías

---

## 🚨 RIESGOS DE LA SOLUCIÓN

### Riesgos Técnicos:

1. **Deadlocks de DB**:
   - Locks pueden causar deadlocks si no se adquieren en orden consistente
   - **Mitigación**: Timeout de 5s en locks, retry exponencial

2. **Performance degradation**:
   - Row locks aumentan latencia de webhooks
   - **Mitigación**: Índices optimizados, locks solo en orden + transacción

3. **Lock timeout en alta carga**:
   - Bajo carga extrema, locks pueden timeout
   - **Mitigación**: Queue de webhooks con processing ordenado

### Riesgos Operacionales:

1. **Rollback complejo**:
   - Si solución causa problemas, rollback es crítico
   - **Mitigación**: Feature flag para habilitar/deshabilitar locks

2. **Compatibilidad con webhooks antiguos**:
   - Webhooks en tránsito durante deploy
   - **Mitigación**: Backward compatibility, gradual rollout

---

## 📈 MÉTRICAS DE ÉXITO

### KPIs a Monitorear:

1. **Tasa de webhooks duplicados detectados**: Target < 0.1%
2. **Latencia promedio de webhooks**: Target < 500ms (con locks)
3. **Tasa de deadlocks de DB**: Target = 0
4. **Transacciones duplicadas en DB**: Target = 0
5. **Errores de transición de estado**: Target < 0.01%

### Alertas Críticas:

```yaml
alerts:
  - name: "Webhook Duplicate Rate High"
    condition: duplicate_rate > 1%
    severity: WARNING

  - name: "Database Lock Timeout"
    condition: lock_timeout_count > 10 per_hour
    severity: CRITICAL

  - name: "Duplicate Transactions Created"
    condition: duplicate_txn_count > 0
    severity: CRITICAL

  - name: "Invalid State Transition Detected"
    condition: invalid_transition_count > 5 per_hour
    severity: WARNING
```

---

## 🎯 CONCLUSIÓN

La race condition en webhooks es un **bug crítico de seguridad financiera** que debe resolverse INMEDIATAMENTE.

**Recomendación**: Implementar Fase 1 y Fase 2 en el próximo release de emergencia (dentro de 7 días).

**Riesgo si no se corrige**:
- Pérdida financiera potencial: $$$
- Violación de compliance: PCI DSS, SOX
- Daño reputacional: Clientes ven cobros duplicados

**Aprobación requerida de**:
- ✅ SecurityBackendAI (yo)
- ⏳ BackendFrameworkAI (implementación)
- ⏳ DatabaseArchitectAI (optimización de locks)
- ⏳ MasterOrchestrator (autorización final)

---

**Documento generado por**: SecurityBackendAI
**Fecha**: 2025-10-02
**Clasificación**: CONFIDENCIAL - INTERNAL USE ONLY
**Próxima revisión**: Después de implementación Sprint 1
