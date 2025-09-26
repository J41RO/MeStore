#!/usr/bin/env python3
"""
🔍 VERIFICADOR DE ESTADO DE DELEGACIONES
Monitorea el estado de solicitudes de delegación automática
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

class DelegationStatusChecker:
    def __init__(self):
        self.requests_dir = ".workspace/requests"
        self.logs_dir = ".workspace/logs"

    def check_request_status(self, request_id):
        """Verificar estado específico de una solicitud"""
        request_file = f"{self.requests_dir}/delegation_{request_id}.json"

        if not os.path.exists(request_file):
            return {"error": f"❌ Request {request_id} no encontrado"}

        with open(request_file, 'r') as f:
            delegation = json.load(f)

        # Calcular tiempo transcurrido
        start_time = datetime.fromisoformat(delegation["timestamp"])
        elapsed_time = datetime.now() - start_time
        elapsed_minutes = int(elapsed_time.total_seconds() / 60)

        # Verificar timeout de escalación
        escalation_time = datetime.fromisoformat(delegation["escalation_timeout"])
        time_to_escalation = escalation_time - datetime.now()
        minutes_to_escalation = max(0, int(time_to_escalation.total_seconds() / 60))

        return {
            "request_id": request_id,
            "status": delegation["status"],
            "requesting_agent": delegation["requesting_agent"],
            "responsible_agent": delegation["responsible_agent"],
            "target_file": delegation["target_file"],
            "elapsed_minutes": elapsed_minutes,
            "minutes_to_escalation": minutes_to_escalation,
            "delegation_chain": delegation.get("delegation_chain", []),
            "activation_file": delegation.get("activation_file"),
            "priority": delegation.get("priority", "NORMAL")
        }

    def list_active_delegations(self):
        """Listar todas las delegaciones activas"""
        if not os.path.exists(self.requests_dir):
            return []

        active_delegations = []

        for file in os.listdir(self.requests_dir):
            if file.startswith("delegation_") and file.endswith(".json"):
                try:
                    with open(f"{self.requests_dir}/{file}", 'r') as f:
                        delegation = json.load(f)

                    if delegation["status"] in ["DELEGATED", "AGENT_ACTIVATED", "ESCALATED_TO_BACKUP"]:
                        active_delegations.append({
                            "request_id": delegation["request_id"],
                            "status": delegation["status"],
                            "responsible_agent": delegation["responsible_agent"],
                            "target_file": delegation["target_file"],
                            "timestamp": delegation["timestamp"],
                            "priority": delegation.get("priority", "NORMAL")
                        })
                except Exception as e:
                    print(f"⚠️ Error leyendo {file}: {e}")

        return sorted(active_delegations, key=lambda x: x["timestamp"], reverse=True)

    def get_agent_workload(self, agent_name):
        """Obtener carga de trabajo de un agente específico"""
        active_delegations = self.list_active_delegations()

        agent_requests = [
            d for d in active_delegations
            if d["responsible_agent"] == agent_name
        ]

        return {
            "agent": agent_name,
            "active_requests": len(agent_requests),
            "requests": agent_requests,
            "status": "BUSY" if len(agent_requests) > 0 else "AVAILABLE"
        }

    def display_status_dashboard(self):
        """Mostrar dashboard completo de delegaciones"""
        print("🔍 DASHBOARD DE DELEGACIONES AUTOMÁTICAS")
        print("=" * 70)

        active_delegations = self.list_active_delegations()

        if not active_delegations:
            print("✅ No hay delegaciones activas en este momento")
            return

        print(f"📊 TOTAL ACTIVAS: {len(active_delegations)}")
        print("")

        for delegation in active_delegations:
            start_time = datetime.fromisoformat(delegation["timestamp"])
            elapsed = datetime.now() - start_time
            elapsed_minutes = int(elapsed.total_seconds() / 60)

            status_emoji = {
                "DELEGATED": "🟡",
                "AGENT_ACTIVATED": "🟠",
                "ESCALATED_TO_BACKUP": "🔴"
            }.get(delegation["status"], "⚪")

            priority_emoji = {
                "CRÍTICA": "🚨",
                "ALTA": "⚠️",
                "NORMAL": "ℹ️"
            }.get(delegation["priority"], "ℹ️")

            print(f"{status_emoji} {delegation['request_id']}")
            print(f"   📁 {delegation['target_file']}")
            print(f"   🤖 {delegation['responsible_agent']}")
            print(f"   {priority_emoji} {delegation['priority']}")
            print(f"   ⏰ {elapsed_minutes} min transcurridos")
            print("")

    def check_escalations_needed(self):
        """Verificar qué solicitudes necesitan escalación"""
        escalations_needed = []

        for file in os.listdir(self.requests_dir):
            if file.startswith("delegation_") and file.endswith(".json"):
                try:
                    with open(f"{self.requests_dir}/{file}", 'r') as f:
                        delegation = json.load(f)

                    if delegation["status"] == "AGENT_ACTIVATED":
                        escalation_time = datetime.fromisoformat(delegation["escalation_timeout"])
                        if datetime.now() > escalation_time:
                            escalations_needed.append(delegation)

                except Exception as e:
                    continue

        return escalations_needed

def main():
    """Función principal del verificador"""
    checker = DelegationStatusChecker()

    if len(sys.argv) == 1:
        # Sin argumentos, mostrar dashboard
        checker.display_status_dashboard()

    elif len(sys.argv) == 2:
        command_or_id = sys.argv[1]

        if command_or_id == "dashboard":
            checker.display_status_dashboard()

        elif command_or_id == "escalations":
            escalations = checker.check_escalations_needed()
            if escalations:
                print("🚨 ESCALACIONES NECESARIAS:")
                for esc in escalations:
                    print(f"   - {esc['request_id']}: {esc['responsible_agent']} → {esc.get('backup_agent', 'master-orchestrator')}")
            else:
                print("✅ No hay escalaciones pendientes")

        elif command_or_id.startswith("REQ_"):
            # Es un request ID específico
            result = checker.check_request_status(command_or_id)

            if "error" in result:
                print(result["error"])
                return

            print(f"📋 ESTADO DE DELEGACIÓN: {result['request_id']}")
            print("=" * 50)
            print(f"🔄 Estado: {result['status']}")
            print(f"📤 Solicitante: {result['requesting_agent']}")
            print(f"📥 Responsable: {result['responsible_agent']}")
            print(f"📁 Archivo: {result['target_file']}")
            print(f"⏰ Tiempo transcurrido: {result['elapsed_minutes']} minutos")
            print(f"⏳ Minutos para escalación: {result['minutes_to_escalation']}")
            print(f"🎯 Prioridad: {result['priority']}")

            if result.get("activation_file"):
                print(f"📂 Archivo de activación: {result['activation_file']}")

            if len(result['delegation_chain']) > 2:
                print(f"🔄 Cadena de delegación: {' → '.join(result['delegation_chain'])}")

        else:
            # Verificar carga de trabajo de agente
            workload = checker.get_agent_workload(command_or_id)
            print(f"👤 CARGA DE TRABAJO: {workload['agent']}")
            print(f"📊 Estado: {workload['status']}")
            print(f"📋 Solicitudes activas: {workload['active_requests']}")

            if workload['requests']:
                print("\n📄 DETALLES:")
                for req in workload['requests']:
                    print(f"   • {req['request_id']}: {req['target_file']}")

    else:
        print("❌ Uso incorrecto")
        print("✅ Usos válidos:")
        print("   python check_delegation_status.py                    # Dashboard general")
        print("   python check_delegation_status.py REQ_12345         # Estado específico")
        print("   python check_delegation_status.py system-architect-ai # Carga de agente")
        print("   python check_delegation_status.py escalations       # Ver escalaciones")

if __name__ == "__main__":
    main()