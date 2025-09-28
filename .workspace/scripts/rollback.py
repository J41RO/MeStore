#!/usr/bin/env python3
"""
Sistema de Rollback para Desarrollo con IA
Restaura funcionalidades a un estado anterior funcional
"""
import os
import shutil
import json
import glob
from datetime import datetime

def list_snapshots():
    snapshots = []
    for dir_name in glob.glob(".workspace/snapshots/*/"):
        metadata_file = os.path.join(dir_name, "metadata.json")
        if os.path.exists(metadata_file):
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
                snapshots.append(metadata)

    snapshots.sort(key=lambda x: x["timestamp"], reverse=True)
    return snapshots

def rollback_to_snapshot(snapshot_id):
    snapshot_dir = f".workspace/snapshots/{snapshot_id}"
    metadata_file = f"{snapshot_dir}/metadata.json"

    if not os.path.exists(metadata_file):
        print(f"❌ Snapshot {snapshot_id} no encontrado")
        return False

    with open(metadata_file, "r") as f:
        metadata = json.load(f)

    print(f"🔄 Restaurando a snapshot: {metadata['feature_name']}")
    print(f"📝 Descripción: {metadata['description']}")
    print(f"👤 Agente: {metadata['agent_name']}")
    print(f"📅 Fecha: {metadata['timestamp']}")

    # Crear backup del estado actual antes de restaurar
    current_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f".workspace/snapshots/backup_before_rollback_{current_timestamp}"
    os.makedirs(backup_dir, exist_ok=True)

    # Restaurar archivos
    restored_files = []
    for file_path in metadata["files_backed_up"]:
        if file_path.startswith("frontend/"):
            backup_file = f"{snapshot_dir}/frontend_{os.path.basename(file_path)}"
        elif file_path.startswith("app/"):
            backup_file = f"{snapshot_dir}/backend_{os.path.basename(file_path)}"
        elif file_path.endswith(".db"):
            backup_file = f"{snapshot_dir}/database_backup.db"
        elif file_path in ["app/main.py", "frontend/vite.config.ts", "docker-compose.yml"]:
            backup_file = f"{snapshot_dir}/config_{os.path.basename(file_path)}"
        else:
            continue

        if os.path.exists(backup_file):
            # Crear backup del estado actual antes de restaurar
            if os.path.exists(file_path):
                current_backup = f"{backup_dir}/{os.path.basename(file_path)}.before_rollback"
                shutil.copy2(file_path, current_backup)

            # Restaurar archivo
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            shutil.copy2(backup_file, file_path)
            restored_files.append(file_path)
            print(f"✅ Restaurado: {file_path}")
        else:
            print(f"⚠️ Backup no encontrado: {backup_file}")

    # Log del rollback
    os.makedirs(".workspace/deployment-history", exist_ok=True)
    with open(".workspace/deployment-history/history.log", "a") as f:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        f.write(f"{timestamp} | ROLLBACK | {metadata['feature_name']} | system | Restored to {snapshot_id}\n")

    print(f"\n✅ Rollback completado a {snapshot_id}")
    print(f"📁 Backup del estado anterior en: {backup_dir}")
    print(f"📝 Archivos restaurados: {len(restored_files)}")
    return True

def show_snapshot_details(snapshot_id):
    snapshot_dir = f".workspace/snapshots/{snapshot_id}"
    metadata_file = f"{snapshot_dir}/metadata.json"

    if not os.path.exists(metadata_file):
        print(f"❌ Snapshot {snapshot_id} no encontrado")
        return

    with open(metadata_file, "r") as f:
        metadata = json.load(f)

    print(f"\n📋 DETALLES DEL SNAPSHOT: {snapshot_id}")
    print(f"🎯 Feature: {metadata['feature_name']}")
    print(f"📝 Descripción: {metadata['description']}")
    print(f"👤 Agente: {metadata['agent_name']}")
    print(f"📅 Fecha: {metadata['timestamp']}")
    print(f"📁 Archivos respaldados:")
    for file in metadata["files_backed_up"]:
        print(f"   - {file}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 2:
        if sys.argv[1] == "details" and len(sys.argv) >= 3:
            show_snapshot_details(sys.argv[2])
        else:
            snapshot_id = sys.argv[1]
            rollback_to_snapshot(snapshot_id)
    else:
        print("🔄 SISTEMA DE ROLLBACK - SNAPSHOTS DISPONIBLES:")
        print("=" * 60)
        snapshots = list_snapshots()
        if not snapshots:
            print("❌ No hay snapshots disponibles")
        else:
            for i, snap in enumerate(snapshots[:10]):
                print(f"{i+1:2d}. {snap['snapshot_id']}")
                print(f"    🎯 {snap['feature_name']}")
                print(f"    📝 {snap['description']}")
                print(f"    👤 {snap['agent_name']} | 📅 {snap['timestamp']}")
                print()

        print("💡 USO:")
        print("  python rollback.py <snapshot_id>     - Restaurar snapshot")
        print("  python rollback.py details <id>      - Ver detalles del snapshot")
        print("  python rollback.py                   - Listar snapshots disponibles")