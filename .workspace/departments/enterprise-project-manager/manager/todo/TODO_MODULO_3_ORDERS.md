# 🏪 TODO MÓDULO 3: ORDER MANAGEMENT ENTERPRISE

**Base Compatible**: TODO_CONFIGURACION_BASE_ENTERPRISE.md ✅
**Dependencias**: Products ✅, Users ✅, Database Architecture ✅
**Tiempo Estimado**: 22 horas (12h backend + 10h frontend)
**Prioridad**: 🔴 CRÍTICA - Revenue Critical Module

---

## 🎯 OBJETIVO DEL MÓDULO
Crear el sistema enterprise de gestión de órdenes donde el SUPERUSUARIO puede controlar todas las órdenes de todos los vendors y buyers, con workflow avanzado, tracking GPS, sistema de quejas, y analytics profundo.

---

## 🗄️ BACKEND - DATABASE & MODELS (6 horas)

### 3.1 Extender Modelo Order Enterprise (2h)
**Compatible con**: Order model existente ✅, User ✅, Product ✅

```python
# app/models/order.py - EXTENDER MODELO EXISTENTE
class Order(BaseModel):
    # CAMPOS EXISTENTES (mantener compatibilidad)
    id: int = Field(primary_key=True)
    buyer_id: FK to User
    vendor_id: FK to User
    total_amount: decimal
    status: OrderStatus
    created_at: datetime
    updated_at: datetime

    # NUEVOS CAMPOS ENTERPRISE
    # Información de Identificación
    order_number: str = Field(unique=True)  # ORD-2025-000001
    external_reference: str = Field(nullable=True)  # Referencia cliente
    order_source: OrderSource = Field(default="web")  # web, mobile, api, phone

    # Workflow y Estados Avanzados
    workflow_state: WorkflowState = Field(default="pending_payment")
    """
    pending_payment → paid → processing → shipped → in_transit →
    delivered → completed | cancelled | returned | refunded
    """
    processing_priority: Priority = Field(default="normal")  # low, normal, high, urgent
    estimated_delivery: datetime = Field(nullable=True)
    actual_delivery: datetime = Field(nullable=True)
    processing_started_at: datetime = Field(nullable=True)
    shipped_at: datetime = Field(nullable=True)
    delivered_at: datetime = Field(nullable=True)

    # Información de Envío
    shipping_address: JSON  # Dirección completa estructurada
    billing_address: JSON   # Dirección de facturación
    shipping_method: str = Field(nullable=True)  # standard, express, overnight
    shipping_cost: decimal = Field(default=0.0)
    shipping_carrier: str = Field(nullable=True)  # "Servientrega", "Coordinadora"
    tracking_number: str = Field(nullable=True, unique=True)

    # GPS Tracking
    current_location: JSON = Field(nullable=True)  # {lat, lng, address, timestamp}
    location_history: JSON = Field(default=list)  # Array de ubicaciones
    delivery_instructions: text = Field(nullable=True)

    # Información de Pago
    payment_method: str = Field(nullable=True)  # "credit_card", "pse", "cash"
    payment_reference: str = Field(nullable=True, unique=True)
    payment_status: PaymentStatus = Field(default="pending")
    paid_at: datetime = Field(nullable=True)
    payment_gateway: str = Field(nullable=True)  # "wompi", "payu", "stripe"

    # Costos y Comisiones
    subtotal: decimal = Field(ge=0)
    tax_amount: decimal = Field(default=0.0)
    discount_amount: decimal = Field(default=0.0)
    commission_rate: decimal = Field(default=0.0)  # % de comisión aplicada
    platform_commission: decimal = Field(default=0.0)  # Comisión calculada
    vendor_payout: decimal = Field(default=0.0)  # Pago al vendedor

    # Control y Auditoría
    assigned_to: FK to User = Field(nullable=True)  # Admin asignado para procesar
    processed_by: FK to User = Field(nullable=True)  # Quien procesó la orden
    cancelled_by: FK to User = Field(nullable=True)
    cancellation_reason: text = Field(nullable=True)

    # Calidad y Experiencia
    customer_rating: int = Field(nullable=True, ge=1, le=5)
    customer_feedback: text = Field(nullable=True)
    internal_notes: text = Field(nullable=True)  # Notas administrativas

    # Metadata y Configuración
    metadata: JSON = Field(default=dict)  # Datos adicionales flexibles
    tags: JSON = Field(default=list)  # Etiquetas para categorización
    flags: JSON = Field(default=list)  # red_flags, rush_order, vip_customer
```

**Dependencias**: User ✅, Product ✅, existing Order model
**Specialist**: @backend-senior-developer

### 3.2 Crear OrderItem Enterprise (1h)
**Propósito**: Manejo detallado de items en la orden

```python
# app/models/order_item.py - EXTENDER MODELO EXISTENTE
class OrderItem(BaseModel):
    # CAMPOS EXISTENTES (mantener)
    id: int
    order_id: FK to Order
    product_id: FK to Product
    quantity: int
    unit_price: decimal
    total_price: decimal

    # NUEVOS CAMPOS ENTERPRISE
    product_variant_id: FK to ProductVariant = Field(nullable=True)
    product_snapshot: JSON  # Snapshot del producto al momento de la orden
    """
    {
      "name": "Producto X",
      "description": "...",
      "images": [...],
      "vendor_name": "Vendor Y",
      "category": "Electronics"
    }
    """

    # Pricing y Descuentos
    original_price: decimal  # Precio original del producto
    applied_discounts: JSON = Field(default=list)  # Descuentos aplicados
    discount_amount: decimal = Field(default=0.0)
    tax_rate: decimal = Field(default=0.0)
    tax_amount: decimal = Field(default=0.0)

    # Estado Individual del Item
    item_status: ItemStatus = Field(default="pending")
    """
    pending → reserved → processing → shipped → delivered →
    cancelled → returned → refunded
    """

    # Logística
    requires_special_handling: bool = Field(default=False)
    weight: decimal = Field(nullable=True)
    dimensions: JSON = Field(nullable=True)  # {length, width, height}

    # Control de Calidad
    quality_check_passed: bool = Field(nullable=True)
    quality_notes: text = Field(nullable=True)
    checked_by: FK to User = Field(nullable=True)
    checked_at: datetime = Field(nullable=True)

    # Tracking Individual
    item_tracking_events: JSON = Field(default=list)
    """
    [
      {"event": "reserved", "timestamp": "...", "location": "..."},
      {"event": "packed", "timestamp": "...", "user": "..."}
    ]
    """
```

