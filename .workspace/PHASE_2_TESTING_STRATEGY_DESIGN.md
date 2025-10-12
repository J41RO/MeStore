# FASE 2 - DISEÑO DE ESTRATEGIA DE TESTING SMS SECURITY

**Fecha**: 2025-10-11
**Agente**: TDD Specialist AI
**Fase**: Análisis y Diseño (NO IMPLEMENTACIÓN)
**Status**: ANÁLISIS COMPLETO
**Referencia**: `.workspace/PHASE_1_SECURITY_IMPLEMENTATION.md`

---

## EXECUTIVE SUMMARY

Este documento presenta el análisis completo del código implementado en Fase 1 y diseña la estrategia integral de testing unitario e integración para el módulo `app/core/sms_security.py` y endpoint `/send-sms-public`.

**Módulo Analizado**: `app/core/sms_security.py` (385 líneas, 5 funciones públicas + 1 helper privada)
**Endpoint Securizado**: `/api/v1/auth/send-sms-public` (líneas 750-920 de auth.py)
**Cobertura Target**: >75% (mínimo proyecto) → 90%+ (target para código crítico de seguridad)
**Tests Estimados**: 25+ test cases (15 unitarios + 10+ integración)

---

## 1. ANÁLISIS DE CÓDIGO IMPLEMENTADO

### 1.1 Módulo `app/core/sms_security.py`

#### Funciones Públicas Identificadas:

| # | Función | LOC | Complejidad | Dependencias | Tipo |
|---|---------|-----|-------------|--------------|------|
| 1 | `check_phone_rate_limit()` | 35 | MEDIA | Redis async | async |
| 2 | `check_ip_rate_limit()` | 35 | MEDIA | Redis async | async |
| 3 | `validate_phone_number()` | 39 | ALTA | phonenumbers lib | sync |
| 4 | `get_client_ip()` | 19 | BAJA | FastAPI Request | sync |
| 5 | `log_sms_security_event()` | 22 | BAJA | logging | sync |
| 6 | `_hash_phone()` (helper) | 3 | BAJA | hashlib | sync |

**Total LOC**: 153 (de 385 totales)
**Documentación**: 232 líneas (60% del archivo son docstrings/comments)

#### Características Críticas:
- **Fail-open design**: Las funciones de rate limiting NO fallan el request si Redis está caído
- **Atomicidad**: Operaciones Redis son atómicas (incr, setex)
- **GDPR Compliance**: Teléfonos hasheados con SHA256
- **Logging estructurado**: JSON logs con metadata completa
- **Validación internacional**: Soporte para E.164 estándar

### 1.2 Endpoint `/send-sms-public`

**Ubicación**: `app/api/v1/endpoints/auth.py` líneas 750-920
**Tipo**: Endpoint público (sin autenticación JWT)
**Complejidad**: ALTA (4 capas de seguridad secuenciales)

#### Flujo de Ejecución:
```
1. Extracción IP → get_client_ip(request)
2. Rate Limit IP → check_ip_rate_limit(redis, ip) [10/hour]
3. Validación Teléfono → validate_phone_number(phone) [E.164]
4. Rate Limit Teléfono → check_phone_rate_limit(redis, phone) [3/10min]
5. Lógica SMS → SMSService.send_verification_code() [Twilio]
6. Logging → log_sms_security_event()
```

**Total de Exit Points**: 8 (5 HTTPExceptions + 3 success paths)

### 1.3 Dependencias Externas

| Dependencia | Tipo | Versión | Mock Requerido | Fixture Disponible |
|-------------|------|---------|----------------|-------------------|
| **RedisService** | Internal | - | SÍ | `mock_redis_for_testing` ✅ |
| **phonenumbers** | External | 8.13.0+ | NO (library test) | Ninguna |
| **FastAPI Request** | Framework | - | SÍ | Crear nueva fixture |
| **SMSService** | Internal | - | SÍ | Ninguna (crear) |
| **Logger** | Built-in | - | SÍ (caplog) | pytest caplog ✅ |

### 1.4 Análisis de `tests/conftest.py`

#### Fixtures Existentes Relevantes:

**✅ DISPONIBLES Y UTILIZABLES:**
```python
- async_session              # AsyncSession de SQLAlchemy (línea 220)
- async_client               # AsyncClient de HTTPX (línea 47)
- mock_redis_for_testing     # Mock de Redis (línea 293) → CRÍTICO
- test_vendor_user           # Usuario vendor (línea 328)
- test_buyer_user            # Usuario buyer (línea 376)
```

**⚠️ NECESARIAS (CREAR NUEVAS):**
```python
- mock_request               # Mock de FastAPI Request con headers
- mock_redis_service         # Mock específico de RedisService
- mock_sms_service_success   # Mock de SMSService (success)
- mock_sms_service_fail      # Mock de SMSService (failure)
```

#### Patrón de Tests Actual:
- **Markers**: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.auth`
- **Async Support**: pytest-asyncio configurado ✅
- **Database**: SQLite in-memory con isolation ✅
- **Coverage**: `.coveragerc` configurado (75% mínimo) ✅

---

## 2. ESTRATEGIA DE TESTING DISEÑADA

### 2.1 Tests Unitarios (Archivo: `tests/unit/test_sms_security.py`)

#### Test 1: `check_phone_rate_limit()` - 6 test cases

**Test Case 1.1: Primera solicitud (debe permitir)**
```python
@pytest.mark.unit
@pytest.mark.asyncio
async def test_check_phone_rate_limit_first_attempt():
    """Primera solicitud debe ser permitida y crear contador en Redis"""
    # Setup
    mock_redis = AsyncMock()
    mock_redis.cache_get.return_value = None  # No existe key
    mock_redis.cache_set.return_value = True

    # Execute
    allowed, message = await check_phone_rate_limit(mock_redis, "+573001234567")

    # Assert
    assert allowed is True
    assert message == "OK"
    mock_redis.cache_set.assert_called_once_with(
        "sms_rate_limit:phone:+573001234567",
        "1",
        expire=600  # 10 minutos
    )
