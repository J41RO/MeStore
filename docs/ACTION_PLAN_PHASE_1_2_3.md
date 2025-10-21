# MESTORE - PLAN DE ACCIÓN INMEDIATO
## Fases 1-3 Detalladas

**Preparado**: Octubre 21, 2025  
**Estado Actual**: Recuperable - Proceder con cautela  
**Punto de Partida**: Antes de Fase 1  

---

## FASE 1: ESTABILIZACIÓN CRÍTICA (Semana 1)

### PRIORIDAD 1: SEGURIDAD - HACER HOY

#### 1.1 Revocar Credenciales Expuestas
- Contraseña Gmail: `jlcmbc0259*a` (EN `.env`)
- ACCIÓN: 
  1. Cambiar contraseña de `jairo.colina.co@gmail.com` AHORA
  2. Generar nueva contraseña de aplicación en Google
  3. Remover `.env` de git si está tracked

**Comando**:
```bash
# Ver si .env está en git
git ls-files | grep .env

# Si está, removerlo
git rm --cached .env

# Añadir a .gitignore si no está
echo ".env" >> .gitignore

# Nuevo commit
git add .gitignore
git commit -m "fix(security): remove .env from tracking"
```

#### 1.2 Mover a Railway Secrets
INMEDIATAMENTE en Railway Dashboard:
```
Settings → Environment Variables

Agregar:
- EMAIL_HOST_PASSWORD = (nueva contraseña)
- GOOGLE_CLIENT_ID = (desde Google Cloud)
- GOOGLE_CLIENT_SECRET = (desde Google Cloud)
- SECRET_KEY = (generar una nueva)
- DATABASE_URL = (ya debe estar)
```

#### 1.3 Audit de Google OAuth
- Revisar que GOOGLE_CLIENT_ID no sea público
- Verificar que las redirect URIs sean correctas:
  - http://localhost:5173/oauth/callback
  - https://mestocker.com/oauth/callback
  - (Agregar dominio real cuando esté listo)

### PRIORIDAD 2: CODE CLEANUP (Día 2-3)

#### 2.1 Eliminar Duplicados de Endpoints

**Problema**: Dos endpoints para vendor registration
- `/app/api/v1/endpoints/vendors.py` (4KB, nuevo)
- `/app/api/v1/endpoints/vendedores.py` (90KB, viejo)

**Decisión**: Mantener `vendors.py` (más limpio), deprecate `vendedores.py`

**Acción**:
```bash
# 1. Verificar que vendors.py tiene toda la lógica necesaria
grep -n "def " app/api/v1/endpoints/vendors.py

# 2. Si no: Copiar funciones de vendedores.py a vendors.py
# 3. Si sí: Marcar vendedores.py como deprecated
# 4. Remover vendedores.py o archivarlo
```

#### 2.2 Limpiar Archivos Backup

```bash
# Encontrar todos los .backup
find . -name "*.backup*" -type f | head -20

# Revisar contenido
ls -lah frontend/src/pages/*.backup
ls -lah app/api/v1/endpoints/*.backup*

# Decisión: Remover o archivar
mkdir -p .archive/backups
mv **/*.backup .archive/backups/
git rm -r app/api/v1/endpoints/*.backup*
```

#### 2.3 Remover Endpoints de Prueba

**Endpoints a remover de producción**:
```python
# En /app/main.py
GET  /test-token           # Line 335
GET  /db-test              # Line 266
GET  /users/test           # Line 301
```

**Acción**:
```python
# OPCIÓN A: Remover solo en producción
@app.get("/test-token")
async def get_test_token():
    if os.getenv("ENVIRONMENT") != "development":
        raise HTTPException(status_code=404)
    # ... resto del código

# OPCIÓN B: Remover completamente
# Simplemente borrar estas funciones
```

**Recomendación**: Opción B (remover completamente)

### PRIORIDAD 3: VERIFICACIÓN DE BD (Día 3-4)

#### 3.1 Verificar Migraciones en Producción