**Dependencias**: Order ✅, Product ✅, ProductVariant ✅
**Specialist**: @backend-senior-developer

### 3.3 Crear OrderTracking GPS System (1.5h)
**Propósito**: Sistema completo de tracking con GPS

```python
# app/models/order_tracking.py - NUEVO MODELO
class OrderTrackingEvent(BaseModel):
    id: int = Field(primary_key=True)
    order_id: FK to Order
    event_type: TrackingEventType
    """
    order_created, payment_confirmed, processing_started,
    packed, shipped, in_transit, out_for_delivery,
    delivered, delivery_attempted, exception_occurred
    """

    event_description: str
    event_details: JSON = Field(default=dict)

    # Ubicación GPS
    location_lat: decimal = Field(nullable=True)
    location_lng: decimal = Field(nullable=True)
    location_address: text = Field(nullable=True)
    location_accuracy: decimal = Field(nullable=True)  # metros

    # Información del Evento
    recorded_by: FK to User = Field(nullable=True)  # Usuario o sistema
    recorded_by_system: str = Field(nullable=True)  # "gps_tracker", "manual", "api"
    is_customer_visible: bool = Field(default=True)
    is_automated: bool = Field(default=False)

    # Evidencia
    photo_urls: JSON = Field(default=list)
    signature_url: str = Field(nullable=True)  # Para entregas
    notes: text = Field(nullable=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)

class DeliveryAttempt(BaseModel):
    """Registro de intentos de entrega"""
    id: int = Field(primary_key=True)
    order_id: FK to Order
    attempt_number: int
    attempted_at: datetime = Field(default_factory=datetime.utcnow)
    delivery_status: DeliveryStatus  # successful, failed, rescheduled
    failure_reason: str = Field(nullable=True)  # "not_home", "wrong_address"
    next_attempt_scheduled: datetime = Field(nullable=True)
    delivery_person: str = Field(nullable=True)
    contact_phone: str = Field(nullable=True)
    notes: text = Field(nullable=True)
```

**Dependencias**: Order ✅, GPS tracking service
**Specialist**: @backend-senior-developer

### 3.4 Sistema OrderDispute (1h)
**Propósito**: Manejo de quejas y disputas

```python
# app/models/order_dispute.py - NUEVO MODELO
class OrderDispute(BaseModel):
    id: int = Field(primary_key=True)
    order_id: FK to Order
    reported_by: FK to User  # Buyer o Vendor
    dispute_type: DisputeType
    """
    product_not_received, product_damaged, wrong_product,
    quality_issue, delivery_issue, refund_request,
    vendor_dispute, payment_issue
    """

    dispute_category: str  # "delivery", "product", "service", "payment"
    priority: Priority = Field(default="normal")

    # Descripción del Problema
    subject: str
    description: text
    evidence_urls: JSON = Field(default=list)  # Fotos, documentos

    # Resolución
    status: DisputeStatus = Field(default="open")
    # open → investigating → resolved → closed → escalated
    assigned_to: FK to User = Field(nullable=True)  # Admin asignado
    resolution: text = Field(nullable=True)
    resolution_amount: decimal = Field(nullable=True)  # Reembolso si aplica
    resolved_at: datetime = Field(nullable=True)
    resolved_by: FK to User = Field(nullable=True)

    # Comunicación
    last_response_at: datetime = Field(nullable=True)
    customer_satisfied: bool = Field(nullable=True)
    internal_notes: text = Field(nullable=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DisputeMessage(BaseModel):
    """Mensajes en la disputa"""
    id: int = Field(primary_key=True)
    dispute_id: FK to OrderDispute
    sender_id: FK to User
    message: text
    attachments: JSON = Field(default=list)
    is_internal: bool = Field(default=False)  # Solo para admins
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Dependencies**: Order ✅, User ✅
**Specialist**: @backend-senior-developer

### 3.5 OrderRefund System (1h)
**Propósito**: Sistema automatizado de reembolsos

```python
# app/models/order_refund.py - NUEVO MODELO
class OrderRefund(BaseModel):
    id: int = Field(primary_key=True)
    order_id: FK to Order
    refund_type: RefundType  # full, partial, shipping_only
    refund_reason: RefundReason
    """
    customer_request, defective_product, wrong_item,
    shipping_damage, cancelled_by_vendor, system_error,
    dispute_resolution
    """

    # Montos
    original_amount: decimal  # Monto original de la orden
    refund_amount: decimal    # Monto a reembolsar
    refund_breakdown: JSON    # Desglose del reembolso
    """
    {
      "product_cost": 100.00,
      "shipping_cost": 15.00,
      "tax_refund": 19.00,
      "commission_deduction": -10.00,
      "processing_fee": -2.00
    }
    """

    # Proceso
    status: RefundStatus = Field(default="requested")
    # requested → approved → processing → completed → failed → cancelled
    requested_by: FK to User
    approved_by: FK to User = Field(nullable=True)
    processed_by: FK to User = Field(nullable=True)

    # Datos de Pago
    original_payment_method: str
    refund_method: str = Field(nullable=True)  # "original_method", "bank_transfer"
    payment_reference: str = Field(nullable=True)
    refund_reference: str = Field(nullable=True, unique=True)

    # Fechas
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    approved_at: datetime = Field(nullable=True)
    processed_at: datetime = Field(nullable=True)
    completed_at: datetime = Field(nullable=True)

    # Notas y Seguimiento
    customer_notes: text = Field(nullable=True)
    admin_notes: text = Field(nullable=True)
    processing_notes: text = Field(nullable=True)
