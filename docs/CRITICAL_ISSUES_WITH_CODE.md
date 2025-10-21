# PROBLEMAS CRÍTICOS ENCONTRADOS - DETALLES CON CÓDIGO

## 1. BackgroundTasks puede ser None en approve-seller

**Ubicación**: `/home/admin-jairo/MeStore/app/api/v1/endpoints/auth.py` líneas 2232-2318

**Código problemático**:
```python
@router.post("/admin/approve-seller/{user_id}", response_model=dict, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def approve_seller(
    user_id: str,
    request: Request,
    current_user: User = Depends(get_current_user_clean),
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = None  # ❌ PROBLEMA: PARÁMETRO OPCIONAL
) -> dict:
    ...
    # Enviar email de aprobación (background)
    if background_tasks:  # ❌ PUEDE SER NONE PERMITIENDO SALTAR ENVÍO DE EMAIL
        email_service = EmailService()
        seller_name = seller.nombre or seller.razon_social or "Vendedor"
        background_tasks.add_task(
            email_service.send_approval_email,
            seller.email,
            seller_name
        )
        logger.info(f"📧 Email de aprobación programado")
```

**Problema**:
- FastAPI no inyecta BackgroundTasks si no está en Depends()
- Si es None, el vendedor es aprobado pero NO recibe email
- Falta notificación crítica al usuario

**Solución**:
```python
from fastapi import BackgroundTasks, Depends

async def approve_seller(
    user_id: str,
    request: Request,
    current_user: User = Depends(get_current_user_clean),
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = Depends()  # ✅ REQUERIDO
) -> dict:
    ...
    # Ahora background_tasks SIEMPRE está disponible
    email_service = EmailService()
    seller_name = seller.nombre or seller.razon_social or "Vendedor"
    background_tasks.add_task(
        email_service.send_approval_email,
        seller.email,
        seller_name
    )
```

---

## 2. reject-seller usa dict en lugar de Pydantic model

**Ubicación**: `/home/admin-jairo/MeStore/app/api/v1/endpoints/auth.py` líneas 2337-2383

**Código problemático**:
```python
@router.post("/admin/reject-seller/{user_id}", response_model=dict, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def reject_seller(
    user_id: str,
    rejection_data: dict,  # ❌ PROBLEMA: dict SIN VALIDACIÓN PYDANTIC
    request: Request,
    current_user: User = Depends(get_current_user_clean),
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = None
) -> dict:
    try:
        reason = rejection_data.get("reason", "").strip()  # ❌ PUEDE FALLAR SI CLAVE NO EXISTE

        if not reason or len(reason) < 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La razón del rechazo debe tener al menos 20 caracteres"
            )

        # 🔒 SECURITY: Validate against dangerous patterns to prevent XSS
        dangerous_patterns = ['<script', 'javascript:', 'onerror=', 'onload=', 'onclick=', '<iframe']
        reason_lower = reason.lower()
        for pattern in dangerous_patterns:
            if pattern in reason_lower:  # ❌ VALIDACIÓN MANUAL SIN SCHEMA
                logger.warning(...)
                raise HTTPException(...)
```

**Problemas**:
- Sin schema Pydantic, no hay validación automática de OpenAPI
- Documentación Swagger incorrecta
- Cliente no sabe qué campos esperar
- Validaciones duplicadas en lugar de reutilizables
- Sin ejemplos en documentación

**Solución**:
```python
from pydantic import BaseModel, Field

class VendorRejectionRequest(BaseModel):
    """Schema para rechazo de vendedor"""
    reason: str = Field(
        ...,
        min_length=20,
        max_length=1000,
        description="Razón del rechazo (20-1000 caracteres)"
    )

    @field_validator('reason')
    @classmethod
    def validate_reason_no_xss(cls, v):
        """Prevenir XSS en razón de rechazo"""
        dangerous_patterns = ['<script', 'javascript:', 'onerror=', 'onload=', 'onclick=', '<iframe']
        reason_lower = v.lower()
        for pattern in dangerous_patterns:
            if pattern in reason_lower:
                raise ValueError(f"Razón contiene patrón no permitido: {pattern}")
        return v

@router.post("/admin/reject-seller/{user_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def reject_seller(
    user_id: str,
    rejection_data: VendorRejectionRequest,  # ✅ SCHEMA VALIDADO
    request: Request,
    current_user: User = Depends(get_current_user_clean),
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = Depends()
) -> dict:
    reason = rejection_data.reason  # ✅ YA VALIDADO AUTOMÁTICAMENTE
    
    # Resto del código sin validación manual
    seller.vendor_status = VendorStatus.REJECTED
    seller.rejection_reason = reason
    ...
```

