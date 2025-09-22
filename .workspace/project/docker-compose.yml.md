# METADATOS: docker-compose.yml

## 🔒 ESTADO: PROTEGIDO CRÍTICO
**RIESGO**: MÁXIMO - Configuración de servicios

## 📝 INFORMACIÓN
- **Última modificación**: 2025-09-20
- **Agente responsable**: cloud-infrastructure-ai
- **Tipo**: Configuración Docker Compose
- **Función**: Orquestación de servicios de desarrollo

## ⚠️ REGLAS DE MODIFICACIÓN
- ❌ **NO CAMBIAR** puertos de servicios (8000, 5173, 5432, 6379)
- ❌ **NO MODIFICAR** variables de entorno críticas
- ❌ **NO ALTERAR** volúmenes de datos
- ❌ **NO TOCAR** configuración de red
- ✅ **SÍ PERMITIDO**: Agregar nuevos servicios con aprobación

## 🚨 PROTOCOLO ANTES DE MODIFICAR
1. **CONTACTO OBLIGATORIO**:
   ```bash
   python .workspace/scripts/contact_responsible_agent.py [tu-agente] docker-compose.yml [motivo]
   ```
2. **Agente Backup**: devops-integration-ai (si principal no responde)
3. **Escalación**: master-orchestrator (después de 15 minutos)
4. Verificar que frontend conecta en puerto correcto
5. Confirmar que backend mantiene puerto 8000
6. Validar que base de datos no pierda datos
7. Probar que Redis mantiene sesiones

## 👥 CADENA DE RESPONSABILIDAD
- **Principal**: cloud-infrastructure-ai (5 min máx respuesta)
- **Backup**: devops-integration-ai (10 min máx respuesta)
- **Escalación**: master-orchestrator (inmediato)
- **Departamento**: .workspace/departments/infrastructure/cloud-infrastructure-ai/

## 📋 CONFIGURACIONES ACTUALES
- **backend**: Puerto 8000, volume código
- **frontend**: Puerto 5173, desarrollo con Vite
- **postgres**: Puerto 5432, volumen persistente
- **redis**: Puerto 6379, cache de sesiones
- **networks**: Red interna Docker

## 🔄 HISTORIAL DE CAMBIOS
- 2025-09-20: Configuración estable servicios (cloud-infrastructure-ai)
- Estado: CRÍTICO - CAMBIOS ROMPEN CONECTIVIDAD

## ⚡ ALERTAS HISTÓRICAS
- 🔥 PROBLEMA CRÍTICO: Cambios aquí rompen la aplicación completa
- ⚠️ Frontend pierde conexión con backend
- ⚠️ Base de datos inaccesible tras modificaciones
- ⚠️ Variables de entorno mal configuradas