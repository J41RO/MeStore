# METADATOS: app/main.py

## 🔒 ESTADO: PROTEGIDO CRÍTICO
**RIESGO**: MÁXIMO - Punto de entrada de la aplicación

## 📝 INFORMACIÓN
- **Última modificación**: 2025-09-20
- **Agente responsable**: system-architect-ai
- **Tipo**: Configuración servidor FastAPI
- **Función**: Punto de entrada principal de la aplicación

## ⚠️ REGLAS DE MODIFICACIÓN
- ❌ **NO CAMBIAR** configuración de CORS
- ❌ **NO MODIFICAR** puerto del servidor (8000)
- ❌ **NO ALTERAR** middleware de autenticación
- ❌ **NO TOCAR** configuración de base de datos
- ✅ **SÍ PERMITIDO**: Agregar nuevos routers con aprobación

## 🚨 PROTOCOLO ANTES DE MODIFICAR
1. **CONTACTO OBLIGATORIO**:
   ```bash
   python .workspace/scripts/contact_responsible_agent.py [tu-agente] app/main.py [motivo]
   ```
2. **Agente Backup**: solution-architect-ai (si principal no responde)
3. **Escalación**: master-orchestrator (después de 15 minutos)
4. Verificar impacto en docker-compose.yml
5. Validar que frontend sigue conectando al puerto correcto
6. Probar que autenticación sigue funcionando

## 👥 CADENA DE RESPONSABILIDAD
- **Principal**: system-architect-ai (5 min máx respuesta)
- **Backup**: solution-architect-ai (10 min máx respuesta)
- **Escalación**: master-orchestrator (inmediato)
- **Departamento**: .workspace/departments/architecture/system-architect-ai/

## 📋 CONFIGURACIONES ACTUALES
- Puerto: 8000
- CORS: Configurado para frontend en puerto 5173
- Middleware: Auth, CORS, Error handling
- Base de datos: PostgreSQL async
- Redis: Configurado para sesiones

## 🔄 HISTORIAL DE CAMBIOS
- 2025-09-20: Configuración inicial estable (system-architect-ai)
- Estado: ESTABLE - NO TOCAR SIN AUTORIZACIÓN