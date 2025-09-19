# 🤖 REFERENCIA RÁPIDA PARA AGENTES

## 🚨 INFORMACIÓN CRÍTICA - LEER ANTES DE TRABAJAR

### 🌐 URLs del Sistema (NO CAMBIAR)
- **Backend**: `http://192.168.1.137:8000`
- **Frontend**: `http://192.168.1.137:5173`

### 👥 Usuarios de Prueba Existentes (NO DUPLICAR)
```
🔑 admin@test.com / admin123 (ADMIN) ✅
🔑 vendor@test.com / vendor123 (VENDOR) ✅
🔑 buyer@test.com / buyer123 (BUYER) ✅
```

### ⚠️ REGLAS OBLIGATORIAS
1. **NO cambiar** puertos ni URLs del sistema
2. **NO crear** usuarios con estos emails
3. **USAR estos usuarios** para pruebas de autenticación
4. **VERIFICAR existencia** antes de crear nuevos usuarios de prueba
5. **NO modificar** proxy Vite (está configurado para 192.168.1.137:8000)

### 🧪 Para Nuevos Usuarios de Prueba
- Formato: `test_[tipo]_[timestamp]@example.com`
- Solo cuando se pruebe flujo de registro
- Verificar antes de crear

### 🔧 Configuraciones Técnicas Críticas
- **Proxy Vite**: `target: "http://192.168.1.137:8000"` ✅ VERIFICADO
- **AuthStore**: `frontend/src/stores/authStore.ts` ✅ FUNCIONAL
- **Integración**: Frontend:5173 → Backend:8000 ✅ OPERATIVA

---
**Ver más detalles**:
- `.workspace/SYSTEM_CONFIG.md`
- `.workspace/TECHNICAL_REQUIREMENTS.md` 🔧 NUEVO