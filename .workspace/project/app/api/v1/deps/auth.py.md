# METADATOS: app/api/v1/deps/auth.py

## 🔒 ESTADO: PROTEGIDO CRÍTICO
**RIESGO**: MÁXIMO - Sistema de autenticación

## 📝 INFORMACIÓN
- **Última modificación**: 2025-09-20
- **Agente responsable**: security-backend-ai
- **Tipo**: Dependencias de autenticación JWT
- **Función**: Validación de tokens y permisos

## ⚠️ REGLAS DE MODIFICACIÓN
- ❌ **NO CAMBIAR** validación de tokens JWT
- ❌ **NO MODIFICAR** verificación de roles
- ❌ **NO ALTERAR** estructura de dependencias
- ❌ **NO TOCAR** configuración de seguridad
- ✅ **SÍ PERMITIDO**: Agregar nuevos roles con aprobación

## 🚨 PROTOCOLO ANTES DE MODIFICAR
1. **CONTACTO OBLIGATORIO**:
   ```bash
   python .workspace/scripts/contact_responsible_agent.py [tu-agente] app/api/v1/deps/auth.py [motivo]
   ```
2. **Agente Backup**: api-security (si principal no responde)
3. **Escalación**: master-orchestrator (después de 15 minutos)
4. Ejecutar tests de autenticación COMPLETOS
5. Verificar que frontend sigue autenticando
6. Validar que todas las rutas protegidas funcionan
7. Probar roles de vendedor, comprador, admin

## 👥 CADENA DE RESPONSABILIDAD
- **Principal**: security-backend-ai (5 min máx respuesta)
- **Backup**: api-security (10 min máx respuesta)
- **Escalación**: master-orchestrator (inmediato)
- **Departamento**: .workspace/departments/backend/security-backend-ai/

## 📋 CONFIGURACIONES ACTUALES
- JWT Secret: Variable de entorno
- Algoritmo: HS256
- Expiración: Configurada
- Roles: admin, vendedor, comprador
- Refresh tokens: Implementados

## 🔄 HISTORIAL DE CAMBIOS
- 2025-09-20: Sistema autenticación estable (security-backend-ai)
- Estado: CRÍTICO - ROMPIMIENTO FRECUENTE DETECTADO

## ⚡ ALERTAS HISTÓRICAS
- ⚠️ Este archivo ha sido modificado incorrectamente 3+ veces
- ⚠️ Cambios aquí rompen el login de usuarios
- ⚠️ Afecta directamente el acceso de vendedores