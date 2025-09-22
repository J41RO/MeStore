# 🔐 TODO SISTEMA USUARIOS Y ROLES - MESTORE MVP

**Team MVP Orchestrator - Plan de Implementación Crítico**
**Fecha**: 2025-09-20
**Prioridad**: CRÍTICA 🚨
**Estado**: PLAN ACTIVO ⚡

---

## 🚨 ERRORES CRÍTICOS - ACCIÓN INMEDIATA (24-48 HORAS)

### 🔴 PRIORIDAD 1: FIX ASYNC/AWAIT ERRORS

#### 1.1 Corregir Registro de Vendedores
- **Archivo**: `app/api/v1/endpoints/vendedores.py` (líneas 169-274)
- **Error**: `object ChunkedIteratorResult can't be used in 'await' expression`
- **Solución**: Corregir uso de async con SQLAlchemy queries
- **Tiempo estimado**: 2-3 horas
- **Asignado a**: backend-framework-ai + database-architect-ai

```python
# PROBLEMA ACTUAL:
result = await db.execute(stmt)
existing_user = result.scalar_one_or_none()  # ❌ Falta await

# SOLUCIÓN:
result = await db.execute(stmt)
existing_user = result.scalar_one_or_none()  # ✅ Correcto
```

#### 1.2 Corregir Login de Vendedores
- **Archivo**: `app/api/v1/endpoints/vendedores.py` (endpoint login)
- **Error**: `'async_generator' object is not an iterator`
- **Solución**: Revisar manejo de resultados async en login
- **Tiempo estimado**: 1-2 horas
- **Asignado a**: security-backend-ai

#### 1.3 Tests de Verificación
- **Archivo**: `tests/test_vendedores_login.py`
- **Acción**: Ejecutar y validar que funcione después de fixes
- **Comando**: `python -m pytest tests/test_vendedores_login.py -v`
- **Tiempo estimado**: 1 hora
- **Asignado a**: tdd-specialist

---

## 🟠 FUNCIONALIDADES FALTANTES - CORTO PLAZO (1 SEMANA)

### 🔶 PRIORIDAD 2: REGISTRO DE COMPRADORES

#### 2.1 Crear Endpoint Registro Compradores
- **Archivo**: `app/api/v1/endpoints/auth.py` o crear `buyers.py`
- **Endpoint**: `POST /api/v1/auth/register-buyer`
- **Campos obligatorios**: email, password, nombre, apellido
- **Campos opcionales**: telefono, ciudad
- **user_type**: Automático BUYER
- **Tiempo estimado**: 3-4 horas
- **Asignado a**: api-architect-ai

```python
# ESQUEMA REQUERIDO:
@router.post("/register-buyer", response_model=TokenResponse)
async def register_buyer(
    buyer_data: BuyerCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    # Implementación similar a vendedores pero simplificada
```

#### 2.2 Schema para Compradores
- **Archivo**: `app/schemas/auth.py`
- **Clase**: `BuyerCreateRequest`
- **Validaciones**: Email único, password fuerte
- **Tiempo estimado**: 1 hora
- **Asignado a**: api-architect-ai

#### 2.3 Tests Registro Compradores
- **Archivo**: `tests/api/test_buyer_registration.py`
- **Tests**: Registro exitoso, email duplicado, validaciones
- **Tiempo estimado**: 2 horas
- **Asignado a**: tdd-specialist

### 🔶 PRIORIDAD 3: SISTEMA OTP FUNCIONAL

#### 3.1 Servicio de Envío de OTP
- **Archivo**: `app/services/otp_service.py` (existe pero no funcional)
- **Funciones**: send_email_otp(), verify_otp(), generate_otp()
- **Integración**: Con servicio de email
- **Tiempo estimado**: 4-5 horas
- **Asignado a**: backend-framework-ai + communication-ai

#### 3.2 Endpoints de Verificación
- **Archivo**: `app/api/v1/endpoints/auth.py`
- **Endpoints**:
  - `POST /api/v1/auth/send-otp`
  - `POST /api/v1/auth/verify-otp`
