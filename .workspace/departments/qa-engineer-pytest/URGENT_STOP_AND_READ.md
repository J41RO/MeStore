# 🚨 DETENER TRABAJO INMEDIATAMENTE - LEER OBLIGATORIO

## ⛔ **TRABAJO SUSPENDIDO HASTA NUEVA ORDEN**

### 📋 **INSTRUCCIONES INMEDIATAS:**

1. **DETENER** cualquier test o modificación que estés haciendo AHORA MISMO
2. **LEER** el archivo `MANDATORY_INSTRUCTIONS.md` en este directorio
3. **VERIFICAR** que el sistema esté funcionando:
   ```bash
   curl http://localhost:8000/health
   curl -X POST "http://localhost:8000/api/v1/auth/admin-login" \
        -H "Content-Type: application/json" \
        -d '{"email": "super@mestore.com", "password": "123456"}'
   ```

### ⚠️ **PROHIBIDO HASTA NUEVA ORDEN:**
- Modificar cualquier archivo de configuración
- Cambiar esquemas de base de datos
- Alterar archivos de autenticación
- Ejecutar tests que puedan afectar `mestore_production.db`
- Trabajar sin coordinación con el manager

### ✅ **LO QUE DEBES HACER:**
1. **LEER** `MANDATORY_INSTRUCTIONS.md` completamente
2. **CONSULTAR** `../PROJECT_CONTEXT.md` para entender el estado actual
3. **COORDINAR** con el enterprise-project-manager antes de continuar
4. **ESPERAR** autorización específica antes de reanudar cualquier trabajo

### 🎯 **PARA TESTING ESPECÍFICAMENTE:**
- **NO** uses `mestore_production.db` para tests
- **USA** una base de datos separada como `mestore_test.db`
- **VERIFICA** que tus tests no rompan funcionalidades existentes
- **COORDINA** con backend y frontend antes de cambios que los afecten

---

**🚨 ESTE ES UN PROTOCOLO DE EMERGENCIA PARA EVITAR ROMPER EL SISTEMA**
**🚨 NO CONTINÚES TRABAJANDO HASTA LEER TODA LA DOCUMENTACIÓN**
**🚨 CUALQUIER TRABAJO SIN COORDINACIÓN SERÁ DESECHADO**

---
**Fecha:** $(date)
**Estado:** SUSPENSIÓN ACTIVA
**Próximo paso:** Leer documentación y coordinar con manager