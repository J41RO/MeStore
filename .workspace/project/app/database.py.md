# METADATOS: app/database.py

## 🔒 ESTADO: PROTEGIDO CRÍTICO
**RIESGO**: MÁXIMO - Configuración base de datos

## 📝 INFORMACIÓN
- **Última modificación**: 2025-09-20
- **Agente responsable**: database-architect-ai
- **Tipo**: Configuración SQLAlchemy
- **Función**: Conexión DB, engine, sesiones

## ⚠️ REGLAS DE MODIFICACIÓN
- ❌ **NO CAMBIAR** configuración de engine
- ❌ **NO MODIFICAR** connection strings
- ❌ **NO ALTERAR** session factory
- ❌ **NO TOCAR** pool configurations
- ✅ **SÍ PERMITIDO**: Optimizaciones con aprobación

## 🚨 PROTOCOLO ANTES DE MODIFICAR
1. **CONTACTO OBLIGATORIO**:
   ```bash
   python .workspace/scripts/contact_responsible_agent.py [tu-agente] app/database.py [motivo]
   ```
2. **Agente Backup**: database-performance (si principal no responde)
3. **Escalación**: master-orchestrator (después de 15 minutos)
4. Verificar que conexiones DB funcionan
5. Confirmar que migraciones siguen aplicando
6. Validar que tests siguen pasando
7. Probar que transacciones funcionan

## 👥 CADENA DE RESPONSABILIDAD
- **Principal**: database-architect-ai (5 min máx respuesta)
- **Backup**: database-performance (10 min máx respuesta)
- **Escalación**: master-orchestrator (inmediato)
- **Departamento**: .workspace/departments/architecture/database-architect-ai/

## 📋 CONFIGURACIONES ACTUALES
- Engine: AsyncSession con asyncpg
- Pool: Connection pooling configurado
- Transactions: Auto-commit off
- Isolation: Read committed
- Timeout: Connection y query timeouts

## 🔄 HISTORIAL DE CAMBIOS
- 2025-09-20: Configuración DB estable (database-architect-ai)
- Estado: CRÍTICO - CAMBIOS ROMPEN ACCESO DB

## ⚡ ALERTAS HISTÓRICAS
- 🔥 PROBLEMA CRÍTICO: Cambios aquí desconectan toda la aplicación
- ⚠️ Engine config incorrecta rompe conexiones
- ⚠️ Session factory mal configurada rompe transacciones
- ⚠️ Pool settings incorrectos causan timeouts

## 🧪 TESTS OBLIGATORIOS POST-MODIFICACIÓN
```bash
# Test conexión básica
python -c "from app.database import engine; print('DB OK')"

# Tests de modelos
python -m pytest tests/test_database_working.py -v

# Test migraciones
make migrate-current
```