```

**Dependencies**: Order ✅, Payment system integration
**Specialist**: @backend-senior-developer

### 3.6 OrderAnalytics Data (0.5h)
**Propósito**: Métricas y analytics de órdenes

```python
# app/models/order_analytics.py - NUEVO MODELO
class OrderMetrics(BaseModel):
    """Métricas calculadas por período"""
    id: int = Field(primary_key=True)

    # Período de cálculo
    metric_date: date
    metric_period: str  # daily, weekly, monthly

    # Métricas por Vendedor (opcional)
    vendor_id: FK to User = Field(nullable=True)  # null = métricas globales

    # Volumen
    total_orders: int = Field(default=0)
    completed_orders: int = Field(default=0)
    cancelled_orders: int = Field(default=0)
    returned_orders: int = Field(default=0)

    # Revenue
    total_revenue: decimal = Field(default=0.0)
    average_order_value: decimal = Field(default=0.0)
    total_commission: decimal = Field(default=0.0)

    # Performance
    avg_processing_time: decimal = Field(default=0.0)  # horas
    avg_delivery_time: decimal = Field(default=0.0)    # horas
    on_time_delivery_rate: decimal = Field(default=0.0)  # %

    # Calidad
    customer_satisfaction: decimal = Field(default=0.0)  # promedio rating
    dispute_rate: decimal = Field(default=0.0)  # %
    refund_rate: decimal = Field(default=0.0)   # %

    calculated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Dependencies**: Order data ✅
**Specialist**: @backend-senior-developer

---

## 🔌 BACKEND - SERVICES & APIS (6 horas)

### 3.7 OrderWorkflow Service (2h)
**Propósito**: Gestión completa del workflow de órdenes

```python
# app/services/order_workflow_service.py - NUEVO SERVICIO
class OrderWorkflowService:

    def create_order_enterprise(
        self,
        order_data: dict,
        buyer: User,
        auto_process: bool = False
    ) -> Order:
        """Crear orden con workflow completo"""

        # Generar número de orden único
        order_number = self.generate_order_number()

        # Crear orden base
        order = Order(
            **order_data,
            buyer_id=buyer.id,
            order_number=order_number,
            workflow_state="pending_payment"
        )
        db.add(order)
        db.flush()  # Para obtener el ID

        # Crear items con validación de inventario
        total_amount = 0
        for item_data in order_data['items']:
            # Validar disponibilidad
            if not self.validate_product_availability(item_data):
                raise InsufficientStockError()

            # Reservar inventario
            self.reserve_inventory(item_data['product_id'], item_data['quantity'])

            # Crear item
            order_item = OrderItem(**item_data, order_id=order.id)
            db.add(order_item)
            total_amount += order_item.total_price

        order.total_amount = total_amount

        # Crear evento inicial de tracking
        self.create_tracking_event(
            order_id=order.id,
            event_type="order_created",
            description="Orden creada exitosamente"
        )

        # Si auto_process, avanzar al siguiente estado
        if auto_process:
            self.advance_workflow(order.id, "payment_confirmed")

        db.commit()
        return order

    def advance_workflow(
        self,
        order_id: int,
        new_state: str,
        processed_by: User = None,
        notes: str = None
    ):
        """Avanzar orden en el workflow"""
        order = db.query(Order).filter(Order.id == order_id).first()

        if not self.can_transition_to(order.workflow_state, new_state):
            raise InvalidTransitionError(f"Cannot transition from {order.workflow_state} to {new_state}")

        old_state = order.workflow_state
        order.workflow_state = new_state
        order.updated_at = datetime.utcnow()

        if processed_by:
            order.processed_by = processed_by.id

        # Actualizar timestamps específicos
        self.update_state_timestamps(order, new_state)

        # Crear evento de tracking
        self.create_tracking_event(
            order_id=order.id,
            event_type=f"state_changed_{new_state}",
            description=f"Estado cambiado de {old_state} a {new_state}",
            recorded_by=processed_by.id if processed_by else None,
            notes=notes
        )

        # Notificar a las partes interesadas
        self.notify_state_change(order, old_state, new_state)

        # Ejecutar acciones automáticas según el estado
        self.execute_state_actions(order, new_state)

        db.commit()

    def bulk_process_orders(
        self,
        order_ids: List[int],
        action: str,
        processed_by: User
    ):
        """SUPERUSER puede procesar órdenes masivamente"""
        if processed_by.user_type != UserType.SUPERUSER:
            raise PermissionDenied("Only SUPERUSER can bulk process orders")

        orders = db.query(Order).filter(Order.id.in_(order_ids)).all()
        results = {"success": [], "failed": []}

        for order in orders:
            try:
                if action == "mark_shipped":
                    self.advance_workflow(order.id, "shipped", processed_by)
                elif action == "mark_delivered":
                    self.advance_workflow(order.id, "delivered", processed_by)
                elif action == "cancel":
                    self.cancel_order(order.id, "Bulk cancellation", processed_by)

                results["success"].append(order.id)
            except Exception as e:
                results["failed"].append({"order_id": order.id, "error": str(e)})

        return results

    def get_orders_for_user(self, requesting_user: User, filters: dict = None):
        """Control de acceso para obtener órdenes"""
        query = db.query(Order)

        if requesting_user.user_type == UserType.SUPERUSER:
            # SUPERUSER ve todas las órdenes
            pass
        elif requesting_user.user_type == UserType.VENDOR:
            # Vendor ve solo sus órdenes
            query = query.filter(Order.vendor_id == requesting_user.id)
        elif requesting_user.user_type == UserType.BUYER:
            # Buyer ve solo sus compras
            query = query.filter(Order.buyer_id == requesting_user.id)
        elif requesting_user.user_type.startswith("ADMIN_"):
            # Admins ven órdenes según su área
            if requesting_user.user_type == "ADMIN_VENTAS":
                # Ve todas las órdenes para métricas de ventas
                pass
            else:
                # Otros admins ven según criterios específicos
                query = self.apply_admin_filters(query, requesting_user)
        else:
            raise PermissionDenied("User cannot access orders")

        # Aplicar filtros adicionales
        if filters:
            query = self.apply_filters(query, filters)

        return query.all()
```

**Dependencies**: Order models ✅, User system ✅, Inventory system
**Specialist**: @backend-senior-developer

### 3.8 OrderTracking Service (1.5h)
**Propósito**: Servicio de tracking con GPS