```

**Estimación**: Desarrollo 10 min | Debugging 5 min | **Total: 15 min**

---

**Test Case 1.2: Segunda solicitud (debe permitir)**
```python
@pytest.mark.unit
@pytest.mark.asyncio
async def test_check_phone_rate_limit_second_attempt():
    """Segunda solicitud debe incrementar contador y permitir"""
    mock_redis = AsyncMock()
    mock_redis.cache_get.return_value = "1"  # Ya hay 1 intento
    mock_redis.redis.incr.return_value = 2

    allowed, message = await check_phone_rate_limit(mock_redis, "+573001234567")

    assert allowed is True
    assert message == "OK"
    mock_redis.redis.incr.assert_called_once()
```

**Estimación**: 10 min

---

**Test Case 1.3: Tercer solicitud (debe permitir - límite no alcanzado)**
```python
@pytest.mark.unit
@pytest.mark.asyncio
async def test_check_phone_rate_limit_third_attempt():
    """Tercer intento debe ser el último permitido"""
    mock_redis = AsyncMock()
    mock_redis.cache_get.return_value = "2"  # Ya hay 2 intentos
    mock_redis.redis.incr.return_value = 3

    allowed, message = await check_phone_rate_limit(mock_redis, "+573001234567")

    assert allowed is True
    assert message == "OK"
```

**Estimación**: 10 min

---

**Test Case 1.4: Cuarto solicitud (debe bloquear con 429)**
```python
@pytest.mark.unit
@pytest.mark.asyncio
async def test_check_phone_rate_limit_exceeded():
    """Cuarto intento debe ser bloqueado por rate limit"""
    mock_redis = AsyncMock()
    mock_redis.cache_get.return_value = "3"  # Ya llegó al límite

    allowed, message = await check_phone_rate_limit(mock_redis, "+573001234567")

    assert allowed is False
    assert "Demasiados intentos" in message
    assert "3 intentos en 10 minutos" in message
    # NO debe incrementar si ya está al límite
    mock_redis.redis.incr.assert_not_called()
```

**Estimación**: 15 min (validación mensaje español)

---

**Test Case 1.5: Redis falla (debe fail-open)**
```python
@pytest.mark.unit
@pytest.mark.asyncio
async def test_check_phone_rate_limit_redis_failure_fail_open():
    """Si Redis falla, debe permitir (fail-open security)"""
    mock_redis = AsyncMock()
    mock_redis.cache_get.side_effect = Exception("Redis connection lost")

    allowed, message = await check_phone_rate_limit(mock_redis, "+573001234567")

    assert allowed is True  # CRÍTICO: fail-open
    assert message == "OK"
```

**Estimación**: 15 min (test crítico de seguridad)

---

**Test Case 1.6: Verificar TTL correcto (600 segundos)**
```python
@pytest.mark.unit
@pytest.mark.asyncio
async def test_check_phone_rate_limit_correct_ttl():
    """Verificar que el TTL sea exactamente 600 segundos (10 minutos)"""
    mock_redis = AsyncMock()
    mock_redis.cache_get.return_value = None

    await check_phone_rate_limit(mock_redis, "+573001234567")

    # Validar que expire sea 600
    call_args = mock_redis.cache_set.call_args
    assert call_args[1]['expire'] == 600  # Kwargs verification
```

**Estimación**: 10 min

**Subtotal Test 1**: 6 casos × ~12 min promedio = **75 minutos**
**Prioridad**: CRÍTICA
**Markers**: `@pytest.mark.unit, @pytest.mark.sms_security, @pytest.mark.rate_limit`

---

#### Test 2: `check_ip_rate_limit()` - 5 test cases

**Casos Similares a Test 1 pero con diferencias:**
- Límite: 10 intentos (vs 3)
- TTL: 3600 segundos (vs 600)
- Mensaje: "red" (vs "teléfono")

**Test Cases**:
1. Primera solicitud (permite)
2. Décima solicitud (permite - última)
3. Onceava solicitud (bloquea)
4. Redis falla (fail-open)
5. Verificar TTL correcto (3600)

**Estimación**: 5 casos × 10 min = **50 minutos**
**Prioridad**: CRÍTICA
**Markers**: `@pytest.mark.unit, @pytest.mark.sms_security, @pytest.mark.rate_limit`

---

#### Test 3: `validate_phone_number()` - 10 test cases

**Características**:
- NO requiere mocking (phonenumbers es librería estable)
- Función síncrona (sin async)
- Alta cobertura de casos edge

**Test Case 3.1: Número colombiano móvil válido**
```python
@pytest.mark.unit
def test_validate_phone_number_colombia_mobile_valid():
    """Validar número móvil colombiano en formato E.164"""
    valid, message, e164 = validate_phone_number("+573001234567")

    assert valid is True
    assert message == "OK"
    assert e164 == "+573001234567"
```

**Test Case 3.2: Número USA móvil válido**
```python
@pytest.mark.unit
def test_validate_phone_number_usa_mobile_valid():
    """Validar número móvil USA en formato E.164"""
    valid, message, e164 = validate_phone_number("+17379771943")

    assert valid is True
    assert message == "OK"
    assert e164.startswith("+1")
    assert len(e164) == 12  # +1 + 10 dígitos
```

**Test Case 3.3: Sin código país (inválido)**
```python
@pytest.mark.unit
def test_validate_phone_number_missing_country_code():
    """Rechazar número sin + y código país"""
    valid, message, e164 = validate_phone_number("3001234567")

    assert valid is False
    assert "Formato telefónico inválido" in message
    assert "código_país" in message
    assert e164 == ""
```

**Test Case 3.4: Número muy corto (inválido)**
```python
@pytest.mark.unit
def test_validate_phone_number_too_short():
    """Rechazar número muy corto"""
    valid, message, e164 = validate_phone_number("+123")

    assert valid is False
    assert "inválido" in message.lower()
    assert e164 == ""
```

**Test Case 3.5: Número fijo/landline (inválido)**
```python
@pytest.mark.unit
def test_validate_phone_number_landline_rejected():
    """Rechazar teléfono fijo (solo móviles aceptados)"""
    # +57 1 2345678 → Número fijo Bogotá
    valid, message, e164 = validate_phone_number("+5712345678")

    assert valid is False
    assert "móvil" in message.lower()
    assert e164 == ""
