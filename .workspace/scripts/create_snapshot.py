#!/usr/bin/env python3
"""
Sistema de Snapshots para Desarrollo con IA
Crea puntos de control cuando funcionalidades están operativas
"""
import os
import shutil
import json
import sqlite3
from datetime import datetime
import subprocess

def create_snapshot(feature_name, description, agent_name="manual"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_id = f"{timestamp}_{feature_name}"

    snapshot_dir = f".workspace/snapshots/{snapshot_id}"
    os.makedirs(snapshot_dir, exist_ok=True)

    # Metadata del snapshot
    metadata = {
        "snapshot_id": snapshot_id,
        "feature_name": feature_name,
        "description": description,
        "agent_name": agent_name,
        "timestamp": datetime.now().isoformat(),
        "status": "working",
        "files_backed_up": []
    }

    print(f"📸 Creando snapshot: {feature_name}")

    # Backup frontend crítico
    frontend_files = [
        "frontend/src/pages/admin/UserManagement.tsx",
        "frontend/src/hooks/admin/useUserManagement.ts",
        "frontend/src/components/admin/UserDataTable.tsx",
        "frontend/src/components/admin/UserDetailsModal.tsx",
        "frontend/src/components/admin/UserCreateModal.tsx",
        "frontend/src/services/superuserService.ts"
    ]

    for file in frontend_files:
        if os.path.exists(file):
            dest = f"{snapshot_dir}/frontend_{os.path.basename(file)}"
            shutil.copy2(file, dest)
            metadata["files_backed_up"].append(file)
            print(f"✅ Frontend: {file}")

    # Backup backend crítico
    backend_files = [
        "app/api/v1/endpoints/superuser_admin.py",
        "app/api/v1/endpoints/superuser_admin_users.py",
        "app/api/v1/endpoints/user_management_enterprise.py",
        "app/api/v1/endpoints/auth.py",
        "app/api/v1/endpoints/secure_auth.py",
        "app/services/superuser_service.py",
        "app/models/user.py",
        "app/schemas/user.py"
    ]

    for file in backend_files:
        if os.path.exists(file):
            dest = f"{snapshot_dir}/backend_{os.path.basename(file)}"
            shutil.copy2(file, dest)
            metadata["files_backed_up"].append(file)
            print(f"✅ Backend: {file}")

    # Backup estructura de BD
    if os.path.exists("mestore_development.db"):
        shutil.copy2("mestore_development.db", f"{snapshot_dir}/database_backup.db")
        metadata["files_backed_up"].append("mestore_development.db")
        print("✅ Database: mestore_development.db")

    # Backup de configuraciones críticas
    config_files = [
        "app/main.py",
        "frontend/vite.config.ts",
        "docker-compose.yml"
    ]

    for file in config_files:
        if os.path.exists(file):
            dest = f"{snapshot_dir}/config_{os.path.basename(file)}"
            shutil.copy2(file, dest)
            metadata["files_backed_up"].append(file)
            print(f"✅ Config: {file}")

    # Guardar metadata
    with open(f"{snapshot_dir}/metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    # Registrar en historial
    os.makedirs(".workspace/deployment-history", exist_ok=True)
    with open(".workspace/deployment-history/history.log", "a") as f:
        f.write(f"{timestamp} | SNAPSHOT | {feature_name} | {agent_name} | {description}\n")

    print(f"📋 Snapshot creado: {snapshot_id}")
    print(f"📁 Ubicación: {snapshot_dir}")
    return snapshot_id

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        feature = sys.argv[1]
        description = sys.argv[2]
        agent = sys.argv[3] if len(sys.argv) > 3 else "manual"
        create_snapshot(feature, description, agent)
    else:
        print("Uso: python create_snapshot.py <feature_name> <description> [agent_name]")
        print("Ejemplo: python create_snapshot.py user_management_working 'UserManagement mostrando usuarios correctamente' claude-code")