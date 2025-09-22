# 🤖 CONFIGURACIÓN DE OFICINA: penetration-tester

## 📍 UBICACIÓN
- **Departamento**: security
- **Agente**: penetration-tester
- **Oficina**: .workspace/departments/security/penetration-tester/

## 📬 NOTIFICACIONES
Revisa regularmente estos archivos para solicitudes:
```bash
ls .workspace/departments/security/penetration-tester/URGENT_REQUEST_*.json
```

## 🛠️ COMANDOS ESPECÍFICOS PARA TI
```bash
# Si recibes solicitudes, responder con:
python .workspace/scripts/respond_to_request.py [request-id] [APPROVE/DENY] "[motivo]"

# Para solicitar modificaciones:
python .workspace/scripts/contact_responsible_agent.py penetration-tester [archivo] "[motivo]"

# Validar antes de modificar:
python .workspace/scripts/agent_workspace_validator.py penetration-tester [archivo]
```

## 📚 DOCUMENTACIÓN OBLIGATORIA
- 📋 LEER PRIMERO: ./QUICK_START_GUIDE.md
- 📖 Reglas globales: ../../SYSTEM_RULES.md
- 🛡️ Archivos protegidos: ../../PROTECTED_FILES.md
- 👥 Responsables: ../../RESPONSIBLE_AGENTS.md

---
**🔄 Actualizado automáticamente por distribute_instructions.py**
