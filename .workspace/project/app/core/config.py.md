# METADATOS: app/core/config.py

## 🔒 ESTADO: PROTEGIDO CRÍTICO
**RIESGO**: MÁXIMO - Variables de entorno críticas

## 📝 INFORMACIÓN
- **Última modificación**: 2025-09-20
- **Agente responsable**: configuration-management
- **Tipo**: Configuraciones aplicación
- **Función**: Variables entorno, secrets, configuraciones

## ⚠️ REGLAS DE MODIFICACIÓN
- ❌ **NO CAMBIAR** DATABASE_URL sin migración
- ❌ **NO MODIFICAR** SECRET_KEY o JWT_SECRET
- ❌ **NO ALTERAR** REDIS_URL configuración
- ❌ **NO TOCAR** configuraciones de producción
- ✅ **SÍ PERMITIDO**: Agregar nuevas variables con validación

## 🚨 PROTOCOLO ANTES DE MODIFICAR
1. **CONTACTO OBLIGATORIO**:
   ```bash
   python .workspace/scripts/contact_responsible_agent.py [tu-agente] app/core/config.py [motivo]
   ```
2. **Agente Backup**: system-architect-ai (si principal no responde)
3. **Escalación**: master-orchestrator (después de 15 minutos)
4. Verificar que variables críticas no cambien
5. Confirmar que servicios siguen conectando
6. Validar configuraciones dev/staging/prod
7. Probar que secrets siguen funcionando

## 👥 CADENA DE RESPONSABILIDAD
- **Principal**: configuration-management (5 min máx respuesta)
- **Backup**: system-architect-ai (10 min máx respuesta)
- **Escalación**: master-orchestrator (inmediato)
- **Departamento**: .workspace/departments/backend/configuration-management/

## 📋 CONFIGURACIONES ACTUALES
- Database: PostgreSQL URL
- Redis: Cache configuration
- JWT: Secret keys y algoritmos
- CORS: Origins permitidos
- Environment: dev/staging/prod

## 🔄 HISTORIAL DE CAMBIOS
- 2025-09-20: Configuraciones estables (configuration-management)
- Estado: CRÍTICO - CAMBIOS ROMPEN SERVICIOS

## ⚡ ALERTAS HISTÓRICAS
- 🔥 PROBLEMA CRÍTICO: Cambios aquí rompen toda la aplicación
- ⚠️ DATABASE_URL incorrecto rompe conexión DB
- ⚠️ SECRET_KEY cambios invalidan todas las sesiones
- ⚠️ REDIS_URL incorrecto rompe cache y sesiones

## 🧪 TESTS OBLIGATORIOS POST-MODIFICACIÓN
```bash
# Verificar configuraciones cargan correctamente
python -c "from app.core.config import settings; print('Config OK')"

# Test servicios críticos
docker-compose ps
curl http://localhost:8000/health
```