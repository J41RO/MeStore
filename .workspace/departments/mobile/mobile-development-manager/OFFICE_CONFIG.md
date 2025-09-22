# 🤖 CONFIGURACIÓN DE OFICINA: mobile-development-manager

## 📍 UBICACIÓN
- **Departamento**: mobile
- **Agente**: mobile-development-manager
- **Oficina**: .workspace/departments/mobile/mobile-development-manager/

## 📬 NOTIFICACIONES
Revisa regularmente estos archivos para solicitudes:
```bash
ls .workspace/departments/mobile/mobile-development-manager/URGENT_REQUEST_*.json
```

## 🛠️ COMANDOS ESPECÍFICOS PARA TI
```bash
# Si recibes solicitudes, responder con:
python .workspace/scripts/respond_to_request.py [request-id] [APPROVE/DENY] "[motivo]"

# Para solicitar modificaciones:
python .workspace/scripts/contact_responsible_agent.py mobile-development-manager [archivo] "[motivo]"

# Validar antes de modificar:
python .workspace/scripts/agent_workspace_validator.py mobile-development-manager [archivo]
```

## 📚 DOCUMENTACIÓN OBLIGATORIA
- 📋 LEER PRIMERO: ./QUICK_START_GUIDE.md
- 📖 Reglas globales: ../../SYSTEM_RULES.md
- 🛡️ Archivos protegidos: ../../PROTECTED_FILES.md
- 👥 Responsables: ../../RESPONSIBLE_AGENTS.md

---
**🔄 Actualizado automáticamente por distribute_instructions.py**