---

## 3. Rate limiting SMS sin fallback (requiere Redis)

**Ubicación**: `/home/admin-jairo/MeStore/app/services/sms_service.py` líneas 74-102

**Código problemático**:
```python
def _check_rate_limit(self, phone_number: str) -> Tuple[bool, str]:
    """
    Verifica si el número ha excedido el rate limit.
    """
    if not self.redis_service:  # ❌ SI NO HAY REDIS, SKIPS RATE LIMIT
        return True, "Rate limiting disabled"

    try:
        rate_limit_key = f"sms_rate_limit:{phone_number}"
        current_count = self.redis_service.get(rate_limit_key)

        if current_count is None:
            current_count = 0
        else:
            current_count = int(current_count)

        if current_count >= self.rate_limit_per_number:
            return False, f"Rate limit excedido. Máximo {self.rate_limit_per_number} SMS por hora"

        return True, "Within rate limit"
    except Exception as e:
        logger.error(f"Error verificando rate limit: {str(e)}")
        return True, "Rate limit check failed, allowing"  # ❌ FAIL-OPEN: PERMITE SPAM
```

**Problemas**:
- Sin Redis, se permite un número ilimitado de SMS
- En desarrollo sin Redis = vulnerabilidad de spam
- Exception catch silencia errores
- "Fail-open" permite ataques

**Solución**:
```python
# Agregar fallback a database rate limiting
from sqlalchemy import select, and_
from datetime import datetime, timedelta

async def _check_rate_limit_with_db_fallback(
    self, 
    db: AsyncSession,
    phone_number: str
) -> Tuple[bool, str]:
    """Check rate limit con fallback a database si Redis no está disponible"""
    
    # Intentar con Redis primero (más rápido)
    if self.redis_service:
        try:
            rate_limit_key = f"sms_rate_limit:{phone_number}"
            current_count = self.redis_service.get(rate_limit_key)
            
            if current_count is None:
                current_count = 0
            else:
                current_count = int(current_count)
            
            if current_count >= self.rate_limit_per_number:
                return False, f"Rate limit excedido. Máximo {self.rate_limit_per_number} SMS por hora"
            
            return True, "Within rate limit"
        except Exception as e:
            logger.warning(f"Redis rate limit check failed, falling back to DB: {str(e)}")
    
    # Fallback a database
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    
    # Contar SMS enviados a este número en la última hora
    # Asumiendo tabla sms_logs con timestamp y phone_number
    result = await db.execute(
        select(func.count(SMSLog.id)).where(
            and_(
                SMSLog.phone_number == phone_number,
                SMSLog.created_at >= one_hour_ago
            )
        )
    )
    sms_count = result.scalar() or 0
    
    if sms_count >= self.rate_limit_per_number:
        return False, f"Rate limit excedido. Máximo {self.rate_limit_per_number} SMS por hora"
    
    return True, "Within rate limit (DB fallback)"
```

---

## 4. Falta endpoint para verificación de documentos por admin

**Ubicación**: `/home/admin-jairo/MeStore/app/models/vendor_document.py` líneas 35-36

**Problema**:
```python
status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)
verified_by = Column(String(36), ForeignKey("users.id"), nullable=True)
verification_notes = Column(Text, nullable=True)
# ❌ NO HAY ENDPOINT PARA QUE ADMIN CAMBIE ESTOS CAMPOS
```

**Impacto**:
- Admin puede ver documentos pero NO puede marcar como verificados
- vendor_status queda en PENDING_DOCUMENTS indefinidamente
- Flujo de aprobación incompleto para personas jurídicas