```python
# app/services/order_tracking_service.py - NUEVO SERVICIO
class OrderTrackingService:

    def create_tracking_event(
        self,
        order_id: int,
        event_type: str,
        description: str,
        location_data: dict = None,
        recorded_by: int = None,
        evidence: dict = None
    ):
        """Crear evento de tracking"""

        tracking_event = OrderTrackingEvent(
            order_id=order_id,
            event_type=event_type,
            event_description=description,
            recorded_by=recorded_by,
            is_automated=(recorded_by is None)
        )

        # Agregar datos de ubicación GPS si están disponibles
        if location_data:
            tracking_event.location_lat = location_data.get('lat')
            tracking_event.location_lng = location_data.get('lng')
            tracking_event.location_address = location_data.get('address')
            tracking_event.location_accuracy = location_data.get('accuracy')

        # Agregar evidencia (fotos, firma, etc.)
        if evidence:
            tracking_event.photo_urls = evidence.get('photos', [])
            tracking_event.signature_url = evidence.get('signature')
            tracking_event.notes = evidence.get('notes')

        db.add(tracking_event)

        # Actualizar ubicación actual de la orden
        if location_data:
            self.update_order_location(order_id, location_data)

        # Notificar al cliente si el evento es visible
        if tracking_event.is_customer_visible:
            self.notify_customer_tracking_update(order_id, tracking_event)

        db.commit()
        return tracking_event

    def update_gps_location(
        self,
        order_id: int,
        lat: float,
        lng: float,
        carrier_info: dict = None
    ):
        """Actualización GPS desde transportadora"""

        # Obtener dirección desde coordenadas
        address = self.reverse_geocode(lat, lng)

        location_data = {
            "lat": lat,
            "lng": lng,
            "address": address,
            "timestamp": datetime.utcnow().isoformat(),
            "carrier": carrier_info.get('carrier_name') if carrier_info else None,
            "vehicle": carrier_info.get('vehicle_info') if carrier_info else None
        }

        # Actualizar orden
        order = db.query(Order).filter(Order.id == order_id).first()
        order.current_location = location_data

        # Agregar a historial
        if not order.location_history:
            order.location_history = []
        order.location_history.append(location_data)

        # Crear evento de tracking
        self.create_tracking_event(
            order_id=order_id,
            event_type="location_update",
            description=f"Ubicación actualizada: {address}",
            location_data=location_data,
            recorded_by_system="gps_tracker"
        )

        db.commit()

    def get_tracking_info(self, order_id: int, requesting_user: User):
        """Obtener información de tracking"""
        order = db.query(Order).filter(Order.id == order_id).first()

        # Verificar permisos
        if not self.can_view_tracking(order, requesting_user):
            raise PermissionDenied("Cannot view tracking for this order")

        # Obtener eventos de tracking
        events = db.query(OrderTrackingEvent).filter(
            OrderTrackingEvent.order_id == order_id
        ).order_by(OrderTrackingEvent.created_at.desc()).all()

        # Filtrar eventos según permisos
        if requesting_user.user_type not in [UserType.SUPERUSER]:
            events = [e for e in events if e.is_customer_visible]

        return {
            "order": order,
            "current_location": order.current_location,
            "location_history": order.location_history,
            "tracking_events": events,
            "estimated_delivery": order.estimated_delivery,
            "delivery_attempts": self.get_delivery_attempts(order_id)
        }

    def record_delivery_attempt(
        self,
        order_id: int,
        delivery_status: str,
        failure_reason: str = None,
        delivery_person: str = None,
        evidence: dict = None
    ):
        """Registrar intento de entrega"""

        # Contar intentos previos
        attempt_count = db.query(DeliveryAttempt).filter(
            DeliveryAttempt.order_id == order_id
        ).count() + 1

        delivery_attempt = DeliveryAttempt(
            order_id=order_id,
            attempt_number=attempt_count,
            delivery_status=delivery_status,
            failure_reason=failure_reason,
            delivery_person=delivery_person
        )

        db.add(delivery_attempt)

        # Crear evento de tracking
        event_description = f"Intento de entrega #{attempt_count}"
        if delivery_status == "successful":
            event_description = "Entrega exitosa"
            # Avanzar workflow
            self.advance_order_workflow(order_id, "delivered")
        elif delivery_status == "failed":
            event_description = f"Intento fallido: {failure_reason}"
            # Programar próximo intento si es posible
            if attempt_count < 3:  # Máximo 3 intentos
                next_attempt = datetime.utcnow() + timedelta(days=1)
                delivery_attempt.next_attempt_scheduled = next_attempt

        self.create_tracking_event(
            order_id=order_id,
            event_type="delivery_attempt",
            description=event_description,
            evidence=evidence
        )

        db.commit()
        return delivery_attempt
```

**Dependencies**: Order models ✅, GPS service, Notification service
**Specialist**: @backend-senior-developer

### 3.9 Order APIs Enterprise (2.5h)
**Propósito**: APIs completas para gestión de órdenes