```

**Test Case 3.6-3.10**: Casos adicionales
- Número internacional válido (México +52)
- Número con caracteres inválidos ("+573-00-123-456")
- Número muy largo (+999...)
- Número con espacios ("+57 300 123 4567")
- Código país no existente (+9999)

**Estimación**: 10 casos × 8 min = **80 minutos**
**Prioridad**: ALTA
**Markers**: `@pytest.mark.unit, @pytest.mark.sms_security, @pytest.mark.phone_validation`

---

#### Test 4: `get_client_ip()` - 5 test cases

**Test Case 4.1: X-Forwarded-For con múltiples IPs**
```python
@pytest.mark.unit
def test_get_client_ip_x_forwarded_for_multiple():
    """Extraer primera IP de X-Forwarded-For chain"""
    from unittest.mock import Mock

    mock_request = Mock()
    mock_request.headers = {
        "X-Forwarded-For": "203.0.113.1, 198.51.100.2, 192.168.1.1"
    }

    ip = get_client_ip(mock_request)

    assert ip == "203.0.113.1"  # Primera IP del chain
```

**Test Case 4.2: X-Forwarded-For con una IP**
```python
@pytest.mark.unit
def test_get_client_ip_x_forwarded_for_single():
    """Extraer IP de X-Forwarded-For con single IP"""
    mock_request = Mock()
    mock_request.headers = {"X-Forwarded-For": "203.0.113.1"}

    ip = get_client_ip(mock_request)

    assert ip == "203.0.113.1"
```

**Test Case 4.3: X-Real-IP header**
```python
@pytest.mark.unit
def test_get_client_ip_x_real_ip():
    """Usar X-Real-IP si no hay X-Forwarded-For"""
    mock_request = Mock()
    mock_request.headers = {"X-Real-IP": "198.51.100.5"}

    ip = get_client_ip(mock_request)

    assert ip == "198.51.100.5"
```

**Test Case 4.4: Sin headers (conexión directa)**
```python
@pytest.mark.unit
def test_get_client_ip_direct_connection():
    """Usar request.client.host si no hay proxy headers"""
    mock_request = Mock()
    mock_request.headers = {}
    mock_request.client.host = "192.168.1.100"

    ip = get_client_ip(mock_request)

    assert ip == "192.168.1.100"
```

**Test Case 4.5: request.client es None**
```python
@pytest.mark.unit
def test_get_client_ip_no_client_object():
    """Retornar 'unknown' si request.client es None"""
    mock_request = Mock()
    mock_request.headers = {}
    mock_request.client = None

    ip = get_client_ip(mock_request)

    assert ip == "unknown"
```

**Estimación**: 5 casos × 10 min = **50 minutos**
**Prioridad**: MEDIA
**Markers**: `@pytest.mark.unit, @pytest.mark.sms_security`

---

#### Test 5: `log_sms_security_event()` - 4 test cases

**Test Case 5.1: Evento exitoso (INFO level)**
```python
@pytest.mark.unit
def test_log_sms_security_event_success(caplog):
    """Log exitoso debe usar logger.info con datos estructurados"""
    import logging
    caplog.set_level(logging.INFO)

    log_sms_security_event(
        event_type="sms_sent",
        phone="+573001234567",
        ip="203.0.113.1",
        success=True,
        extra={"twilio_sid": "SM123"}
    )

    # Verificar log record
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelname == "INFO"
    assert "sms_sent" in record.message
    assert "twilio_sid" in str(record.extra)
```

**Test Case 5.2: Evento fallido (WARNING level)**
```python
@pytest.mark.unit
def test_log_sms_security_event_failure(caplog):
    """Log fallido debe usar logger.warning"""
    import logging
    caplog.set_level(logging.WARNING)

    log_sms_security_event(
        event_type="rate_limit_phone",
        phone="+573001234567",
        ip="203.0.113.1",
        success=False,
        reason="Rate limit exceeded"
    )

    record = caplog.records[0]
    assert record.levelname == "WARNING"
    assert "FAILED" in record.message
```

**Test Case 5.3: Verificar hashing SHA256 del teléfono**
```python
@pytest.mark.unit
def test_log_sms_security_event_phone_hashing(caplog):
    """Teléfono debe ser hasheado con SHA256 (GDPR)"""
    import hashlib

    phone = "+573001234567"
    expected_hash = hashlib.sha256(phone.encode()).hexdigest()[:16]

    log_sms_security_event(
        event_type="sms_sent",
        phone=phone,
        ip="203.0.113.1",
        success=True
    )

    record = caplog.records[0]
    # El hash debe estar en extra data
    assert expected_hash in str(record.extra)
    # El teléfono original NO debe estar en logs
    assert phone not in record.message
```

**Test Case 5.4: Verificar estructura JSON completa**
```python
@pytest.mark.unit
def test_log_sms_security_event_json_structure(caplog):
    """Verificar que log_data tenga estructura JSON completa"""
    log_sms_security_event(
        event_type="sms_sent",
        phone="+573001234567",
        ip="203.0.113.1",
        success=True,
        reason="Test reason",
        extra={"custom_field": "value"}
    )

    record = caplog.records[0]
    log_extra = record.extra

    # Verificar campos obligatorios
    assert "timestamp" in str(log_extra)
    assert "event" in str(log_extra)
    assert "phone_hash" in str(log_extra)
    assert "ip" in str(log_extra)
    assert "success" in str(log_extra)
    assert "reason" in str(log_extra)
    assert "custom_field" in str(log_extra)
