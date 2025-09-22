# METADATOS: frontend/vite.config.ts

## 🔒 ESTADO: PROTEGIDO CRÍTICO
**RIESGO**: ALTO - Configuración frontend

## 📝 INFORMACIÓN
- **Última modificación**: 2025-09-20
- **Agente responsable**: frontend-performance-ai
- **Tipo**: Configuración Vite desarrollo
- **Función**: Servidor de desarrollo y build

## ⚠️ REGLAS DE MODIFICACIÓN
- ❌ **NO CAMBIAR** puerto del servidor (5173)
- ❌ **NO MODIFICAR** proxy hacia backend (localhost:8000)
- ❌ **NO ALTERAR** configuración de HMR
- ❌ **NO TOCAR** configuración de testing
- ✅ **SÍ PERMITIDO**: Optimizaciones de build con aprobación

## 🚨 PROTOCOLO ANTES DE MODIFICAR
1. **CONTACTO OBLIGATORIO**:
   ```bash
   python .workspace/scripts/contact_responsible_agent.py [tu-agente] frontend/vite.config.ts [motivo]
   ```
2. **Agente Backup**: react-specialist-ai (si principal no responde)
3. **Escalación**: master-orchestrator (después de 15 minutos)
4. Verificar que proxy mantiene conexión con backend
5. Confirmar que puerto 5173 sigue disponible
6. Validar que Docker Compose sigue funcionando
7. Probar hot reload después de cambios

## 👥 CADENA DE RESPONSABILIDAD
- **Principal**: frontend-performance-ai (5 min máx respuesta)
- **Backup**: react-specialist-ai (10 min máx respuesta)
- **Escalación**: master-orchestrator (inmediato)
- **Departamento**: .workspace/departments/frontend/frontend-performance-ai/

## 📋 CONFIGURACIONES ACTUALES
- Puerto: 5173
- Proxy: /api -> http://localhost:8000
- HMR: Habilitado
- Build: Optimizado para producción
- Testing: Vitest configurado

## 🔄 HISTORIAL DE CAMBIOS
- 2025-09-20: Configuración estable Vite (frontend-performance-ai)
- Estado: ESTABLE - CAMBIOS ROMPEN DESARROLLO

## ⚡ ALERTAS HISTÓRICAS
- ⚠️ Cambios en proxy rompen conexión API
- ⚠️ Modificaciones de puerto afectan Docker
- ⚠️ HMR se rompe con configuraciones incorrectas