```python
# app/api/v1/endpoints/orders.py - EXTENDER ENDPOINTS EXISTENTES

# ENDPOINTS EXISTENTES (mantener compatibilidad)
@router.post("/orders/", response_model=OrderResponse)
@require_role([UserType.BUYER])
async def create_order():
    """Crear orden - endpoint existente"""
    pass

@router.get("/orders/my", response_model=List[OrderResponse])
@require_role([UserType.BUYER])
async def get_my_orders():
    """Órdenes del buyer - endpoint existente"""
    pass

# NUEVOS ENDPOINTS ENTERPRISE - SUPERUSER
@router.get("/superuser/orders/all", response_model=List[OrderResponse])
@require_role([UserType.SUPERUSER])
async def get_all_orders_superuser(
    status: OrderStatus = None,
    vendor_id: int = None,
    date_from: date = None,
    date_to: date = None,
    skip: int = 0,
    limit: int = 100
):
    """SUPERUSER obtiene todas las órdenes de todos los vendors"""
    pass

@router.put("/superuser/orders/{order_id}/workflow", response_model=OrderResponse)
@require_role([UserType.SUPERUSER])
async def update_order_workflow(
    order_id: int,
    workflow_data: OrderWorkflowUpdate
):
    """SUPERUSER puede cambiar estado de cualquier orden"""
    pass

@router.post("/superuser/orders/bulk-process", response_model=BulkProcessResponse)
@require_role([UserType.SUPERUSER])
async def bulk_process_orders(
    order_ids: List[int],
    action: str,
    notes: str = None
):
    """Procesamiento masivo de órdenes"""
    pass

@router.get("/superuser/orders/analytics", response_model=OrderAnalyticsResponse)
@require_role([UserType.SUPERUSER])
async def get_order_analytics(
    period: str = "30d",
    vendor_id: int = None,
    group_by: str = "day"
):
    """Analytics completo de órdenes"""
    pass

# ENDPOINTS PARA VENDORS
@router.get("/vendor/orders/", response_model=List[OrderResponse])
@require_role([UserType.VENDOR])
async def get_vendor_orders(
    status: OrderStatus = None,
    skip: int = 0,
    limit: int = 50
):
    """Vendor obtiene solo sus órdenes"""
    pass

@router.put("/vendor/orders/{order_id}/process", response_model=OrderResponse)
@require_role([UserType.VENDOR])
async def process_vendor_order(
    order_id: int,
    process_data: OrderProcessData
):
    """Vendor procesa su orden"""
    pass

@router.post("/vendor/orders/{order_id}/ship", response_model=OrderResponse)
@require_role([UserType.VENDOR])
async def ship_order(
    order_id: int,
    shipping_data: ShippingData
):
    """Marcar orden como enviada"""
    pass

# ENDPOINTS DE TRACKING
@router.get("/orders/{order_id}/tracking", response_model=TrackingResponse)
@require_authentication
async def get_order_tracking(order_id: int):
    """Obtener información de tracking"""
    pass

@router.post("/orders/{order_id}/tracking/location", response_model=TrackingEventResponse)
@require_role([UserType.SUPERUSER, UserType.VENDOR])
async def update_tracking_location(
    order_id: int,
    location_data: LocationUpdate
):
    """Actualizar ubicación GPS"""
    pass

@router.post("/orders/{order_id}/delivery-attempt", response_model=DeliveryAttemptResponse)
@require_role([UserType.SUPERUSER, UserType.VENDOR])
async def record_delivery_attempt(
    order_id: int,
    delivery_data: DeliveryAttemptData
):
    """Registrar intento de entrega"""
    pass

# ENDPOINTS DE DISPUTAS
@router.post("/orders/{order_id}/dispute", response_model=DisputeResponse)
@require_authentication
async def create_dispute(
    order_id: int,
    dispute_data: DisputeCreateData
):
    """Crear disputa por orden"""
    pass

@router.get("/superuser/disputes/", response_model=List[DisputeResponse])
@require_role([UserType.SUPERUSER])
async def get_all_disputes():
    """SUPERUSER ve todas las disputas"""
    pass

@router.put("/superuser/disputes/{dispute_id}/resolve", response_model=DisputeResponse)
@require_role([UserType.SUPERUSER])
async def resolve_dispute(
    dispute_id: int,
    resolution_data: DisputeResolutionData
):
    """Resolver disputa"""
    pass

# ENDPOINTS DE REFUNDS
@router.post("/orders/{order_id}/refund", response_model=RefundResponse)
@require_role([UserType.SUPERUSER, UserType.BUYER])
async def request_refund(
    order_id: int,
    refund_data: RefundRequestData
):
    """Solicitar reembolso"""
    pass

@router.put("/superuser/refunds/{refund_id}/approve", response_model=RefundResponse)
@require_role([UserType.SUPERUSER])
async def approve_refund(
    refund_id: int,
    approval_data: RefundApprovalData
):
    """Aprobar reembolso"""
    pass
```

**Dependencies**: Order models ✅, Workflow service ✅, Tracking service ✅
**Specialist**: @backend-senior-developer

---

## ⚛️ FRONTEND - COMPONENTS & INTERFACES (10 horas)

### 3.10 OrderManagementDashboard SUPERUSER (4h)
**Propósito**: Dashboard central para control total de órdenes

```jsx
// frontend/src/components/superuser/OrderManagementDashboard.tsx
import { useState, useEffect } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { orderService } from '../../services/orderService';

const OrderManagementDashboard = () => {
  const { user, hasPermission } = useAuthStore();
  const [orders, setOrders] = useState([]);
  const [analytics, setAnalytics] = useState({});
  const [filters, setFilters] = useState({});
  const [selectedOrders, setSelectedOrders] = useState([]);

  if (!hasPermission('order.manage_all')) {
    return <Unauthorized />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header con métricas globales */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
            <OrderMetricCard
              title="Órdenes Totales"
              value={analytics.totalOrders}
              change={analytics.orderGrowth}
              icon={ShoppingCart}
              color="blue"
            />
            <OrderMetricCard
              title="Revenue Hoy"
              value={formatCurrency(analytics.revenueToday)}
              change={analytics.revenueChange}
              icon={DollarSign}
              color="green"
            />
            <OrderMetricCard
              title="Procesando"
              value={analytics.processingOrders}
              change={analytics.processingChange}
              icon={Clock}
              color="yellow"
            />
            <OrderMetricCard
              title="En Tránsito"
              value={analytics.inTransitOrders}
              change={analytics.transitChange}
              icon={Truck}
              color="purple"
            />
            <OrderMetricCard
              title="Disputas Activas"
              value={analytics.activeDisputes}
              change={analytics.disputeChange}
              icon={AlertTriangle}
              color="red"
            />
          </div>
        </div>
      </div>

      {/* Filtros y búsqueda avanzada */}
      <div className="max-w-7xl mx-auto py-6 px-4">
        <OrderAdvancedFilters
          filters={filters}
          onFiltersChange={setFilters}
          showAllVendors={true}  // SUPERUSER ve todos los vendors
          showAdvancedFilters={true}
        />

        {/* Acciones masivas */}
        {selectedOrders.length > 0 && (
          <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center justify-between">
              <span className="text-blue-800">
                {selectedOrders.length} órdenes seleccionadas
              </span>
              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  onClick={() => handleBulkAction('mark_shipped')}
                  icon={Truck}
                >
                  Marcar Enviado
                </Button>
                <Button
                  variant="outline"
                  onClick={() => handleBulkAction('mark_delivered')}
                  icon={CheckCircle}
                >
                  Marcar Entregado
                </Button>
                <Button
                  variant="outline"
                  onClick={() => handleBulkAction('cancel')}
                  icon={XCircle}
                >
                  Cancelar
                </Button>
                <Button
                  variant="outline"
                  onClick={() => handleBulkAction('export')}
                  icon={Download}
                >
                  Exportar
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Vista de órdenes con tabs */}
        <div className="bg-white rounded-lg shadow">
          <OrderViewTabs
            activeTab={filters.view}
            onTabChange={(tab) => setFilters({...filters, view: tab})}
            tabs={[
              { id: 'all', name: 'Todas', count: analytics.totalOrders },
              { id: 'pending', name: 'Pendientes', count: analytics.pendingOrders },
              { id: 'processing', name: 'Procesando', count: analytics.processingOrders },
              { id: 'shipped', name: 'Enviadas', count: analytics.shippedOrders },
              { id: 'delivered', name: 'Entregadas', count: analytics.deliveredOrders },
              { id: 'disputes', name: 'Disputas', count: analytics.disputeOrders }
            ]}
          />

          <OrderDataTable
            orders={orders}
            selectedOrders={selectedOrders}
            onSelectionChange={setSelectedOrders}
            actions={[
              'view', 'edit_workflow', 'tracking', 'dispute',
              'refund', 'impersonate_buyer', 'contact_vendor',
              'priority_change', 'assign_admin'
            ]}
            onAction={handleOrderAction}
            showVendorInfo={true}  // SUPERUSER ve info del vendor
            showInternalNotes={true}  // SUPERUSER ve notas internas
          />
        </div>

        {/* Paginación */}
        <OrderPagination
          currentPage={filters.page}
          totalPages={Math.ceil(analytics.totalOrders / filters.limit)}
          onPageChange={(page) => setFilters({...filters, page})}
        />
      </div>

      {/* Modales */}
      <OrderDetailModal />
      <OrderWorkflowEditor />
      <OrderDisputeModal />
      <OrderRefundModal />
      <BulkOrderActionModal />
    </div>
  );
};
```