**Solución**:
```python
@router.put("/vendedores/documents/{doc_id}/verify", response_model=dict)
async def verify_vendor_document(
    doc_id: str,
    verification_data: dict,  # {"status": "verified|rejected", "notes": "..."}
    current_user: User = Depends(get_current_user_clean),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Admin verifica documento de vendor"""
    
    # Validar que es admin
    if current_user.user_type not in [UserType.ADMIN, UserType.SUPERUSER, UserType.OWNER]:
        raise HTTPException(status_code=403, detail="Admin requerido")
    
    # Obtener documento
    doc = await db.execute(
        select(VendorDocument).where(VendorDocument.id == doc_id)
    )
    document = doc.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    # Actualizar estado
    document.status = verification_data.get("status")  # verified|rejected
    document.verified_by = current_user.id
    document.verification_notes = verification_data.get("notes")
    document.verified_at = datetime.utcnow()
    
    await db.commit()
    
    # Si TODOS los documentos están verificados, cambiar vendor_status
    vendor = document.vendor
    all_verified = all(
        d.status == DocumentStatus.VERIFIED 
        for d in vendor.vendor_documents
    )
    
    if all_verified:
        vendor.vendor_status = VendorStatus.PENDING_APPROVAL
        await db.commit()
    
    return {"success": True, "document_id": doc_id, "status": document.status}
```

---

## 5. Falta validación de transiciones de estado

**Ubicación**: Todos los endpoints que cambian vendor_status

**Problema**:
```python
# En approve_seller (línea 2301)
seller.vendor_status = VendorStatus.APPROVED  # ❌ SIN VALIDAR ESTADO ANTERIOR

# En register_multi_type (línea 1952)
vendor_status = VendorStatus.DRAFT if is_natural else VendorStatus.PENDING_DOCUMENTS
# ❌ PERO PUEDE SER APROBADO ANTES CON ADMIN QUE LO CAMBIA A DRAFT?
```

**Impacto**:
- Estados inválidos: APPROVED → DRAFT → APPROVED
- Inconsistencia en base de datos
- Auditoría confusa

**Solución**:
```python
class VendorStatusTransition:
    """Define transiciones válidas de vendor_status"""
    
    VALID_TRANSITIONS = {
        VendorStatus.DRAFT: [
            VendorStatus.PENDING_APPROVAL,
            VendorStatus.REJECTED
        ],
        VendorStatus.PENDING_DOCUMENTS: [
            VendorStatus.PENDING_APPROVAL,
            VendorStatus.REJECTED
        ],
        VendorStatus.PENDING_APPROVAL: [
            VendorStatus.APPROVED,
            VendorStatus.REJECTED
        ],
        VendorStatus.APPROVED: [
            VendorStatus.SUSPENDED,
            VendorStatus.DELETED
        ],
        VendorStatus.REJECTED: [
            VendorStatus.DRAFT  # Permite re-aplicar
        ]
    }
    
    @staticmethod
    def is_valid(current_status: VendorStatus, new_status: VendorStatus) -> bool:
        """Valida si la transición es permitida"""
        if current_status not in VendorStatusTransition.VALID_TRANSITIONS:
            return False
        return new_status in VendorStatusTransition.VALID_TRANSITIONS[current_status]
    
    @staticmethod
    def validate_or_raise(current_status: VendorStatus, new_status: VendorStatus):
        """Valida y lanza excepción si inválida"""
        if not VendorStatusTransition.is_valid(current_status, new_status):
            raise ValueError(
                f"Transición inválida: {current_status} → {new_status}. "
                f"Transiciones válidas: {VendorStatusTransition.VALID_TRANSITIONS.get(current_status, [])}"
            )

# Usar en endpoints:
async def approve_seller(user_id: str, ...):
    ...
    seller = ...  # Obtener vendor
    
    # Validar transición
    VendorStatusTransition.validate_or_raise(
        seller.vendor_status,
        VendorStatus.APPROVED
    )
    
    seller.vendor_status = VendorStatus.APPROVED
    ...
```

---

## RESUMEN DE ACCIONES INMEDIATAS

1. **URGENTE (Hoy)**: Arreglar BackgroundTasks en approve-seller
2. **URGENTE (Hoy)**: Crear VendorRejectionRequest schema
3. **IMPORTANTE (Esta semana)**: Implementar endpoint de verificación de documentos
4. **IMPORTANTE (Esta semana)**: Implementar state machine para transiciones
5. **IMPORTANTE (Esta semana)**: Rate limiting fallback con DB