```bash
# Ver estado actual
make migrate-current

# Ver historial
make migrate-history

# IMPORTANTE: En Railway, ejecutar
python3 scripts/run_migrations.py --env production --validate
```

#### 3.2 Backup de Producción

```bash
# En Railway Dashboard
# 1. Go to Settings → Backups
# 2. Click "Create Backup Now"
# 3. Descargar backup
# 4. Almacenar en lugar seguro
```

#### 3.3 Test de Conexión DB

```bash
# Local test
python3 -c "
from app.core.config import settings
from sqlalchemy import create_engine, text
engine = create_engine(settings.DATABASE_URL)
with engine.connect() as conn:
    result = conn.execute(text('SELECT VERSION()'))
    print(result.fetchone())
"

# O vía endpoint
curl http://localhost:8000/db-test
```

### PRIORIDAD 4: TESTING (Día 4-5)

#### 4.1 Ejecutar Test Suite

```bash
# Full test run
pytest tests/ -v --tb=short 2>&1 | tee test_run.log

# Ver resumen
pytest tests/ --collect-only | grep "error"

# Count failures
pytest tests/ -v --tb=no | grep -E "FAILED|PASSED" | wc -l
```

#### 4.2 Tests Críticos Solo

```bash
# Solo tests de vendedores
pytest tests/ -k "vendor" -v

# Solo tests de auth
pytest tests/ -k "auth" -v

# Solo tests de integración
pytest tests/integration/ -v
```

#### 4.3 Generar Coverage Report

```bash
pytest tests/ --cov=app --cov-report=html --cov-report=term-missing

# Abrir reporte
open htmlcov/index.html
```

### PRIORIDAD 5: DOCUMENTACIÓN (Día 5)

#### 5.1 Actualizar README

```markdown
# MeStore - Status: STABLE FOR ACTIVATION

## Current State (Oct 21, 2025)
- Backend: 80% functional
- Frontend: 75% functional
- Vendors: 70% functional
- Infrastructure: 85% ready

## Critical Issues (RESOLVED)
- [x] Security credentials moved to Railway
- [x] Deprecated endpoints cleaned
- [x] Backup created
- [x] Tests verified

## Next Steps
See MESTORE_DIAGNOSTIC_REPORT.md for Phase 2-3
```

---

## FASE 2: ACTIVACIÓN DE VENDEDORES (Semana 2-3)

### PRIORIDAD 1: ENDPOINT CONSOLIDATION (Día 1-2)

#### 1.1 Elegir Endpoint Standard

**Opción A**: Usar `/api/v1/vendors/register`
```
Ventajas:
- Nombre en inglés (internacional)
- Más limpio y moderno
- Mejor para documentación
```

**Opción B**: Usar `/api/v1/vendedores/registro`
```
Ventajas:
- Nombre en español (local)
- Más contexto para usuarios colombianos
```

**RECOMENDACIÓN**: Opción A (`/api/v1/vendors/`)

#### 1.2 Consolidación Técnica

```python
# En /app/api/v1/__init__.py, asegurarse que:
from .endpoints import (
    vendors,           # ← Main endpoint
    # vendedores deprecated in v2.0
)

# Router registration
api_router.include_router(
    vendors.router, 
    prefix="/vendors", 
    tags=["vendors"]
)

# OPTIONAL: Legacy support (hasta 3 meses)
api_router.include_router(
    vendedores.router,
    prefix="/vendedores",
    tags=["vendedores-deprecated"]
)
```

### PRIORIDAD 2: OTP ACTIVATION (Día 2-3)

#### 2.1 Setup SMS Gateway (Twilio)

**Archivo**: `/app/services/sms_service.py` (crear si no existe)

```python
import twilio.rest
from app.core.config import settings

class SMSService:
    def __init__(self):
        self.client = twilio.rest.Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
    
    async def send_otp(self, phone: str, otp: str) -> bool:
        """Send OTP via SMS"""
        try:
            message = self.client.messages.create(
                body=f"Tu código OTP de MeStore es: {otp}",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone
            )
            return True
        except Exception as e:
            logger.error(f"SMS send failed: {e}")
            return False
```