**Dependencies**: Auth store ✅, Order service (nuevo), UI components ✅
**Specialist**: @frontend-react-specialist

### 3.11 OrderTrackingInterface (2h)
**Propósito**: Interface de tracking con mapa GPS

```jsx
// frontend/src/components/ui/OrderTrackingInterface.tsx
import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Polyline } from 'react-leaflet';
import { orderTrackingService } from '../../services/orderTrackingService';

const OrderTrackingInterface = ({ orderId, userRole }) => {
  const [trackingData, setTrackingData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTrackingData();
    // Configurar updates en tiempo real cada 30 segundos
    const interval = setInterval(loadTrackingData, 30000);
    return () => clearInterval(interval);
  }, [orderId]);

  const loadTrackingData = async () => {
    try {
      const data = await orderTrackingService.getTracking(orderId);
      setTrackingData(data);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="space-y-6">
      {/* Header con estado actual */}
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold">
              Seguimiento - Orden #{trackingData.order.order_number}
            </h2>
            <p className="text-gray-600">
              Estado: <span className="font-medium">{trackingData.order.workflow_state}</span>
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-600">Entrega estimada</p>
            <p className="font-medium">
              {formatDate(trackingData.order.estimated_delivery)}
            </p>
          </div>
        </div>

        {/* Progress bar del estado */}
        <OrderProgressBar
          currentState={trackingData.order.workflow_state}
          states={['paid', 'processing', 'shipped', 'in_transit', 'delivered']}
        />
      </div>

      {/* Mapa GPS */}
      {trackingData.current_location && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="p-4 border-b">
            <h3 className="font-medium">Ubicación Actual</h3>
            <p className="text-sm text-gray-600">
              Última actualización: {formatDateTime(trackingData.current_location.timestamp)}
            </p>
          </div>
          <div className="h-64">
            <MapContainer
              center={[trackingData.current_location.lat, trackingData.current_location.lng]}
              zoom={13}
              className="h-full w-full"
            >
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              />

              {/* Marcador de ubicación actual */}
              <Marker
                position={[trackingData.current_location.lat, trackingData.current_location.lng]}
              />

              {/* Ruta si hay historial de ubicaciones */}
              {trackingData.location_history.length > 1 && (
                <Polyline
                  positions={trackingData.location_history.map(loc => [loc.lat, loc.lng])}
                  color="blue"
                  weight={3}
                />
              )}
            </MapContainer>
          </div>
        </div>
      )}

      {/* Timeline de eventos */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-4 border-b">
          <h3 className="font-medium">Historial de Seguimiento</h3>
        </div>
        <div className="p-4">
          <TrackingTimeline
            events={trackingData.tracking_events}
            showInternalEvents={userRole === 'SUPERUSER'}
          />
        </div>
      </div>

      {/* Información adicional para SUPERUSER/VENDOR */}
      {['SUPERUSER', 'VENDOR'].includes(userRole) && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b">
            <h3 className="font-medium">Información Adicional</h3>
          </div>
          <div className="p-4 space-y-4">
            {/* Intentos de entrega */}
            {trackingData.delivery_attempts.length > 0 && (
              <div>
                <h4 className="font-medium mb-2">Intentos de Entrega</h4>
                <div className="space-y-2">
                  {trackingData.delivery_attempts.map(attempt => (
                    <DeliveryAttemptCard
                      key={attempt.id}
                      attempt={attempt}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Acciones rápidas */}
            <div className="flex space-x-2">
              <Button
                onClick={() => openLocationUpdateModal()}
                icon={MapPin}
                size="sm"
              >
                Actualizar Ubicación
              </Button>
              <Button
                onClick={() => openDeliveryAttemptModal()}
                icon={Package}
                size="sm"
              >
                Registrar Entrega
              </Button>
              {userRole === 'SUPERUSER' && (
                <Button
                  onClick={() => openWorkflowEditor()}
                  icon={Settings}
                  size="sm"
                  variant="outline"
                >
                  Editar Workflow
                </Button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const TrackingTimeline = ({ events, showInternalEvents }) => {
  return (
    <div className="flow-root">
      <ul className="-mb-8">
        {events.map((event, index) => (
          <li key={event.id}>
            <div className="relative pb-8">
              {index !== events.length - 1 && (
                <span
                  className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                  aria-hidden="true"
                />
              )}
              <div className="relative flex space-x-3">
                <div>
                  <span className={`h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white ${getEventColor(event.event_type)}`}>
                    {getEventIcon(event.event_type)}
                  </span>
                </div>
                <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {event.event_description}
                    </p>
                    {event.location_address && (
                      <p className="text-sm text-gray-500">
                        📍 {event.location_address}
                      </p>
                    )}
                    {event.notes && (showInternalEvents || !event.is_internal) && (
                      <p className="text-sm text-gray-600 mt-1">
                        {event.notes}
                      </p>
                    )}
                  </div>
                  <div className="text-right text-sm whitespace-nowrap text-gray-500">
                    <time>{formatDateTime(event.created_at)}</time>
                    {event.recorded_by && (
                      <p className="text-xs">por {event.recorded_by_name}</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};
```