```

**Estimación**: 4 casos × 12 min = **48 minutos**
**Prioridad**: MEDIA (logging no crítico)
**Markers**: `@pytest.mark.unit, @pytest.mark.sms_security, @pytest.mark.logging`

---

### 2.2 Resumen Tests Unitarios

| Función | Test Cases | Tiempo Est. | Prioridad | Markers |
|---------|------------|-------------|-----------|---------|
| `check_phone_rate_limit()` | 6 | 75 min | CRÍTICA | unit, rate_limit |
| `check_ip_rate_limit()` | 5 | 50 min | CRÍTICA | unit, rate_limit |
| `validate_phone_number()` | 10 | 80 min | ALTA | unit, phone_validation |
| `get_client_ip()` | 5 | 50 min | MEDIA | unit |
| `log_sms_security_event()` | 4 | 48 min | MEDIA | unit, logging |
| **TOTAL UNITARIOS** | **30** | **303 min** (~5 horas) | - | - |

**Cobertura Esperada**: 95%+ del módulo `sms_security.py`

---

### 2.3 Tests de Integración (Archivo: `tests/integration/test_sms_security_endpoint.py`)

#### Test 6: Endpoint `/send-sms-public` - Flujo completo exitoso

**Test Case 6.1: Flujo completo con todos los layers pasando**
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_send_sms_public_endpoint_full_success(
    async_client,
    mock_redis_for_testing,
    monkeypatch
):
    """Test flujo completo de /send-sms-public con éxito"""

    # Mock Twilio success
    mock_sms_service = AsyncMock()
    mock_sms_service.send_verification_code.return_value = {
        'success': True,
        'status': 'pending'
    }

    # Monkeypatch SMSService
    monkeypatch.setattr('app.api.v1.endpoints.auth.SMSService', lambda: mock_sms_service)

    # Execute request
    response = await async_client.post(
        "/api/v1/auth/send-sms-public?phone=%2B573001234567",
        headers={"X-Forwarded-For": "203.0.113.1"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert "enviado exitosamente" in data['message']

    # Verify Twilio was called
    mock_sms_service.send_verification_code.assert_called_once_with(
        phone_number="+573001234567",
        channel="sms"
    )
```

**Estimación**: 30 min (setup complejo de mocks)
**Prioridad**: CRÍTICA

---

#### Test 7: Rate Limiting por Teléfono

**Test Case 7.1: 3 solicitudes permitidas, 4ta bloqueada**
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_send_sms_public_phone_rate_limit(async_client, monkeypatch):
    """Validar rate limit de 3 intentos por teléfono en 10 minutos"""

    # Mock Twilio success
    mock_sms = AsyncMock()
    mock_sms.send_verification_code.return_value = {'success': True, 'status': 'pending'}
    monkeypatch.setattr('app.api.v1.endpoints.auth.SMSService', lambda: mock_sms)

    phone = "+573001234567"

    # Primer request - SUCCESS
    resp1 = await async_client.post(f"/api/v1/auth/send-sms-public?phone={phone}")
    assert resp1.status_code == 200

    # Segundo request - SUCCESS
    resp2 = await async_client.post(f"/api/v1/auth/send-sms-public?phone={phone}")
    assert resp2.status_code == 200

    # Tercer request - SUCCESS (último permitido)
    resp3 = await async_client.post(f"/api/v1/auth/send-sms-public?phone={phone}")
    assert resp3.status_code == 200

    # Cuarto request - BLOCKED (429)
    resp4 = await async_client.post(f"/api/v1/auth/send-sms-public?phone={phone}")
    assert resp4.status_code == 429
    assert "Demasiados intentos" in resp4.json()['detail']

    # Verificar header Retry-After
    assert resp4.headers.get("Retry-After") == "600"
```

**Estimación**: 25 min
**Prioridad**: CRÍTICA

---

#### Test 8: Rate Limiting por IP

**Test Case 8.1: 10 solicitudes permitidas, 11va bloqueada**
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_send_sms_public_ip_rate_limit(async_client, monkeypatch):
    """Validar rate limit de 10 intentos por IP en 1 hora"""

    mock_sms = AsyncMock()
    mock_sms.send_verification_code.return_value = {'success': True, 'status': 'pending'}
    monkeypatch.setattr('app.api.v1.endpoints.auth.SMSService', lambda: mock_sms)

    ip = "203.0.113.100"
    headers = {"X-Forwarded-For": ip}

    # Enviar 10 requests con diferentes números (para no hit phone limit)
    for i in range(10):
        phone = f"+5730012345{i:02d}"
        resp = await async_client.post(
            f"/api/v1/auth/send-sms-public?phone={phone}",
            headers=headers
        )
        assert resp.status_code == 200, f"Request {i+1} should succeed"

    # 11vo request - BLOCKED por IP rate limit
    resp11 = await async_client.post(
        f"/api/v1/auth/send-sms-public?phone=%2B573001234599",
        headers=headers
    )
    assert resp11.status_code == 429
    assert "red" in resp11.json()['detail'].lower()
    assert resp11.headers.get("Retry-After") == "3600"
```

**Estimación**: 30 min (loop de 10 requests)
**Prioridad**: CRÍTICA

---

#### Test 9: Validación de Teléfono Inválido

**Test Cases**:
- 9.1: Sin código país (+)
- 9.2: Número muy corto
- 9.3: Teléfono fijo (landline)
- 9.4: Formato inválido

```python
@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_phone,expected_error", [
    ("3001234567", "código_país"),
    ("+123", "inválido"),
    ("+5712345678", "móvil"),
    ("+999999999999", "inválido"),
])
async def test_send_sms_public_invalid_phone_formats(
    async_client,
    invalid_phone,
    expected_error
):
    """Validar rechazo de formatos telefónicos inválidos"""

    response = await async_client.post(
        f"/api/v1/auth/send-sms-public?phone={invalid_phone}"
    )

    assert response.status_code == 400
    assert expected_error in response.json()['detail'].lower()
```

**Estimación**: 20 min (parametrized)
**Prioridad**: ALTA

---

#### Test 10: Twilio API Failure

**Test Case 10.1: Twilio retorna error**
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_send_sms_public_twilio_failure(async_client, monkeypatch):
    """Manejar error de Twilio API correctamente"""

    # Mock Twilio failure
    mock_sms = AsyncMock()
    mock_sms.send_verification_code.return_value = {
        'success': False,
        'status': 'failed'
    }
    monkeypatch.setattr('app.api.v1.endpoints.auth.SMSService', lambda: mock_sms)

    response = await async_client.post(
        "/api/v1/auth/send-sms-public?phone=%2B573001234567"
    )

    assert response.status_code == 400
    assert "Error enviando SMS" in response.json()['detail']