**Configuración en `.env`**:
```
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1234567890
```

**En Railway**:
```
Settings → Environment Variables
Add TWILIO_* variables
```

#### 2.2 Setup Email Service

**Archivo**: `/app/services/email_service.py` (mejorar existente)

```python
class EmailService:
    async def send_otp(self, email: str, otp: str) -> bool:
        """Send OTP via email"""
        template = f"""
        <html>
        <body>
        <h1>MeStore - Código de Verificación</h1>
        <p>Tu código OTP es: <strong>{otp}</strong></p>
        <p>Válido por 10 minutos</p>
        </body>
        </html>
        """
        return await send_email(email, "Código de Verificación", template)
```

#### 2.3 Enable OTP in Endpoints

```python
# En /app/api/v1/endpoints/vendors.py

@router.post("/register")
async def register_vendor(
    vendor_data: VendorCreate,
    db: AsyncSession = Depends(get_db)
):
    # ... crear usuario ...
    
    # Enviar OTP
    otp = generate_otp()  # 6 dígitos
    user.otp_secret = otp
    user.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    if vendor_data.otp_method == "SMS":
        sms_service.send_otp(vendor_data.telefono, otp)
    else:
        email_service.send_otp(vendor_data.email, otp)
    
    await db.commit()
    return {"message": "OTP sent", "otp_method": vendor_data.otp_method}

@router.post("/verify-otp")
async def verify_otp(
    email: str,
    otp: str,
    db: AsyncSession = Depends(get_db)
):
    user = await db.execute(...)
    if user.otp_secret != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    if user.otp_expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")
    
    user.is_verified = True
    user.vendor_status = VendorStatus.APPROVED
    await db.commit()
    
    return {"message": "Email verified", "access_token": token}
```

### PRIORIDAD 3: ADMIN WORKFLOWS (Día 4-5)

#### 3.1 Vendor Approval Process

**Flujo Actual**: Auto-aprobación (MVP)

**Flujo Mejorado**: 
```
1. Vendor registra
2. Sistema envía OTP
3. Vendor verifica OTP
4. Status = PENDING_APPROVAL (admin review)
5. Admin revisa documentos
6. Admin aprueba (status = APPROVED) o rechaza
7. Vendor notificado
```

**Endpoint para Admin**:
```python
@router.post("/admin/{vendor_id}/approve")
async def approve_vendor(
    vendor_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user.is_admin():
        raise HTTPException(status_code=403)
    
    vendor = await db.get(User, vendor_id)
    vendor.vendor_status = VendorStatus.APPROVED
    vendor.account_status = AccountStatus.ACTIVE
    
    # Enviar email de aprobación
    await email_service.send_vendor_approved(vendor.email, vendor.business_name)
    
    await db.commit()
    return {"message": "Vendor approved"}

@router.post("/admin/{vendor_id}/reject")
async def reject_vendor(
    vendor_id: str,
    reason: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user.is_admin():
        raise HTTPException(status_code=403)
    
    vendor = await db.get(User, vendor_id)
    vendor.vendor_status = VendorStatus.REJECTED
    vendor.rejection_reason = reason
    vendor.rejected_at = datetime.utcnow()
    vendor.rejected_by_id = current_user.id
    
    # Enviar email de rechazo
    await email_service.send_vendor_rejected(
        vendor.email, 
        vendor.business_name,
        reason
    )
    
    await db.commit()
    return {"message": "Vendor rejected"}
```

#### 3.2 Admin Dashboard Integration

**Frontend**: `/frontend/src/pages/AdminVendorManagement.tsx`

```typescript
// Componente para listar vendors pendientes
const PendingVendors = () => {
  const [vendors, setVendors] = useState([]);
  
  useEffect(() => {
    fetchVendors({ status: "PENDING_APPROVAL" });
  }, []);
  
  return (
    <table>
      <thead>
        <tr>
          <th>Nombre</th>
          <th>Email</th>
          <th>Tipo</th>
          <th>Registrado</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        {vendors.map(v => (
          <tr key={v.id}>
            <td>{v.business_name}</td>
            <td>{v.email}</td>
            <td>{v.tipo_vendedor}</td>
            <td>{formatDate(v.created_at)}</td>
            <td>
              <button onClick={() => approveVendor(v.id)}>Aprobar</button>
              <button onClick={() => openRejectDialog(v.id)}>Rechazar</button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};
```