**Dependencies**: Map library (React Leaflet), Tracking service (nuevo)
**Specialist**: @frontend-react-specialist

### 3.12 OrderProcessingPanel Vendors (2h)
**Propósito**: Panel de procesamiento para vendors

```jsx
// frontend/src/components/vendor/OrderProcessingPanel.tsx
const OrderProcessingPanel = () => {
  const { user } = useAuthStore();
  const [orders, setOrders] = useState([]);
  const [metrics, setMetrics] = useState({});
  const [activeTab, setActiveTab] = useState('pending');

  return (
    <div className="space-y-6">
      {/* Métricas del vendor */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <VendorMetricCard
          title="Órdenes Pendientes"
          value={metrics.pendingOrders}
          icon={Clock}
          color="orange"
          action={() => setActiveTab('pending')}
        />
        <VendorMetricCard
          title="Para Enviar"
          value={metrics.readyToShip}
          icon={Package}
          color="blue"
          action={() => setActiveTab('ready')}
        />
        <VendorMetricCard
          title="En Tránsito"
          value={metrics.inTransit}
          icon={Truck}
          color="purple"
          action={() => setActiveTab('transit')}
        />
        <VendorMetricCard
          title="Completadas Hoy"
          value={metrics.completedToday}
          icon={CheckCircle}
          color="green"
        />
      </div>

      {/* Panel principal de órdenes */}
      <div className="bg-white rounded-lg shadow">
        <VendorOrderTabs
          activeTab={activeTab}
          onTabChange={setActiveTab}
          tabs={[
            { id: 'pending', name: 'Pendientes', count: metrics.pendingOrders },
            { id: 'ready', name: 'Listas para Enviar', count: metrics.readyToShip },
            { id: 'transit', name: 'En Tránsito', count: metrics.inTransit },
            { id: 'completed', name: 'Completadas', count: metrics.completed }
          ]}
        />

        <div className="p-6">
          {activeTab === 'pending' && (
            <PendingOrdersList
              orders={orders.filter(o => o.workflow_state === 'processing')}
              onProcessOrder={handleProcessOrder}
            />
          )}

          {activeTab === 'ready' && (
            <ReadyToShipOrdersList
              orders={orders.filter(o => o.workflow_state === 'ready_to_ship')}
              onShipOrder={handleShipOrder}
            />
          )}

          {activeTab === 'transit' && (
            <InTransitOrdersList
              orders={orders.filter(o => o.workflow_state === 'in_transit')}
              onUpdateTracking={handleUpdateTracking}
            />
          )}

          {activeTab === 'completed' && (
            <CompletedOrdersList
              orders={orders.filter(o => o.workflow_state === 'completed')}
            />
          )}
        </div>
      </div>

      {/* Modales */}
      <OrderProcessingModal />
      <ShippingLabelModal />
      <TrackingUpdateModal />
    </div>
  );
};

const PendingOrdersList = ({ orders, onProcessOrder }) => {
  return (
    <div className="space-y-4">
      {orders.map(order => (
        <div key={order.id} className="border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium">Orden #{order.order_number}</h4>
              <p className="text-sm text-gray-600">
                {order.items.length} items • {formatCurrency(order.total_amount)}
              </p>
              <p className="text-xs text-gray-500">
                Ordenado el {formatDate(order.created_at)}
              </p>
            </div>
            <div className="flex space-x-2">
              <Button
                size="sm"
                onClick={() => onProcessOrder(order.id, 'accept')}
              >
                Procesar
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => viewOrderDetails(order.id)}
              >
                Ver Detalles
              </Button>
            </div>
          </div>

          {/* Items de la orden */}
          <div className="mt-3 border-t pt-3">
            <div className="space-y-2">
              {order.items.map(item => (
                <div key={item.id} className="flex items-center justify-between text-sm">
                  <div className="flex items-center space-x-3">
                    <img
                      src={item.product.image_url}
                      alt={item.product.name}
                      className="w-8 h-8 rounded object-cover"
                    />
                    <span>{item.product.name}</span>
                    <span className="text-gray-500">x{item.quantity}</span>
                  </div>
                  <span className="font-medium">
                    {formatCurrency(item.total_price)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
```

**Dependencies**: Vendor-specific order service, UI components ✅
**Specialist**: @frontend-react-specialist

### 3.13 OrderAnalyticsCharts (2h)
**Propósito**: Visualización de analytics de órdenes