```

**Estimación**: 15 min
**Prioridad**: ALTA

---

**Test Case 10.2: Twilio lanza excepción**
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_send_sms_public_twilio_exception(async_client, monkeypatch):
    """Manejar excepción de Twilio correctamente"""

    mock_sms = AsyncMock()
    mock_sms.send_verification_code.side_effect = Exception("Twilio API unreachable")
    monkeypatch.setattr('app.api.v1.endpoints.auth.SMSService', lambda: mock_sms)

    response = await async_client.post(
        "/api/v1/auth/send-sms-public?phone=%2B573001234567"
    )

    assert response.status_code == 500
    assert "Error al enviar código SMS" in response.json()['detail']
```

**Estimación**: 15 min
**Prioridad**: ALTA

---

#### Test 11: Security Logging Verification

**Test Case 11.1: Verificar logs generados en flujo completo**
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_send_sms_public_security_logging(async_client, monkeypatch, caplog):
    """Verificar que security events sean loggeados correctamente"""
    import logging
    caplog.set_level(logging.INFO)

    mock_sms = AsyncMock()
    mock_sms.send_verification_code.return_value = {'success': True, 'status': 'pending'}
    monkeypatch.setattr('app.api.v1.endpoints.auth.SMSService', lambda: mock_sms)

    await async_client.post("/api/v1/auth/send-sms-public?phone=%2B573001234567")

    # Verificar que se loggeó el evento exitoso
    log_messages = [rec.message for rec in caplog.records]
    assert any("SMS Security Event" in msg and "sms_sent" in msg for msg in log_messages)
```

**Estimación**: 20 min
**Prioridad**: BAJA (nice-to-have)

---

### 2.4 Resumen Tests de Integración

| Test | Descripción | Tiempo Est. | Prioridad |
|------|-------------|-------------|-----------|
| Test 6 | Flujo completo éxito | 30 min | CRÍTICA |
| Test 7 | Rate limit teléfono | 25 min | CRÍTICA |
| Test 8 | Rate limit IP | 30 min | CRÍTICA |
| Test 9 | Validación teléfono | 20 min | ALTA |
| Test 10 | Twilio failures | 30 min | ALTA |
| Test 11 | Security logging | 20 min | BAJA |
| **TOTAL INTEGRACIÓN** | - | **155 min** (~2.5 horas) | - |

**Cobertura Esperada**: 85%+ del endpoint `/send-sms-public`

---

## 3. FIXTURES NECESARIAS

### 3.1 Fixtures a Crear en `tests/conftest.py`

#### Fixture 1: `mock_request` - Mock de FastAPI Request

```python
@pytest.fixture(scope="function")
def mock_request():
    """
    Mock de FastAPI Request con headers configurables.

    Usage:
        def test_example(mock_request):
            mock_request.headers = {"X-Forwarded-For": "203.0.113.1"}
            ip = get_client_ip(mock_request)
    """
    from unittest.mock import Mock

    request = Mock()
    request.headers = {}
    request.client = Mock()
    request.client.host = "127.0.0.1"

    return request
```

**Estimación creación**: 10 min

---

#### Fixture 2: `mock_redis_service` - Mock específico de RedisService

```python
@pytest.fixture(scope="function")
def mock_redis_service():
    """
    Mock de RedisService para tests de rate limiting.

    Simula comportamiento de Redis con dict en memoria.
    """
    from unittest.mock import AsyncMock

    # Storage en memoria
    storage = {}

    async def cache_get(key):
        return storage.get(key)

    async def cache_set(key, value, expire=3600):
        storage[key] = value
        return True

    async def incr(key):
        current = int(storage.get(key, "0"))
        storage[key] = str(current + 1)
        return current + 1

    mock = AsyncMock()
    mock.cache_get.side_effect = cache_get
    mock.cache_set.side_effect = cache_set
    mock.redis.incr.side_effect = incr

    return mock
```

**Estimación creación**: 20 min

---

#### Fixture 3: `mock_sms_service_success` - Mock SMSService exitoso

```python
@pytest.fixture(scope="function")
def mock_sms_service_success(monkeypatch):
    """
    Mock de SMSService que simula envío exitoso.

    Auto-patch SMSService en auth.py
    """
    from unittest.mock import AsyncMock

    mock_sms = AsyncMock()
    mock_sms.send_verification_code.return_value = {
        'success': True,
        'status': 'pending'
    }

    # Auto-patch
    monkeypatch.setattr(
        'app.api.v1.endpoints.auth.SMSService',
        lambda: mock_sms
    )

    return mock_sms
```

**Estimación creación**: 15 min

---

#### Fixture 4: `mock_sms_service_fail` - Mock SMSService fallido

```python
@pytest.fixture(scope="function")
def mock_sms_service_fail(monkeypatch):
    """Mock de SMSService que simula falla de Twilio"""
    from unittest.mock import AsyncMock

    mock_sms = AsyncMock()
    mock_sms.send_verification_code.return_value = {
        'success': False,
        'status': 'failed'
    }

    monkeypatch.setattr(
        'app.api.v1.endpoints.auth.SMSService',
        lambda: mock_sms
    )

    return mock_sms
```

**Estimación creación**: 10 min

---

### 3.2 Resumen Fixtures

| Fixture | Tipo | Scope | Estimación | Prioridad |
|---------|------|-------|------------|-----------|
| `mock_request` | Mock | function | 10 min | ALTA |
| `mock_redis_service` | Mock | function | 20 min | CRÍTICA |
| `mock_sms_service_success` | Mock | function | 15 min | CRÍTICA |
| `mock_sms_service_fail` | Mock | function | 10 min | ALTA |
| **TOTAL FIXTURES** | - | - | **55 min** | - |

---

## 4. ESTRUCTURA DE ARCHIVOS PROPUESTA

```
tests/
├── conftest.py                           # Agregar 4 fixtures nuevas
├── unit/
│   └── test_sms_security.py              # NUEVO: 30 test cases unitarios
└── integration/
    └── test_sms_security_endpoint.py     # NUEVO: 10+ test cases integración