### PRIORIDAD 4: TESTING (Día 5-6)

#### 4.1 E2E Test: Vendor Registration Flow

```python
# tests/e2e/test_vendor_registration_flow.py

@pytest.mark.asyncio
async def test_vendor_registration_complete_flow(client, db):
    """Test vendor registration from start to finish"""
    
    # Step 1: Register vendor
    response = client.post("/api/v1/vendors/register", json={
        "email": "vendor@test.com",
        "password": "SecurePass123!",
        "nombre": "Juan Perez",
        "telefono": "3001234567",
        "business_name": "Mi Tienda",
        "tipo_vendedor": "persona_natural",
        "ciudad": "Bogotá",
        "departamento": "Cundinamarca"
    })
    assert response.status_code == 201
    vendor_id = response.json()["vendor_id"]
    
    # Step 2: Verify email (OTP)
    # Get OTP from DB or email service
    user = await db.get(User, vendor_id)
    otp = user.otp_secret
    
    response = client.post("/api/v1/vendors/verify-otp", json={
        "email": "vendor@test.com",
        "otp": otp
    })
    assert response.status_code == 200
    assert response.json()["access_token"]
    
    # Step 3: Approve vendor (as admin)
    admin_user = create_admin_user(db)
    admin_token = create_token(admin_user)
    
    response = client.post(
        f"/api/v1/vendors/admin/{vendor_id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    
    # Verify vendor is active
    user = await db.get(User, vendor_id)
    assert user.vendor_status == "approved"
    assert user.account_status == "active"
```

#### 4.2 Performance Test

```python
# tests/performance/test_vendor_registration_load.py

@pytest.mark.asyncio
async def test_vendor_registration_load(client, performance_monitor):
    """Test vendor registration under load"""
    
    tasks = []
    for i in range(100):  # 100 concurrent registrations
        task = register_vendor_async(client, i)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    
    # Assertions
    success_rate = len([r for r in results if r.ok]) / len(results)
    assert success_rate > 0.95  # At least 95% success
    
    # Response times
    response_times = [r.elapsed.total_seconds() for r in results]
    avg_time = sum(response_times) / len(response_times)
    assert avg_time < 2.0  # Average < 2 seconds
```

---

## FASE 3: REFINAMIENTO Y OPTIMIZACIÓN (Semana 4+)

### PRIORIDAD 1: PERFORMANCE (Semana 4)

#### 1.1 Database Query Optimization

```python
# Identificar queries lentas
# En logging:
import time

@app.middleware("http")
async def log_slow_queries(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = time.time() - start
    
    if elapsed > 0.5:
        logger.warning(f"Slow query: {request.url} took {elapsed}s")
    
    return response

# Optimizaciones específicas:
# 1. Add indexes a campos frecuentes
make migrate-auto MSG="Add indexes for vendor queries"

# 2. Implementar query eager loading
from sqlalchemy.orm import selectinload

stmt = select(User).options(
    selectinload(User.products),
    selectinload(User.orders)
).where(User.user_type == UserType.VENDOR)
```

#### 1.2 Frontend Bundle Optimization

```bash
# Analizar bundle
npm run analyze:bundle

# Optimizaciones:
# 1. Code splitting por rutas
# 2. Lazy loading de componentes
# 3. Minificación agresiva
# 4. Tree shaking

npm run build:production
```

#### 1.3 Redis Caching

```python
# En services, agregar caching
from redis.asyncio import Redis

class VendorService:
    def __init__(self, redis: Redis):
        self.redis = redis
    
    async def get_vendor_profile(self, vendor_id: str):
        # Try cache first
        cached = await self.redis.get(f"vendor:{vendor_id}")
        if cached:
            return json.loads(cached)
        
        # Query DB
        vendor = await db.get(User, vendor_id)
        
        # Cache for 1 hour
        await self.redis.setex(
            f"vendor:{vendor_id}",
            3600,
            json.dumps(vendor.to_dict())
        )
        
        return vendor
```

