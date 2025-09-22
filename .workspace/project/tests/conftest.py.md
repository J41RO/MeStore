# METADATOS: tests/conftest.py

## 🔒 ESTADO: PROTEGIDO CRÍTICO
**RIESGO**: MÁXIMO - NO CREAR USUARIOS DUPLICADOS

## 📝 INFORMACIÓN
- **Última modificación**: 2025-09-20
- **Agente responsable**: tdd-specialist
- **Tipo**: Fixtures de testing pytest
- **Función**: Datos de prueba para testing

## ⚠️ REGLAS DE MODIFICACIÓN
- ❌ **NO CREAR** usuarios duplicados (email/documento únicos)
- ❌ **NO MODIFICAR** fixtures existentes sin validar dependencias
- ❌ **NO ALTERAR** configuración de base de datos de testing
- ❌ **NO CAMBIAR** isolation de transacciones
- ✅ **SÍ PERMITIDO**: Agregar nuevas fixtures que no conflicten

## 🚨 PROTOCOLO ANTES DE MODIFICAR
1. **CONTACTO OBLIGATORIO**:
   ```bash
   python .workspace/scripts/contact_responsible_agent.py [tu-agente] tests/conftest.py [motivo]
   ```
2. **Agente Backup**: unit-testing-ai (si principal no responde)
3. **Escalación**: master-orchestrator (después de 15 minutos)
4. Verificar que no hay emails/documentos duplicados
5. Ejecutar TODOS los tests antes de commit
6. Validar que tests existentes siguen pasando
7. Confirmar aislamiento de base de datos

## 👥 CADENA DE RESPONSABILIDAD
- **Principal**: tdd-specialist (5 min máx respuesta)
- **Backup**: unit-testing-ai (10 min máx respuesta)
- **Escalación**: master-orchestrator (inmediato)
- **Departamento**: .workspace/departments/testing/tdd-specialist/

## 📋 CONFIGURACIONES ACTUALES
- Base de datos: Testing aislada con transacciones
- Usuarios fixture: Con emails únicos
- Fixtures disponibles: user_factory, vendor_factory, etc.
- Cleanup: Automático con rollback

## 🔄 HISTORIAL DE CAMBIOS
- 2025-09-20: Fixtures estables sin duplicados (tdd-specialist)
- Estado: CRÍTICO - USUARIOS DUPLICADOS DETECTADOS ANTES

## ⚡ ALERTAS HISTÓRICAS
- 🔥 PROBLEMA CRÍTICO: Tests creaban users con emails duplicados
- ⚠️ IntegrityError por email/documento constraints
- ⚠️ Tests fallaban por fixtures mal configurados
- ⚠️ Solo usar fixtures existentes - NO crear usuarios en tests individuales

## 🧪 TESTS OBLIGATORIOS POST-MODIFICACIÓN
```bash
# Verificar que no hay duplicados
python -m pytest tests/ -v -k "test_user"

# Verificar fixtures funcionan
python -m pytest tests/ -v --tb=short

# Verificar isolation
python -m pytest tests/test_database_isolation.py -v
```