```

**Justificación**:
- `unit/` → Tests aislados de funciones sin dependencias externas
- `integration/` → Tests del endpoint completo con mocks

---

## 5. PATRÓN TDD Y CICLO RED-GREEN-REFACTOR

### 5.1 Uso de Markers

**Markers Obligatorios**:
```python
@pytest.mark.unit               # Tests unitarios
@pytest.mark.integration        # Tests de integración
@pytest.mark.sms_security       # Específico de SMS security
@pytest.mark.rate_limit         # Rate limiting tests
@pytest.mark.phone_validation   # Validación de teléfonos
@pytest.mark.asyncio            # Tests async (pytest-asyncio)
```

**Ejemplo**:
```python
@pytest.mark.unit
@pytest.mark.sms_security
@pytest.mark.rate_limit
@pytest.mark.asyncio
async def test_check_phone_rate_limit_first_attempt():
    pass
```

### 5.2 Tests Síncronos vs Async

| Función | Test Type | Justificación |
|---------|-----------|---------------|
| `check_phone_rate_limit()` | **async** | Función async con Redis |
| `check_ip_rate_limit()` | **async** | Función async con Redis |
| `validate_phone_number()` | **sync** | Función sync, no I/O |
| `get_client_ip()` | **sync** | Función sync |
| `log_sms_security_event()` | **sync** | Función sync |
| Endpoint `/send-sms-public` | **async** | FastAPI endpoint async |

### 5.3 Uso de Parametrize

**Ejemplo: Validación de múltiples teléfonos inválidos**
```python
@pytest.mark.unit
@pytest.mark.parametrize("invalid_phone,expected_error_fragment", [
    ("3001234567", "código_país"),
    ("+123", "inválido"),
    ("+5712345678", "móvil"),
    ("+999999999999", "inválido"),
    ("+57 300 123 4567", "inválido"),  # Con espacios
])
def test_validate_phone_number_invalid_formats(invalid_phone, expected_error_fragment):
    valid, message, e164 = validate_phone_number(invalid_phone)

    assert valid is False
    assert expected_error_fragment in message.lower()
    assert e164 == ""
```

**Beneficio**: 5 casos en 1 test function → más mantenible

### 5.4 Coverage Target

**Mínimo Proyecto**: 75% (configurado en `.coveragerc`)
**Target SMS Security**: 90%+ (código crítico de seguridad)

**Comando para medir**:
```bash
pytest tests/unit/test_sms_security.py tests/integration/test_sms_security_endpoint.py \
  --cov=app.core.sms_security \
  --cov=app.api.v1.endpoints.auth \
  --cov-report=term-missing \
  --cov-report=html
```

---

## 6. PLAN DE IMPLEMENTACIÓN

### 6.1 Orden de Creación (Prioridad CRÍTICA primero)

#### FASE A: Setup Inicial (60 min)
1. Crear directorio `tests/unit/` si no existe (5 min)
2. Crear archivo `tests/unit/test_sms_security.py` vacío (5 min)
3. Crear archivo `tests/integration/test_sms_security_endpoint.py` vacío (5 min)
4. Implementar 4 fixtures en `conftest.py` (55 min)
   - `mock_request` (10 min)
   - `mock_redis_service` (20 min)
   - `mock_sms_service_success` (15 min)
   - `mock_sms_service_fail` (10 min)

**Total Fase A**: 1 hora

---

#### FASE B: Tests Unitarios CRÍTICOS (125 min)
5. Test 1: `check_phone_rate_limit()` - 6 casos (75 min)
6. Test 2: `check_ip_rate_limit()` - 5 casos (50 min)

**Total Fase B**: ~2 horas

---

#### FASE C: Tests Unitarios ALTOS (80 min)
7. Test 3: `validate_phone_number()` - 10 casos (80 min)

**Total Fase C**: ~1.5 horas

---

#### FASE D: Tests Unitarios MEDIOS (98 min)
8. Test 4: `get_client_ip()` - 5 casos (50 min)
9. Test 5: `log_sms_security_event()` - 4 casos (48 min)

**Total Fase D**: ~1.5 horas

---

#### FASE E: Tests Integración CRÍTICOS (85 min)
10. Test 6: Flujo completo exitoso (30 min)
11. Test 7: Rate limit teléfono (25 min)
12. Test 8: Rate limit IP (30 min)

**Total Fase E**: ~1.5 horas

---

#### FASE F: Tests Integración ALTOS (50 min)
13. Test 9: Validación teléfono inválido (20 min)
14. Test 10: Twilio failures (30 min)

**Total Fase F**: ~1 hora

---

#### FASE G: Tests Integración BAJOS (20 min)
15. Test 11: Security logging (20 min)

**Total Fase G**: 20 min

---

### 6.2 Tiempo Total Estimado

| Fase | Descripción | Tiempo | Acumulado |
|------|-------------|--------|-----------|
| A | Setup + Fixtures | 60 min | 1h |
| B | Unit CRÍTICOS | 125 min | 3h 5min |
| C | Unit ALTOS | 80 min | 4h 25min |
| D | Unit MEDIOS | 98 min | 6h 3min |
| E | Integ CRÍTICOS | 85 min | 7h 28min |
| F | Integ ALTOS | 50 min | 8h 18min |
| G | Integ BAJOS | 20 min | 8h 38min |
| **TOTAL** | **Implementación completa** | **518 min** | **~8.6 horas** |

**Buffer 20% para debugging**: +104 min → **~10.3 horas TOTAL**

**Distribución recomendada**:
- Día 1: Fases A + B (Setup + Unit CRÍTICOS) → 3 horas
- Día 2: Fases C + D (Unit ALTOS + MEDIOS) → 3 horas
- Día 3: Fases E + F + G (Integración completa) → 2.5 horas

---

## 7. VALIDACIÓN Y CALIDAD

### 7.1 Criterios de Aceptación

**Tests Unitarios (30 casos)**:
- [x] Todos los tests son independientes (no state compartido)
- [x] Cada test valida UNA funcionalidad específica
- [x] Mocking correcto de dependencias externas
- [x] Assertions claras y específicas
- [x] Coverage >90% de `sms_security.py`

**Tests de Integración (10+ casos)**:
- [x] Validan flujo end-to-end del endpoint
- [x] Prueban todos los exit points (success + errors)
- [x] Verifican rate limiting funcional
- [x] Validan respuestas HTTP correctas (status codes + bodies)
- [x] Coverage >85% del endpoint `/send-sms-public`

**Calidad General**:
- [x] Naming descriptivo (test_function_scenario_expected)
- [x] Docstrings explicando propósito del test
- [x] Sin código duplicado (usar fixtures y parametrize)
- [x] Ejecución rápida (<30s todos los tests)
- [x] Sin falsos positivos/negativos

### 7.2 Comandos de Validación

**Ejecutar solo tests SMS security**:
```bash
pytest -v -m "sms_security"
```

**Ejecutar tests unitarios**:
```bash
pytest -v tests/unit/test_sms_security.py
```

**Ejecutar tests integración**:
```bash
pytest -v tests/integration/test_sms_security_endpoint.py
```

**Coverage completo**:
```bash
pytest tests/unit/test_sms_security.py tests/integration/test_sms_security_endpoint.py \
  --cov=app.core.sms_security \
  --cov=app.api.v1.endpoints.auth \
  --cov-report=term-missing \
  --cov-report=html \
  -v