### PRIORIDAD 2: DOCUMENTATION (Semana 4)

#### 2.1 API Documentation (Swagger)

FastAPI auto-genera documentación en `/docs`

**Mejorar**:
```python
# En endpoints, agregar ejemplos
@router.post(
    "/vendors/register",
    response_model=VendorResponse,
    responses={
        201: {"description": "Vendor created successfully"},
        400: {"description": "Email already registered"},
        422: {"description": "Invalid request body"}
    },
    examples={
        "successful": {
            "summary": "Successful registration",
            "value": {
                "email": "vendor@example.com",
                "business_name": "Mi Tienda",
                ...
            }
        }
    }
)
async def register_vendor(vendor_data: VendorCreate):
    ...
```

#### 2.2 Setup Guide for Developers

**Archivo**: `docs/DEVELOPER_SETUP.md`

```markdown
# Developer Setup Guide

## Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

## Local Setup
1. Clone repository
2. Copy .env.example to .env
3. Install backend dependencies
4. Install frontend dependencies
5. Run database migrations
6. Start services

## Common Commands
...
```

#### 2.3 Operations Runbook

**Archivo**: `docs/OPERATIONS_RUNBOOK.md`

```markdown
# Operations Runbook

## Deployment
### Deploying to Production
1. Verify tests pass
2. Create git tag
3. Push to main
4. Railway auto-deploys

### Monitoring
- Check /health endpoint
- Monitor error rates
- Track response times

## Emergency Procedures
### Database Connection Lost
...

### High Error Rate
...
```

### PRIORIDAD 3: MONITORING (Semana 4-5)

#### 3.1 Error Tracking (Sentry)

```bash
# Instalar sentry
pip install sentry-sdk

# Configurar en app
import sentry_sdk
sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=settings.ENVIRONMENT,
    traces_sample_rate=0.1
)
```

#### 3.2 Metrics Collection

```python
# Prometheus metrics
from prometheus_client import Counter, Histogram

vendor_registrations = Counter(
    'vendor_registrations_total',
    'Total vendor registrations'
)

registration_duration = Histogram(
    'vendor_registration_duration_seconds',
    'Time to process vendor registration'
)

@router.post("/vendors/register")
async def register_vendor(...):
    with registration_duration.time():
        # ... registration logic ...
        vendor_registrations.inc()
```

#### 3.3 Alerting

**En Railway Console**:
```
Settings → Alerts
Add conditions:
- API Uptime < 99%
- Error rate > 1%
- Response time p95 > 1000ms
```

---

## CHECKLIST FASE 1-3

### FASE 1: ✓ STABILIZATION (Week 1)
- [ ] Security credentials moved
- [ ] .env removed from git
- [ ] Endpoints deduplicated
- [ ] Backup created
- [ ] Tests verified (70%+)
- [ ] Deploy to production

### FASE 2: ✓ VENDOR ACTIVATION (Week 2-3)
- [ ] Endpoint consolidated on /vendors/
- [ ] OTP SMS/Email working
- [ ] Admin approval workflow
- [ ] E2E tests pass
- [ ] Frontend integrated
- [ ] Deploy to production

### FASE 3: ✓ REFINEMENT (Week 4+)
- [ ] Performance optimized
- [ ] Documentation complete
- [ ] Monitoring active
- [ ] Caching implemented
- [ ] Roadmap for scaling
- [ ] Team trained

---

## SUPPORT CONTACTS

**Technical Issues**:
- Backend: Check /health endpoint first
- Database: `make migrate-current` shows status
- Frontend: Browser console for errors

**Emergency**:
1. Check Railway dashboard
2. Review recent deployments
3. Check Sentry for errors
4. Rollback if needed: `git revert HEAD`

---

**Document Version**: 1.0  
**Last Updated**: October 21, 2025  
**Status**: Ready for Implementation