```jsx
// frontend/src/components/analytics/OrderAnalyticsCharts.tsx
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';

const OrderAnalyticsCharts = ({ userRole, vendorId = null }) => {
  const [analyticsData, setAnalyticsData] = useState({});
  const [timeframe, setTimeframe] = useState('30d');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, [timeframe, vendorId]);

  const loadAnalytics = async () => {
    const endpoint = userRole === 'SUPERUSER'
      ? '/api/v1/superuser/orders/analytics'
      : `/api/v1/vendor/orders/analytics`;

    const data = await orderService.getAnalytics({
      period: timeframe,
      vendor_id: vendorId
    });

    setAnalyticsData(data);
    setLoading(false);
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="space-y-8">
      {/* Controles de tiempo */}
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">Analytics de Órdenes</h2>
        <TimeframeSelector
          value={timeframe}
          onChange={setTimeframe}
          options={[
            { value: '7d', label: '7 días' },
            { value: '30d', label: '30 días' },
            { value: '90d', label: '3 meses' },
            { value: '1y', label: '1 año' }
          ]}
        />
      </div>

      {/* Revenue Chart */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium mb-4">Revenue por Período</h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={analyticsData.revenue_timeline}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip formatter={(value) => formatCurrency(value)} />
            <Legend />
            <Area
              type="monotone"
              dataKey="revenue"
              stroke="#3B82F6"
              fill="#3B82F6"
              fillOpacity={0.3}
              name="Revenue"
            />
            <Area
              type="monotone"
              dataKey="commission"
              stroke="#10B981"
              fill="#10B981"
              fillOpacity={0.3}
              name="Comisión"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Orders Volume */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium mb-4">Volumen de Órdenes</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={analyticsData.orders_volume}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="total_orders" fill="#3B82F6" name="Total" />
              <Bar dataKey="completed_orders" fill="#10B981" name="Completadas" />
              <Bar dataKey="cancelled_orders" fill="#EF4444" name="Canceladas" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Order Status Distribution */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium mb-4">Distribución de Estados</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={analyticsData.status_distribution}
                cx="50%"
                cy="50%"
                outerRadius={80}
                fill="#8884d8"
                dataKey="count"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {analyticsData.status_distribution?.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getStatusColor(entry.status)} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium mb-4">Métricas de Performance</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Processing Time */}
          <div>
            <h4 className="font-medium mb-2">Tiempo de Procesamiento</h4>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={analyticsData.processing_time}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip formatter={(value) => `${value} horas`} />
                <Line
                  type="monotone"
                  dataKey="avg_processing_time"
                  stroke="#8B5CF6"
                  strokeWidth={2}
                  name="Tiempo Promedio"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Delivery Performance */}
          <div>
            <h4 className="font-medium mb-2">Performance de Entrega</h4>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={analyticsData.delivery_performance}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip formatter={(value) => `${value}%`} />
                <Area
                  type="monotone"
                  dataKey="on_time_rate"
                  stroke="#10B981"
                  fill="#10B981"
                  fillOpacity={0.3}
                  name="Entregas a Tiempo"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Top Products/Vendors - Solo para SUPERUSER */}
      {userRole === 'SUPERUSER' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium mb-4">Top Productos</h3>
            <div className="space-y-3">
              {analyticsData.top_products?.map((product, index) => (
                <div key={product.id} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span className="font-medium text-gray-500">#{index + 1}</span>
                    <span>{product.name}</span>
                  </div>
                  <div className="text-right">
                    <span className="font-medium">{product.order_count} órdenes</span>
                    <p className="text-sm text-gray-500">
                      {formatCurrency(product.revenue)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium mb-4">Top Vendedores</h3>
            <div className="space-y-3">
              {analyticsData.top_vendors?.map((vendor, index) => (
                <div key={vendor.id} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span className="font-medium text-gray-500">#{index + 1}</span>
                    <span>{vendor.name}</span>
                  </div>
                  <div className="text-right">
                    <span className="font-medium">{vendor.order_count} órdenes</span>
                    <p className="text-sm text-gray-500">
                      {formatCurrency(vendor.revenue)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
```

**Dependencies**: Chart library (Recharts), Analytics service
**Specialist**: @frontend-react-specialist

---

## 📊 INTEGRACIÓN CON SISTEMA BASE

### Compatible con TODO_CONFIGURACION_BASE_ENTERPRISE.md:
✅ **Database Architecture**: Extiende Order model existente manteniendo compatibilidad
✅ **Auth System**: Integra con RBAC existente, respeta permisos por rol
✅ **API Structure**: Sigue convención `/api/v1/` con nuevos endpoints enterprise
✅ **Frontend Architecture**: Usa stores existentes y component architecture
✅ **Error Handling**: Compatible con error hierarchy existente

### APIs que conectan con otros módulos:
- `GET /api/v1/orders/{order_id}/user` → Módulo Users
- `GET /api/v1/orders/{order_id}/products` → Módulo Products
- `POST /api/v1/payments/orders/{order_id}/process` → Módulo Payments
- `POST /api/v1/notifications/orders/{order_id}/status` → Módulo Notifications
- `GET /api/v1/analytics/orders/{order_id}/metrics` → Módulo Analytics

---

## ✅ TESTING & VALIDATION

### Tests Backend (qa-engineer-pytest):
```python
def test_superuser_can_manage_all_orders():
    """SUPERUSER debe poder gestionar órdenes de todos los vendors"""
    pass

def test_vendor_can_only_manage_own_orders():
    """Vendor solo puede gestionar sus propias órdenes"""
    pass

def test_order_workflow_transitions():
    """Workflow de órdenes funciona correctamente"""
    pass

def test_gps_tracking_updates():
    """Sistema de tracking GPS funciona"""
    pass
```

### Tests Frontend:
```typescript
describe('OrderManagementDashboard', () => {
  test('SUPERUSER sees all orders', () => {});
  test('Vendor sees only own orders', () => {});
  test('Order tracking works correctly', () => {});
});
```

---

## 🎯 CRITERIOS DE ÉXITO

### Funcionalidades Críticas:
- [ ] SUPERUSER controla todas las órdenes de todos los vendors
- [ ] Workflow completo funcional con estados avanzados
- [ ] Sistema de tracking GPS operativo
- [ ] Gestión de disputas y reembolsos funcional
- [ ] Analytics completo con visualizaciones
- [ ] Operaciones masivas para SUPERUSER

### Integration Success:
- [ ] Compatible con Products y Users modules
- [ ] APIs integradas con Payment system
- [ ] Frontend usa architecture base existente
- [ ] Preparado para AI agents (futuro)

---

**🔗 MÓDULO COMPATIBLE CON ENTERPRISE BASE**
**🏪 SISTEMA COMPLETO DE ÓRDENES ENTERPRISE**
**⏱️ 22 HORAS IMPLEMENTACIÓN COORDINADA**