```

**Solo tests CRÍTICOS**:
```bash
pytest -v -m "sms_security and (rate_limit or integration)"
```

---

## 8. PLANTILLAS DE CÓDIGO

### 8.1 Template Test Unitario

```python
"""
Tests unitarios para módulo SMS Security.
Archivo: tests/unit/test_sms_security.py
"""

import pytest
from unittest.mock import AsyncMock, Mock
from app.core.sms_security import (
    check_phone_rate_limit,
    check_ip_rate_limit,
    validate_phone_number,
    get_client_ip,
    log_sms_security_event
)


# ============================================================================
# TEST GROUP 1: check_phone_rate_limit()
# ============================================================================

@pytest.mark.unit
@pytest.mark.sms_security
@pytest.mark.rate_limit
@pytest.mark.asyncio
async def test_check_phone_rate_limit_first_attempt():
    """Primera solicitud debe ser permitida y crear contador en Redis"""
    # Setup
    mock_redis = AsyncMock()
    mock_redis.cache_get.return_value = None
    mock_redis.cache_set.return_value = True

    # Execute
    allowed, message = await check_phone_rate_limit(mock_redis, "+573001234567")

    # Assert
    assert allowed is True
    assert message == "OK"
    mock_redis.cache_set.assert_called_once_with(
        "sms_rate_limit:phone:+573001234567",
        "1",
        expire=600
    )


# ... más test cases aquí
```

### 8.2 Template Test Integración

```python
"""
Tests de integración para endpoint /send-sms-public.
Archivo: tests/integration/test_sms_security_endpoint.py
"""

import pytest
from unittest.mock import AsyncMock


@pytest.mark.integration
@pytest.mark.sms_security
@pytest.mark.asyncio
async def test_send_sms_public_endpoint_full_success(
    async_client,
    mock_redis_for_testing,
    monkeypatch
):
    """Test flujo completo de /send-sms-public con éxito en todas las capas"""

    # Setup: Mock Twilio success
    mock_sms_service = AsyncMock()
    mock_sms_service.send_verification_code.return_value = {
        'success': True,
        'status': 'pending'
    }
    monkeypatch.setattr('app.api.v1.endpoints.auth.SMSService', lambda: mock_sms_service)

    # Execute
    response = await async_client.post(
        "/api/v1/auth/send-sms-public?phone=%2B573001234567",
        headers={"X-Forwarded-For": "203.0.113.1"}
    )

    # Assert HTTP response
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert "enviado exitosamente" in data['message']

    # Assert service was called correctly
    mock_sms_service.send_verification_code.assert_called_once_with(
        phone_number="+573001234567",
        channel="sms"
    )


# ... más test cases aquí
```

### 8.3 Template Fixture

```python
@pytest.fixture(scope="function")
def mock_redis_service():
    """
    Mock de RedisService para tests de rate limiting.

    Simula comportamiento de Redis con dict en memoria para tests aislados.

    Usage:
        async def test_example(mock_redis_service):
            allowed, msg = await check_phone_rate_limit(mock_redis_service, "+573001234567")
            assert allowed is True
    """
    from unittest.mock import AsyncMock

    # Storage en memoria
    storage = {}

    async def cache_get(key):
        return storage.get(key)

    async def cache_set(key, value, expire=3600):
        storage[key] = value
        return True

    async def incr(key):
        current = int(storage.get(key, "0"))
        storage[key] = str(current + 1)
        return current + 1

    # Create mock
    mock = AsyncMock()
    mock.cache_get.side_effect = cache_get
    mock.cache_set.side_effect = cache_set
    mock.redis.incr.side_effect = incr

    return mock
