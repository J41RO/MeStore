# PROTOCOLO DE DESARROLLO CON IA - OBLIGATORIO PARA TODOS LOS AGENTES

## 🚨 REGLA FUNDAMENTAL
**NUNCA modificar funcionalidades que YA ESTÁN FUNCIONANDO sin crear snapshot primero**

## 🔄 FLUJO OBLIGATORIO PARA CLAUDE CODE Y TODOS LOS AGENTES

### 1. ANTES de cualquier modificación que pueda afectar funcionalidad existente:
```bash
python .workspace/scripts/create_snapshot.py "feature_name_working" "Descripción del estado funcional" "nombre-agente"
```

### 2. DESPUÉS de implementar nueva funcionalidad Y CONFIRMAR QUE FUNCIONA:
```bash
python .workspace/scripts/create_snapshot.py "feature_name_enhanced" "Nueva funcionalidad agregada y funcionando" "nombre-agente"
```

### 3. SI algo se rompe, ROLLBACK inmediato:
```bash
python .workspace/scripts/rollback.py <snapshot_id_que_funcionaba>
```

## 🎯 PUNTOS DE CONTROL CRÍTICOS

### Frontend:
- **UserManagement.tsx** - Componente principal que DEBE mostrar usuarios
- **URLs de endpoints** - Deben mantenerse funcionando
- **Autenticación** - Nunca romper login admin
- **Navegación** - Portal administrativo accesible

### Backend:
- **superuser_admin.py** - Endpoints que funcionan
- **auth.py** - Sistema de autenticación
- **user.py** - Modelo de usuarios (NO crear duplicados)

### Base de datos:
- **mestore_development.db** - Nunca corromper datos existentes
- **Usuarios reales** - Preservar datos que ya están funcionando

## 🤝 COMUNICACIÓN ENTRE AGENTES

### Antes de modificar:
1. ✅ Verificar qué está funcionando actualmente
2. ✅ Crear snapshot del estado funcional
3. ✅ Documentar exactamente qué se va a cambiar
4. ✅ Hacer cambios incrementales
5. ✅ Probar después de cada cambio
6. ❌ Si algo falla, rollback inmediato

### Historial de cambios:
- `.workspace/deployment-history/history.log` - Log completo
- `.workspace/snapshots/` - Estados funcionales guardados
- `.workspace/rollback-points/` - Puntos de restauración rápida

## 📋 COMANDOS OBLIGATORIOS

### Crear snapshot (OBLIGATORIO antes de modificar):
```bash
python .workspace/scripts/create_snapshot.py "user_management_working" "UserManagement mostrando usuarios reales correctamente" "claude-code"
```

### Ver snapshots disponibles:
```bash
python .workspace/scripts/rollback.py
```

### Restaurar funcionalidad (si algo se rompe):
```bash
python .workspace/scripts/rollback.py 20250927_123456_user_management_working
```

### Ver detalles de un snapshot:
```bash
python .workspace/scripts/rollback.py details 20250927_123456_user_management_working
```

## 🚨 PROTOCOLO DE EMERGENCIA

### Si UserManagement no muestra usuarios:
1. ✅ Verificar endpoint: `GET /api/v1/superuser-admin/users`
2. ✅ Verificar autenticación admin funciona
3. ✅ Crear snapshot del estado roto para diagnóstico
4. ✅ Rollback al último snapshot funcional
5. ✅ Investigar qué cambió entre snapshots

### Si portal admin no es accesible:
1. ✅ Verificar NavigationProvider (no useCallback en useMemo)
2. ✅ Verificar rutas: `/admin-portal` → `/admin-login` → `/admin-secure-portal`
3. ✅ Rollback a snapshot funcional
4. ✅ Aplicar cambios incrementalmente

## 📞 RESPONSABILIDADES POR AGENTE

### Claude Code (por defecto):
- ✅ Crear snapshots antes de cualquier modificación
- ✅ Verificar que funcionalidades existentes siguen funcionando
- ✅ Rollback inmediato si algo se rompe

### Agentes especializados:
- ✅ Consultar `.workspace/PROTECTED_FILES.md` antes de modificar
- ✅ Crear snapshot del estado funcional antes de trabajar
- ✅ Documentar cambios en commits con template obligatorio
- ✅ Verificar funcionalidad después de cambios

## 💾 TEMPLATE DE COMMITS CON SNAPSHOTS
```
tipo(área): descripción breve

Snapshot-Before: snapshot_id_antes_del_cambio
Snapshot-After: snapshot_id_despues_del_cambio
Functionality-Verified: [WORKING/BROKEN]
Admin-Portal-Access: [VERIFIED/BROKEN]
User-Data-Visible: [YES/NO]
Rollback-Available: [YES/snapshot_id]

Descripción detallada del cambio...
```

## 🎯 OBJETIVOS DEL SISTEMA

1. **Preservar funcionalidades**: Lo que funciona, SIGUE funcionando
2. **Desarrollo incremental**: Agregar sin romper
3. **Rollback rápido**: Restaurar estado funcional en segundos
4. **Historial completo**: Trazabilidad de todos los cambios
5. **Coordinación de agentes**: Evitar conflictos entre modificaciones

## 🔥 REGLAS DE ORO

1. **Snapshot SIEMPRE antes de modificar**
2. **Verificar funcionalidad DESPUÉS de cada cambio**
3. **Rollback INMEDIATO si algo falla**
4. **NUNCA commitear código que rompe funcionalidad existente**
5. **Comunicar cambios en commits con snapshots referenciados**

---

**⚡ ESTE PROTOCOLO ES OBLIGATORIO PARA TODOS LOS AGENTES**
**📋 CUALQUIER VIOLACIÓN SERÁ ESCALADA AL MASTER-ORCHESTRATOR**