# 🤖 CONFIGURACIÓN DE OFICINA: e2e-testing-ai

## 📍 UBICACIÓN
- **Departamento**: testing
- **Agente**: e2e-testing-ai
- **Oficina**: .workspace/departments/testing/e2e-testing-ai/

## 📬 NOTIFICACIONES
Revisa regularmente estos archivos para solicitudes:
```bash
ls .workspace/departments/testing/e2e-testing-ai/URGENT_REQUEST_*.json
```

## 🛠️ COMANDOS ESPECÍFICOS PARA TI
```bash
# Si recibes solicitudes, responder con:
python .workspace/scripts/respond_to_request.py [request-id] [APPROVE/DENY] "[motivo]"

# Para solicitar modificaciones:
python .workspace/scripts/contact_responsible_agent.py e2e-testing-ai [archivo] "[motivo]"

# Validar antes de modificar:
python .workspace/scripts/agent_workspace_validator.py e2e-testing-ai [archivo]
```

## 📚 DOCUMENTACIÓN OBLIGATORIA
- 📋 LEER PRIMERO: ./QUICK_START_GUIDE.md
- 📖 Reglas globales: ../../SYSTEM_RULES.md
- 🛡️ Archivos protegidos: ../../PROTECTED_FILES.md
- 👥 Responsables: ../../RESPONSIBLE_AGENTS.md

---
**🔄 Actualizado automáticamente por distribute_instructions.py**
