# METADATOS: app/services/auth_service.py

## 🔒 ESTADO: PROTEGIDO CRÍTICO
**RIESGO**: MÁXIMO - Lógica de autenticación

## 📝 INFORMACIÓN
- **Última modificación**: 2025-09-20
- **Agente responsable**: security-backend-ai`
- **Tipo**: Servicio de autenticación
- **Función**: Lógica de login, registro, JWT, validaciones

## ⚠️ REGLAS DE MODIFICACIÓN
- ❌ **NO CAMBIAR** lógica de hashing de passwords
- ❌ **NO MODIFICAR** validación de JWT tokens
- ❌ **NO ALTERAR** verificación de roles
- ❌ **NO TOCAR** manejo de sesiones
- ✅ **SÍ PERMITIDO**: Agregar nuevos métodos con aprobación

## 🚨 PROTOCOLO ANTES DE MODIFICAR
1. **CONTACTO OBLIGATORIO**:
   ```bash
   python .workspace/scripts/contact_responsible_agent.py [tu-agente] app/services/auth_service.py [motivo]
   ```
2. **Agente Backup**: api-security (si principal no responde)
3. **Escalación**: master-orchestrator (después de 15 minutos)
4. Ejecutar tests completos de autenticación
5. Verificar login/logout funcionan
6. Validar roles y permisos
7. Probar refresh tokens

## 👥 CADENA DE RESPONSABILIDAD
- **Principal**: security-backend-ai (5 min máx respuesta)
- **Backup**: api-security (10 min máx respuesta)
- **Escalación**: master-orchestrator (inmediato)
- **Departamento**: .workspace/departments/backend/security-backend-ai/

## 📋 CONFIGURACIONES ACTUALES
- Password hashing: bcrypt con salt
- JWT: HS256 algorithm
- Token expiry: 30 min access, 7 days refresh
- Roles: admin, vendedor, comprador
- Session management: Redis-based

## 🔄 HISTORIAL DE CAMBIOS
- 2025-09-20: Lógica auth estable (security-backend-ai)
- Estado: CRÍTICO - CAMBIOS ROMPEN LOGIN

## ⚡ ALERTAS HISTÓRICAS
- 🔥 PROBLEMA CRÍTICO: Modificaciones aquí rompen login completo
- ⚠️ JWT generation/validation es muy sensible
- ⚠️ Password hashing no debe cambiar
- ⚠️ Solo security-backend-ai puede modificar

## 🧪 TESTS OBLIGATORIOS POST-MODIFICACIÓN
```bash
# Tests específicos de auth service
python -m pytest tests/unit/auth/test_auth_service* -v

# Tests de endpoints auth
python -m pytest tests/api/test_auth_endpoints.py -v

# Verificar roles y permisos
python -m pytest -k "test_role" -v
```