- **Tiempo estimado**: 2-3 horas
- **Asignado a**: api-architect-ai

#### 3.3 Frontend OTP Flow
- **Archivos**: Componentes de verificación
- **Pantallas**: Envío OTP, Verificación código
- **Tiempo estimado**: 4-6 horas
- **Asignado a**: react-specialist-ai

---

## 🟡 VALIDACIONES FRONTEND - MEDIANO PLAZO (2 SEMANAS)

### 🔷 PRIORIDAD 4: ROLE-BASED ACCESS CONTROL

#### 4.1 Guards de Navegación
- **Archivo**: `frontend/src/components/auth/RoleGuard.tsx`
- **Funcionalidad**: Proteger rutas por user_type
- **Roles**: ADMIN, VENDOR, BUYER
- **Tiempo estimado**: 3-4 horas
- **Asignado a**: react-specialist-ai

#### 4.2 Dashboards Específicos por Rol
- **Vendor Dashboard**: Productos, ventas, comisiones
- **Buyer Dashboard**: Pedidos, favoritos, historial
- **Admin Dashboard**: Gestión usuarios, estadísticas
- **Tiempo estimado**: 8-12 horas por dashboard
- **Asignado a**: frontend-framework-ai + ux-specialist-ai

#### 4.3 Navegación Condicional
- **Archivo**: `frontend/src/components/layout/Navigation.tsx`
- **Funcionalidad**: Menús diferentes por rol
- **Tiempo estimado**: 2-3 horas
- **Asignado a**: ux-specialist-ai

---

## 🔵 OPTIMIZACIONES UX - LARGO PLAZO (3-4 SEMANAS)

### 🔹 PRIORIDAD 5: ONBOARDING FLOWS

#### 5.1 Flujo Registro Vendedores
- **Pasos**: Registro → Verificación → Documentos → Aprobación
- **Estados**: DRAFT → PENDING_DOCUMENTS → PENDING_APPROVAL → APPROVED
- **Tiempo estimado**: 6-8 horas
- **Asignado a**: ux-specialist-ai

#### 5.2 Flujo Registro Compradores
- **Pasos**: Registro → Verificación → Onboarding → Compras
- **Simplificado**: Sin documentos ni aprobaciones
- **Tiempo estimado**: 4-5 horas
- **Asignado a**: ux-specialist-ai

#### 5.3 Welcome Dashboards
- **Vendors**: Tutorial productos, configuración pagos
- **Buyers**: Tutorial compras, configuración perfil
- **Tiempo estimado**: 4-6 horas cada uno
- **Asignado a**: ux-specialist-ai

---

## 📋 TESTS DE ACEPTACIÓN CRÍTICOS

### ✅ CHECKLIST MVP USUARIOS/ROLES

#### Backend Functionality
- [ ] **Registro vendedor funciona** sin async errors
- [ ] **Login vendedor funciona** sin generator errors
- [ ] **Registro comprador implementado** y funcional
- [ ] **Login admin/superuser funciona**
- [ ] **Autorización por roles funciona** en endpoints
- [ ] **Creación de admins por superuser** funciona

#### Frontend Functionality
- [ ] **Role guards protegen rutas** correctamente
- [ ] **Navegación condicional** por user_type
- [ ] **Dashboards específicos** por rol funcionan
- [ ] **Formularios registro** vendor/buyer funcionan
- [ ] **Login/logout flow** completo funciona

#### Security & Validation
- [ ] **JWT tokens válidos** y seguros
- [ ] **Refresh tokens funcionan**
- [ ] **Passwords hasheadas** correctamente
- [ ] **Email único enforced**
- [ ] **Cédula única enforced**
- [ ] **OTP verification funciona**

---

## 🚀 PLAN DE EJECUCIÓN POR SPRINTS

### SPRINT 1: CORRECCIÓN CRÍTICA (2 días)
**Objetivo**: Restaurar funcionalidad básica
- Fix async/await errors vendedores
- Fix login vendedores
- Tests de verificación

### SPRINT 2: COMPRADORES (3 días)
**Objetivo**: Implementar registro compradores
- Endpoint registro buyers
- Schema y validaciones
- Tests completos

