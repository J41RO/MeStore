#!/usr/bin/env python3
"""
✅ SISTEMA DE RESPUESTA PARA AGENTES RESPONSABLES
Script para que agentes responsables aprueben/rechacen solicitudes
"""

import os
import json
from datetime import datetime

def load_request(request_id):
    """Cargar solicitud por ID"""
    request_file = f".workspace/requests/request_{request_id}.json"

    if not os.path.exists(request_file):
        print(f"❌ Solicitud no encontrada: {request_id}")
        return None

    with open(request_file, 'r') as f:
        return json.load(f)

def save_request(request):
    """Guardar solicitud actualizada"""
    request_file = f".workspace/requests/request_{request['id']}.json"
    with open(request_file, 'w') as f:
        json.dump(request, f, indent=2)

def approve_request(request, responding_agent, reason):
    """Aprobar solicitud"""
    response = {
        "timestamp": datetime.now().isoformat(),
        "agent": responding_agent,
        "decision": "APPROVED",
        "reason": reason
    }

    request["status"] = "approved"
    request["responses"].append(response)

    # Generar token de autorización
    auth_token = f"AUTH_{request['id']}_{responding_agent}"

    # Crear archivo de autorización para el agente solicitante
    requesting_agent = request["requesting_agent"]
    auth_file = f".workspace/authorizations/auth_{request['id']}.json"

    os.makedirs(".workspace/authorizations", exist_ok=True)
    with open(auth_file, 'w') as f:
        json.dump({
            "request_id": request["id"],
            "authorized_agent": requesting_agent,
            "target_file": request["target_file"],
            "authorized_by": responding_agent,
            "authorization_token": auth_token,
            "valid_until": datetime.now().isoformat(),
            "reason": reason,
            "instructions": f"Usar: python .workspace/scripts/agent_workspace_validator.py {requesting_agent} {request['target_file']} {responding_agent}"
        }, f, indent=2)

    print(f"✅ SOLICITUD APROBADA")
    print(f"🎫 Token de autorización: {auth_token}")
    print(f"📁 Archivo autorizado: {auth_file}")
    print(f"🤖 Agente autorizado: {requesting_agent}")
    print(f"📝 Motivo: {reason}")

    return auth_token

def deny_request(request, responding_agent, reason):
    """Rechazar solicitud"""
    response = {
        "timestamp": datetime.now().isoformat(),
        "agent": responding_agent,
        "decision": "DENIED",
        "reason": reason
    }

    request["status"] = "denied"
    request["responses"].append(response)

    print(f"❌ SOLICITUD RECHAZADA")
    print(f"🤖 Rechazada por: {responding_agent}")
    print(f"📝 Motivo: {reason}")
    print(f"💡 El agente solicitante debe considerar alternativas")

def notify_requesting_agent(request):
    """Notificar al agente solicitante sobre la respuesta"""
    requesting_agent = request["requesting_agent"]
    status = request["status"]

    # Crear notificación para el agente solicitante
    notification_dir = f".workspace/notifications/{requesting_agent}"
    os.makedirs(notification_dir, exist_ok=True)

    notification_file = f"{notification_dir}/response_{request['id']}.json"
    with open(notification_file, 'w') as f:
        json.dump({
            "request_id": request["id"],
            "status": status,
            "file": request["target_file"],
            "responses": request["responses"],
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)

    print(f"📬 Notificación enviada a: {notification_file}")

def main():
    """Función principal"""
    import sys

    if len(sys.argv) < 4:
        print("❌ Uso: python respond_to_request.py <request_id> <APPROVE/DENY> <reason>")
        print("🔧 Ejemplo: python respond_to_request.py abc123 APPROVE 'Cambio necesario para seguridad'")
        print("🔧 Ejemplo: python respond_to_request.py abc123 DENY 'Riesgo muy alto para este cambio'")
        sys.exit(1)

    request_id = sys.argv[1]
    decision = sys.argv[2].upper()
    reason = ' '.join(sys.argv[3:])

    if decision not in ["APPROVE", "DENY"]:
        print("❌ Decisión debe ser APPROVE o DENY")
        sys.exit(1)

    # Cargar solicitud
    request = load_request(request_id)
    if not request:
        sys.exit(1)

    # Verificar que no esté ya respondida
    if request["status"] != "pending":
        print(f"⚠️ Solicitud ya fue respondida: {request['status']}")
        print(f"📊 Respuestas previas: {len(request['responses'])}")
        return

    # Simular identificación del agente respondiente
    # En implementación real sería automático
    responding_agent = input("🤖 Ingrese su nombre de agente: ").strip()

    print(f"📋 PROCESANDO RESPUESTA")
    print(f"🆔 Solicitud: {request_id}")
    print(f"🤖 Respondiendo: {responding_agent}")
    print(f"📁 Archivo: {request['target_file']}")
    print(f"✅ Decisión: {decision}")
    print(f"📝 Motivo: {reason}")
    print("-" * 50)

    # Procesar decisión
    if decision == "APPROVE":
        auth_token = approve_request(request, responding_agent, reason)
    else:
        deny_request(request, responding_agent, reason)

    # Guardar solicitud actualizada
    save_request(request)

    # Notificar al agente solicitante
    notify_requesting_agent(request)

    print(f"✅ RESPUESTA PROCESADA EXITOSAMENTE")

    if decision == "APPROVE":
        print(f"🚀 El agente {request['requesting_agent']} puede proceder con la modificación")
        print(f"🔧 Comando autorizado:")
        print(f"   python .workspace/scripts/agent_workspace_validator.py {request['requesting_agent']} {request['target_file']} {responding_agent}")
    else:
        print(f"🛑 Modificación denegada. El agente debe considerar alternativas.")

if __name__ == "__main__":
    main()