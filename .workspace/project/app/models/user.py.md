# METADATOS: app/models/user.py

## 🔒 ESTADO: PROTEGIDO CRÍTICO
**RIESGO**: MÁXIMO - Modelo base de usuarios

## 📝 INFORMACIÓN
- **Última modificación**: 2025-09-20
- **Agente responsable**: database-architect-ai
- **Tipo**: Modelo SQLAlchemy usuarios
- **Función**: Esquema de base de datos usuarios

## ⚠️ REGLAS DE MODIFICACIÓN
- ❌ **NO CREAR** usuarios duplicados en testing
- ❌ **NO MODIFICAR** campos primarios (id, email)
- ❌ **NO ALTERAR** relaciones con otras tablas
- ❌ **NO CAMBIAR** validaciones existentes
- ✅ **SÍ PERMITIDO**: Agregar campos opcionales con migración

## 🚨 PROTOCOLO ANTES DE MODIFICAR
1. **CONTACTO OBLIGATORIO**:
   ```bash
   python .workspace/scripts/contact_responsible_agent.py [tu-agente] app/models/user.py [motivo]
   ```
2. **Agente Backup**: backend-framework-ai (si principal no responde)
3. **Escalación**: master-orchestrator (después de 15 minutos)
4. Verificar que no existen usuarios de prueba duplicados
5. Ejecutar migración de base de datos
6. Probar registro y login después de cambios
7. Validar que tests no crean usuarios duplicados

## 👥 CADENA DE RESPONSABILIDAD
- **Principal**: database-architect-ai (5 min máx respuesta)
- **Backup**: backend-framework-ai (10 min máx respuesta)
- **Escalación**: master-orchestrator (inmediato)
- **Departamento**: .workspace/departments/architecture/database-architect-ai/

## 📋 CONFIGURACIONES ACTUALES
- Campos únicos: email, documento_identidad
- Roles: definidos en enum
- Validaciones: email, teléfono colombiano
- Relaciones: con orders, vendedor_profile
- Campos colombianos: implementados

## 🔄 HISTORIAL DE CAMBIOS
- 2025-09-20: Modelo usuarios estable (database-architect-ai)
- Estado: CRÍTICO - CREACIÓN DUPLICADA FRECUENTE

## ⚡ ALERTAS HISTÓRICAS
- 🔥 PROBLEMA CRÍTICO: Tests crean usuarios duplicados
- ⚠️ Registro de usuarios falla por duplicados
- ⚠️ Email constraint violations frecuentes
- ⚠️ Verificar fixtures de testing