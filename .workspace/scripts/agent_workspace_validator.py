#!/usr/bin/env python3
"""
🤖 VALIDADOR WORKSPACE PARA AGENTES
Script que TODOS los agentes deben ejecutar antes de modificar archivos
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Archivos protegidos nivel crítico
PROTECTED_FILES = {
    "app/main.py": "system-architect-ai",
    "frontend/vite.config.ts": "frontend-performance-ai",
    "docker-compose.yml": "cloud-infrastructure-ai",
    "app/api/v1/deps/auth.py": "security-backend-ai",
    "app/services/auth_service.py": "security-backend-ai",
    "app/models/user.py": "database-architect-ai",
    "tests/conftest.py": "tdd-specialist",
    "app/core/config.py": "configuration-management",
    "app/database.py": "database-architect-ai"
}

def validate_workspace_access(agent_name, target_file):
    """Validar que agente tenga derecho a modificar archivo"""
    print(f"🔍 Validando acceso de {agent_name} a {target_file}")

    # 1. Verificar si archivo está protegido
    if target_file in PROTECTED_FILES:
        responsible_agent = PROTECTED_FILES[target_file]

        if agent_name != responsible_agent and agent_name != "master-orchestrator":
            print(f"❌ ACCESO DENEGADO")
            print(f"📁 Archivo: {target_file}")
            print(f"🛡️  Protegido por: {responsible_agent}")
            print(f"🤖 Agente solicitante: {agent_name}")
            print(f"✅ Solución: Consultar con {responsible_agent} primero")
            return False

    # 2. Verificar que existan metadatos
    metadata_file = f".workspace/project/{target_file}.md"
    if not os.path.exists(metadata_file):
        print(f"⚠️  Archivo sin metadatos: {target_file}")
        print(f"📋 Se requiere: {metadata_file}")

    # 3. Leer reglas específicas del archivo
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as f:
            content = f.read()
            if "PROTEGIDO CRÍTICO" in content:
                print(f"🚨 ARCHIVO NIVEL CRÍTICO: {target_file}")
            if "NO MODIFICAR" in content:
                print(f"❌ MODIFICACIÓN EXPLÍCITAMENTE PROHIBIDA")
                return False

    print(f"✅ Acceso autorizado para {agent_name}")
    return True

def log_agent_activity(agent_name, action, target_file, approved_by=None):
    """Registrar actividad del agente"""
    log_dir = ".workspace/logs"
    os.makedirs(log_dir, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    log_file = f"{log_dir}/agent_activity_{today}.json"

    activity = {
        "timestamp": datetime.now().isoformat(),
        "agent": agent_name,
        "action": action,
        "file": target_file,
        "approved_by": approved_by,
        "status": "authorized" if approved_by or agent_name == "master-orchestrator" else "self-authorized"
    }

    # Leer log existente o crear nuevo
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            logs = json.load(f)
    else:
        logs = []

    logs.append(activity)

    # Escribir log actualizado
    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=2)

    print(f"📝 Actividad registrada en {log_file}")

def check_workspace_compliance():
    """Verificar que agente haya leído documentos obligatorios"""
    required_docs = [
        ".workspace/SYSTEM_RULES.md",
        ".workspace/PROTECTED_FILES.md",
        ".workspace/AGENT_PROTOCOL.md"
    ]

    print("📚 Verificando lectura de documentos obligatorios...")

    for doc in required_docs:
        if not os.path.exists(doc):
            print(f"❌ DOCUMENTO FALTANTE: {doc}")
            return False
        print(f"✅ {doc} - Disponible")

    return True

def generate_commit_template(agent_name, target_file, approved_by=None):
    """Generar template de commit obligatorio"""
    template = f"""feat(workspace): Modificación autorizada de {target_file}

Workspace-Check: ✅ Consultado
Archivo: {target_file}
Agente: {agent_name}
Protocolo: {"APROBACIÓN_OBTENIDA" if approved_by else "SEGUIDO"}
Tests: PENDING
{"Responsable: " + approved_by if approved_by else ""}

Cambios realizados:
- TODO: Describir qué se modificó
- TODO: Explicar por qué era necesario
- TODO: Listar qué se probó después
"""

    print("📋 TEMPLATE DE COMMIT OBLIGATORIO:")
    print("-" * 50)
    print(template)
    print("-" * 50)

    # Guardar template para uso posterior
    with open(".workspace/logs/last_commit_template.txt", "w") as f:
        f.write(template)

def main():
    """Función principal del validador"""
    if len(sys.argv) < 3:
        print("❌ Uso: python agent_workspace_validator.py <agent_name> <target_file>")
        print("🔧 Ejemplo: python agent_workspace_validator.py backend-framework-ai app/main.py")
        sys.exit(1)

    agent_name = sys.argv[1]
    target_file = sys.argv[2]
    approved_by = sys.argv[3] if len(sys.argv) > 3 else None

    print(f"🚨 VALIDADOR WORKSPACE ACTIVADO")
    print(f"🤖 Agente: {agent_name}")
    print(f"📁 Archivo objetivo: {target_file}")
    print("-" * 50)

    # 1. Verificar compliance básico
    if not check_workspace_compliance():
        print("❌ WORKSPACE NO CONFIGURADO CORRECTAMENTE")
        sys.exit(1)

    # 2. Validar acceso del agente
    if not validate_workspace_access(agent_name, target_file):
        print("❌ ACCESO DENEGADO - CONSULTE CON AGENTE RESPONSABLE")
        sys.exit(1)

    # 3. Registrar actividad
    log_agent_activity(agent_name, "file_access_request", target_file, approved_by)

    # 4. Generar template de commit
    generate_commit_template(agent_name, target_file, approved_by)

    print("✅ VALIDACIÓN COMPLETADA - PUEDE PROCEDER")
    print("📋 Use el template de commit generado")
    print("🧪 RECUERDE: Ejecutar tests después de modificar")

if __name__ == "__main__":
    main()