### SPRINT 3: OTP SYSTEM (5 días)
**Objetivo**: Sistema verificación funcional
- Servicio OTP
- Endpoints verification
- Frontend components

### SPRINT 4: FRONTEND ROLES (5 días)
**Objetivo**: Role-based access control
- Role guards
- Conditional navigation
- Basic dashboards

### SPRINT 5: UX OPTIMIZATION (7 días)
**Objetivo**: Experiencia usuario completa
- Onboarding flows
- Welcome dashboards
- Polish y testing

---

## 📊 MÉTRICAS DE ÉXITO

### KPIs Técnicos
- ✅ 0 errores críticos en sistema auth
- ✅ 100% tests passing para usuarios/roles
- ✅ Cobertura >90% en módulos auth
- ✅ Tiempo respuesta login <200ms

### KPIs Funcionales
- ✅ Registro vendedor/comprador funciona
- ✅ Login por roles funciona
- ✅ Separación roles frontend funciona
- ✅ OTP verification funciona

### KPIs UX
- ✅ Onboarding completado <5 minutos
- ✅ Dashboards específicos por rol
- ✅ Navegación intuitiva por user_type
- ✅ 0 accesos no autorizados

---

## 🔧 COMANDOS DE VALIDACIÓN

### Tests Backend
```bash
# Test salud sistema
python -m pytest tests/api/test_health.py -v

# Test autenticación
python -m pytest tests/test_vendedores_login.py -v
python -m pytest tests/unit/auth/ -v

# Test usuarios
python -m pytest tests/test_models_user.py -v
python -m pytest tests/test_user_colombian_fields.py -v

# Coverage completo
python -m pytest --cov=app/api/v1/endpoints/auth.py --cov-report=term-missing
```

### Validación Manual
```bash
# Verificar servidor corriendo
curl http://192.168.1.137:8000/health

# Test registro vendedor
curl -X POST http://192.168.1.137:8000/api/v1/vendedores/registro \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test123!","nombre":"Test","apellido":"User","cedula":"12345678"}'

# Test login
curl -X POST http://192.168.1.137:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test123!"}'
```

---

## 🎯 ENTREGABLES FINALES

### Documentación Requerida
1. **API Documentation** - Endpoints auth actualizados
2. **User Roles Guide** - Documentación para desarrolladores
3. **Frontend Integration Guide** - Como implementar role guards
4. **Testing Strategy** - Tests E2E para autenticación

### Código Entregable
1. **Backend**: Todos los endpoints auth funcionando
2. **Frontend**: Role-based access control completo
3. **Tests**: Cobertura >90% en sistema usuarios
4. **Database**: Migraciones para nuevos campos si necesario

---

## ⚠️ RIESGOS Y MITIGACIONES

### Riesgo 1: Async/Await Complexity
- **Mitigación**: Pair programming con database-architect-ai
- **Backup**: Rollback a versiones síncronas si necesario

### Riesgo 2: Frontend Role Integration
- **Mitigación**: Tests E2E desde día 1
- **Backup**: Implementación básica primero, optimización después

### Riesgo 3: OTP Service Dependencies
- **Mitigación**: Mock service para development
- **Backup**: Verificación automática en testing

---

**RESPONSABLE GENERAL**: team-mvp-orchestrator
**SUPERVISIÓN**: master-orchestrator
**ESCALACIÓN**: director-enterprise-ceo

**PRÓXIMA REVISIÓN**: 24 horas después de inicio Sprint 1
**STATUS REPORTS**: Diarios durante corrección crítica

---

## 📞 CONTACTOS DE EMERGENCIA

**Errores críticos**: security-backend-ai + backend-framework-ai
**Database issues**: database-architect-ai
**Frontend problems**: react-specialist-ai
**Testing failures**: tdd-specialist
**Architecture decisions**: system-architect-ai

---

Este TODO es un **documento vivo** que se actualizará conforme avance la implementación. Cada tarea completada debe marcarse ✅ y cualquier bloqueo debe escalarse inmediatamente al team-mvp-orchestrator.