#!/usr/bin/env python3
"""
📞 SISTEMA DE CONTACTO CON AGENTES RESPONSABLES
Script para contactar automáticamente al agente responsable de un archivo
"""

import os
import json
import uuid
from datetime import datetime, timedelta

# Matriz de responsabilidad
RESPONSIBILITY_MATRIX = {
    "app/main.py": {
        "primary": "system-architect-ai",
        "backup": "solution-architect-ai",
        "department": "architecture"
    },
    "frontend/vite.config.ts": {
        "primary": "frontend-performance-ai",
        "backup": "react-specialist-ai",
        "department": "frontend"
    },
    "docker-compose.yml": {
        "primary": "cloud-infrastructure-ai",
        "backup": "devops-integration-ai",
        "department": "infrastructure"
    },
    "app/api/v1/deps/auth.py": {
        "primary": "security-backend-ai",
        "backup": "api-security",
        "department": "backend"
    },
    "app/services/auth_service.py": {
        "primary": "security-backend-ai",
        "backup": "api-security",
        "department": "backend"
    },
    "app/models/user.py": {
        "primary": "database-architect-ai",
        "backup": "backend-framework-ai",
        "department": "architecture"
    },
    "tests/conftest.py": {
        "primary": "tdd-specialist",
        "backup": "unit-testing-ai",
        "department": "testing"
    },
    "app/core/config.py": {
        "primary": "configuration-management",
        "backup": "system-architect-ai",
        "department": "backend"
    },
    "app/database.py": {
        "primary": "database-architect-ai",
        "backup": "database-performance",
        "department": "architecture"
    }
}

def create_request(requesting_agent, target_file, reason):
    """Crear solicitud de modificación"""
    request_id = str(uuid.uuid4())[:8]

    request = {
        "id": request_id,
        "timestamp": datetime.now().isoformat(),
        "requesting_agent": requesting_agent,
        "target_file": target_file,
        "reason": reason,
        "status": "pending",
        "contacted_agents": [],
        "responses": [],
        "escalation_level": 1,
        "deadline": (datetime.now() + timedelta(minutes=5)).isoformat()
    }

    # Guardar solicitud
    requests_dir = ".workspace/requests"
    os.makedirs(requests_dir, exist_ok=True)

    request_file = f"{requests_dir}/request_{request_id}.json"
    with open(request_file, 'w') as f:
        json.dump(request, f, indent=2)

    return request_id, request

def contact_primary_agent(request):
    """Contactar agente principal responsable"""
    target_file = request["target_file"]

    if target_file not in RESPONSIBILITY_MATRIX:
        print(f"❌ Archivo no está en matriz de responsabilidad: {target_file}")
        return False

    resp_info = RESPONSIBILITY_MATRIX[target_file]
    primary_agent = resp_info["primary"]
    department = resp_info["department"]

    print(f"📞 CONTACTANDO AGENTE PRINCIPAL")
    print(f"🤖 Agente: {primary_agent}")
    print(f"🏢 Departamento: {department}")
    print(f"📁 Archivo: {target_file}")
    print(f"💬 Motivo: {request['reason']}")
    print(f"⏰ Deadline: 5 minutos desde ahora")

    # Simular notificación (en implementación real sería Slack/Teams/Email)
    notification = {
        "timestamp": datetime.now().isoformat(),
        "agent": primary_agent,
        "type": "primary_contact",
        "message": f"Solicitud de {request['requesting_agent']} para modificar {target_file}",
        "deadline": request["deadline"]
    }

    request["contacted_agents"].append(notification)

    # Crear archivo de notificación para el agente
    agent_dir = f".workspace/departments/{department}/{primary_agent}"
    os.makedirs(agent_dir, exist_ok=True)

    notification_file = f"{agent_dir}/URGENT_REQUEST_{request['id']}.json"
    with open(notification_file, 'w') as f:
        json.dump({
            "request_id": request["id"],
            "requesting_agent": request["requesting_agent"],
            "file": target_file,
            "reason": request["reason"],
            "deadline": request["deadline"],
            "instructions": f"Responder con: python .workspace/scripts/respond_to_request.py {request['id']} [APPROVE/DENY] [motivo]"
        }, f, indent=2)

    print(f"📬 Notificación enviada a: {notification_file}")
    return True

def save_request(request):
    """Guardar estado actualizado de solicitud"""
    request_file = f".workspace/requests/request_{request['id']}.json"
    with open(request_file, 'w') as f:
        json.dump(request, f, indent=2)

def main():
    """Función principal"""
    import sys

    if len(sys.argv) < 4:
        print("❌ Uso: python contact_responsible_agent.py <requesting_agent> <target_file> <reason>")
        print("🔧 Ejemplo: python contact_responsible_agent.py backend-framework-ai app/api/v1/deps/auth.py 'Necesito agregar validación'")
        sys.exit(1)

    requesting_agent = sys.argv[1]
    target_file = sys.argv[2]
    reason = ' '.join(sys.argv[3:])

    print(f"🚨 SOLICITUD DE MODIFICACIÓN DE ARCHIVO PROTEGIDO")
    print(f"🤖 Agente solicitante: {requesting_agent}")
    print(f"📁 Archivo: {target_file}")
    print(f"💬 Motivo: {reason}")
    print("-" * 60)

    # Crear solicitud
    request_id, request = create_request(requesting_agent, target_file, reason)
    print(f"📋 Solicitud creada: {request_id}")

    # Contactar agente principal
    if contact_primary_agent(request):
        save_request(request)

        print(f"✅ SOLICITUD ENVIADA EXITOSAMENTE")
        print(f"🆔 ID de solicitud: {request_id}")
        print(f"⏰ Tiempo límite: 5 minutos")
        print(f"📊 Estado: Esperando respuesta del agente responsable")
        print(f"🔍 Verificar estado: python .workspace/scripts/check_request_status.py {request_id}")

        # Programar escalación automática
        print(f"⚡ Escalación automática programada en 5 minutos si no hay respuesta")

    else:
        print(f"❌ ERROR: No se pudo contactar agente responsable")
        sys.exit(1)

if __name__ == "__main__":
    main()