```

---

## 9. RIESGOS Y MITIGACIONES

### 9.1 Riesgos Identificados

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| **Redis mock no simula comportamiento real** | MEDIA | ALTO | Usar fixture con dict en memoria que simula TTL y atomicidad |
| **Tests flaky por timing issues** | BAJA | MEDIO | Evitar `time.sleep()`, usar mocks deterministas |
| **Coverage no alcanza 75%** | BAJA | ALTO | Priorizar tests CRÍTICOS primero, medir coverage incremental |
| **Monkeypatch de SMSService no funciona** | MEDIA | ALTO | Verificar import path correcto en monkeypatch |
| **Tests integration muy lentos** | MEDIA | BAJO | Usar mocks, evitar llamadas reales a Twilio |

### 9.2 Plan de Contingencia

**Si Redis mock falla**:
1. Usar fixture `mock_redis_for_testing` existente en conftest.py
2. Simplificar mock a solo retornar valores hardcoded
3. Priorizar tests de lógica sobre tests de Redis

**Si coverage <75%**:
1. Identificar líneas no cubiertas con `--cov-report=html`
2. Agregar tests específicos para branches no cubiertos
3. Revisar código muerto (líneas nunca ejecutadas)

**Si tests muy lentos**:
1. Usar markers para ejecutar solo tests críticos
2. Paralelizar con `pytest-xdist`
3. Optimizar fixtures (scope='module' donde sea posible)

---

## 10. PRÓXIMOS PASOS (DESPUÉS DE APROBACIÓN)

### Paso 1: Coordinar con `unit-testing-ai`
- Compartir este documento de diseño
- Solicitar aprobación de estrategia
- Asignar tasks según prioridad

### Paso 2: Implementación Incremental
- Crear branch: `feature/sms-security-tests`
- Implementar Fase A (Setup + Fixtures) primero
- Commit incremental por cada test group
- Pull Request con cobertura mínima 75%

### Paso 3: Code Review
- Revisión por `security-backend-ai` (validar tests de seguridad)
- Revisión por `tdd-specialist` (validar patrón TDD)
- Aprobación final de `master-orchestrator`

### Paso 4: Merge y CI/CD
- Merge a `main` después de aprobaciones
- Verificar que CI/CD pase con nuevos tests
- Monitorear coverage en pipeline

---

## 11. RESUMEN EJECUTIVO

### Tests Totales: 40+

| Categoría | Cantidad | Tiempo Est. | Prioridad |
|-----------|----------|-------------|-----------|
| **Tests Unitarios** | 30 | 5 horas | ALTA |
| **Tests Integración** | 10+ | 2.5 horas | CRÍTICA |
| **Fixtures** | 4 | 1 hora | CRÍTICA |
| **TOTAL** | 44+ | **~10 horas** | - |

### Coverage Esperado

| Módulo/Endpoint | Coverage Target | Líneas Cubiertas |
|-----------------|-----------------|------------------|
| `app/core/sms_security.py` | 90%+ | 138+ de 153 LOC |
| `/send-sms-public` endpoint | 85%+ | 145+ de 170 LOC |
| **Promedio General** | **88%** | **283+ de 323 LOC** |

### Métricas de Calidad

- **Independencia**: 100% de tests son independientes
- **Reproducibilidad**: 100% deterministas (no flaky)
- **Velocidad**: <30 segundos para suite completa
- **Mantenibilidad**: Fixtures reutilizables, código DRY

---

## 12. APROBACIONES REQUERIDAS

**Este documento requiere aprobación de**:
- [ ] `unit-testing-ai` - Validar estrategia de tests unitarios
- [ ] `security-backend-ai` - Validar tests de seguridad
- [ ] `tdd-specialist` - Validar patrón TDD y coverage

**Una vez aprobado, proceder con**:
- Creación de branch `feature/sms-security-tests`
- Implementación incremental siguiendo plan de 10 horas
- Pull Request con mínimo 75% coverage

---

## 13. REFERENCIAS

**Documentos relacionados**:
- `.workspace/PHASE_1_SECURITY_IMPLEMENTATION.md` - Fase 1 completada
- `tests/conftest.py` - Fixtures existentes
- `app/core/sms_security.py` - Código a testear
- `.coveragerc` - Configuración de coverage

**Standards y convenciones**:
- pytest markers: `unit`, `integration`, `sms_security`, `asyncio`
- Naming: `test_function_scenario_expected`
- Coverage mínimo: 75% (proyecto) → 90% (seguridad)

---

## ANEXO A: CASOS DE PRUEBA COMPLETOS

### A.1 Matriz de Test Cases

| # | Función | Caso | Input | Expected Output | Prioridad |
|---|---------|------|-------|-----------------|-----------|
| 1.1 | check_phone_rate_limit | Primera solicitud | phone="+5730..." | allowed=True, msg="OK" | CRÍTICA |
| 1.2 | check_phone_rate_limit | Segunda solicitud | count=1 | allowed=True | CRÍTICA |
| 1.3 | check_phone_rate_limit | Tercer solicitud | count=2 | allowed=True | CRÍTICA |
| 1.4 | check_phone_rate_limit | Cuarta solicitud | count=3 | allowed=False, 429 | CRÍTICA |
| 1.5 | check_phone_rate_limit | Redis falla | Exception | allowed=True (fail-open) | CRÍTICA |
| 1.6 | check_phone_rate_limit | TTL correcto | - | expire=600 | MEDIA |
| 2.1 | check_ip_rate_limit | Primera solicitud | ip="203..." | allowed=True | CRÍTICA |
| 2.2 | check_ip_rate_limit | Décima solicitud | count=9 | allowed=True | CRÍTICA |
| 2.3 | check_ip_rate_limit | Onceava solicitud | count=10 | allowed=False, 429 | CRÍTICA |
| 2.4 | check_ip_rate_limit | Redis falla | Exception | allowed=True | CRÍTICA |
| 2.5 | check_ip_rate_limit | TTL correcto | - | expire=3600 | MEDIA |
| 3.1 | validate_phone_number | Colombia móvil | "+5730012..." | valid=True | ALTA |
| 3.2 | validate_phone_number | USA móvil | "+1737977..." | valid=True | ALTA |
| 3.3 | validate_phone_number | Sin código país | "3001234567" | valid=False | ALTA |
| 3.4 | validate_phone_number | Muy corto | "+123" | valid=False | ALTA |
| 3.5 | validate_phone_number | Landline | "+5712345678" | valid=False | ALTA |
| ... | ... | ... | ... | ... | ... |

*(Matriz completa con 40+ casos disponible en implementación)*

---

**FIN DEL DOCUMENTO DE DISEÑO**

**Próximo paso**: Esperar aprobación y proceder con implementación según plan de 10 horas.

**Responsable de implementación**: `unit-testing-ai`
**Coordinador**: `tdd-specialist` (este agente)
**Aprobador final**: `master-orchestrator`

---

**Fecha de elaboración**: 2025-10-11
**Versión**: 1.0
**Status**: PENDIENTE APROBACIÓN
