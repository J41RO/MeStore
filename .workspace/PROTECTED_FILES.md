# 🛡️ ARCHIVOS PROTEGIDOS MESTORE

## 🚨 LISTA DEFINITIVA DE ARCHIVOS INTOCABLES

### 🔥 NIVEL CRÍTICO (NUNCA MODIFICAR)

#### Configuración de Servidores
```
❌ app/main.py                    # Punto entrada FastAPI - Puerto 8000
❌ frontend/vite.config.ts        # Configuración Vite - Puerto 5173
❌ docker-compose.yml             # Orquestación servicios
❌ app/core/config.py             # Variables entorno críticas
```

#### Sistema de Autenticación Completo
```
❌ app/api/v1/deps/auth.py        # Dependencias JWT - CRÍTICO
❌ app/services/auth_service.py   # Lógica autenticación
❌ app/api/v1/endpoints/auth.py   # Endpoints login/registro
❌ frontend/src/contexts/AuthContext.tsx   # Context React auth
❌ frontend/src/services/authService.ts    # Cliente auth
❌ frontend/src/components/auth/            # Componentes auth
```

#### Modelos de Base de Datos Críticos
```
❌ app/models/user.py             # Modelo usuarios - NO DUPLICAR
❌ app/models/order.py            # Modelo pedidos
❌ app/database.py                # Configuración DB
❌ alembic/                       # Migraciones - Solo DB expert
```

### ⚠️ NIVEL ALTO RIESGO (CONSULTA OBLIGATORIA)

#### Sistema de Pagos
```
⚠️ app/services/integrated_payment_service.py
⚠️ app/api/v1/endpoints/payments.py
⚠️ frontend/src/components/payments/
⚠️ app/models/payment.py
```

#### Testing y Fixtures
```
⚠️ tests/conftest.py              # Fixtures - NO CREAR USUARIOS DUPLICADOS
⚠️ tests/database_isolation.py   # Aislamiento DB
⚠️ tests/fixtures/               # Datos de prueba
```

#### Configuración de Infraestructura
```
⚠️ Dockerfile                    # Contenedor backend
⚠️ frontend/Dockerfile           # Contenedor frontend
⚠️ .env.example                  # Variables ejemplo
⚠️ alembic.ini                   # Configuración migraciones
```

### 📋 PROBLEMAS HISTÓRICOS DETECTADOS

#### 🔥 USUARIOS DUPLICADOS EN TESTING
**Archivos afectados:**
- `tests/conftest.py` - Fixtures crean users duplicados
- `tests/test_*.py` - Tests individuales crean users
- `app/models/user.py` - Constraints únicos violados

**Solución obligatoria:**
- Usar SOLO fixtures existentes de `conftest.py`
- NO crear usuarios en tests individuales
- Verificar email/documento únicos

#### 🔥 PUERTOS DE SERVIDOR CAMBIADOS
**Archivos afectados:**
- `docker-compose.yml` - Cambian puerto 8000->otro
- `frontend/vite.config.ts` - Cambian puerto 5173->otro
- `app/main.py` - Modifican puerto uvicorn

**Consecuencia:**
- Frontend pierde conexión con backend
- Docker Compose no levanta servicios
- Desarrollo se rompe completamente

#### 🔥 AUTENTICACIÓN ROTA
**Archivos afectados:**
- `app/api/v1/deps/auth.py` - Modifican validación JWT
- `app/services/auth_service.py` - Cambian lógica login
- JWT secrets/algorithms modificados

**Consecuencia:**
- Usuarios no pueden hacer login
- Sesiones se invalidan
- Vendedores pierden acceso

### 🎯 REGLAS ESPECÍFICAS POR ARCHIVO

#### app/main.py
```
✅ PERMITIDO: Agregar nuevos routers
❌ PROHIBIDO: Cambiar puerto, CORS, middleware
🔍 RESPONSABLE: system-architect-ai
```

#### app/api/v1/deps/auth.py
```
✅ PERMITIDO: Agregar nuevos roles (con aprobación)
❌ PROHIBIDO: Modificar validación JWT existente
🔍 RESPONSABLE: security-backend-ai
```

#### app/models/user.py
```
✅ PERMITIDO: Agregar campos opcionales con migración
❌ PROHIBIDO: Modificar campos únicos, crear duplicados
🔍 RESPONSABLE: database-architect-ai
```

#### tests/conftest.py
```
✅ PERMITIDO: Agregar nuevas fixtures
❌ PROHIBIDO: Modificar fixtures de usuarios existentes
🔍 RESPONSABLE: tdd-specialist
```

#### docker-compose.yml
```
✅ PERMITIDO: Agregar nuevos servicios
❌ PROHIBIDO: Cambiar puertos, variables críticas
🔍 RESPONSABLE: cloud-infrastructure-ai
```

### 🚨 PROTOCOLO DE EMERGENCIA

#### Si se detecta modificación no autorizada:
1. **PARAR** desarrollo inmediatamente
2. **REVERTIR** cambio con git
3. **NOTIFICAR** a agente responsable
4. **DOCUMENTAR** incidente en `.workspace/incidents/`
5. **ACTUALIZAR** reglas si es necesario

#### Comando de verificación rápida:
```bash
# Verificar archivos críticos no modificados
git status app/main.py app/api/v1/deps/auth.py docker-compose.yml
```

### 📊 ESTADÍSTICAS DE PROTECCIÓN

#### Archivos Nivel Crítico: 12
#### Archivos Alto Riesgo: 15
#### Total Protegidos: 27

#### Agentes con Permisos Especiales:
- `master-orchestrator`: Todos los archivos
- `system-architect-ai`: Arquitectura global
- `security-backend-ai`: Solo autenticación
- `database-architect-ai`: Solo modelos y DB
- `cloud-infrastructure-ai`: Solo Docker/infra

### 🔄 ACTUALIZACIÓN DE LISTA

**Última actualización**: 2025-09-20
**Próxima revisión**: Mensual o después de incidentes
**Autorización cambios**: Solo `master-orchestrator`

---
**⚡ RECORDATORIO**: Esta lista se basa en problemas REALES detectados. No es teoría, son archivos que SE HAN ROTO múltiples veces por modificaciones incorrectas.