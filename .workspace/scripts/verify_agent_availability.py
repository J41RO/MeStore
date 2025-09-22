#!/usr/bin/env python3
"""
🔍 VERIFICADOR DE DISPONIBILIDAD DE AGENTES
Script para verificar que todos los archivos protegidos tienen agentes responsables disponibles
"""

import os
import json
from datetime import datetime

# Matriz completa de responsabilidad
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
        "department": "architecture",
        "backup_department": "backend"
    },
    "tests/conftest.py": {
        "primary": "tdd-specialist",
        "backup": "unit-testing-ai",
        "department": "testing"
    },
    "app/core/config.py": {
        "primary": "configuration-management",
        "backup": "system-architect-ai",
        "department": "backend",
        "backup_department": "architecture"
    },
    "app/database.py": {
        "primary": "database-architect-ai",
        "backup": "database-performance",
        "department": "architecture"
    }
}

def check_agent_office_exists(agent_name, department):
    """Verificar que la oficina del agente existe"""
    office_path = f".workspace/departments/{department}/{agent_name}"
    return os.path.exists(office_path)

def check_metadata_exists(file_path):
    """Verificar que existen metadatos para el archivo"""
    metadata_path = f".workspace/project/{file_path}.md"
    return os.path.exists(metadata_path)

def check_metadata_has_contact_info(file_path):
    """Verificar que metadatos tienen información de contacto actualizada"""
    metadata_path = f".workspace/project/{file_path}.md"

    if not os.path.exists(metadata_path):
        return False

    with open(metadata_path, 'r') as f:
        content = f.read()

    # Verificar que tiene información de contacto actualizada
    has_contact_script = "contact_responsible_agent.py" in content
    has_backup_info = "Agente Backup" in content
    has_escalation = "Escalación" in content
    has_responsibility_chain = "CADENA DE RESPONSABILIDAD" in content

    return has_contact_script and has_backup_info and has_escalation and has_responsibility_chain

def generate_availability_report():
    """Generar reporte de disponibilidad de agentes"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_protected_files": len(RESPONSIBILITY_MATRIX),
        "files_status": {},
        "agents_status": {},
        "issues": [],
        "summary": {
            "fully_configured": 0,
            "missing_offices": 0,
            "missing_metadata": 0,
            "incomplete_metadata": 0
        }
    }

    print("🔍 VERIFICANDO DISPONIBILIDAD DE AGENTES RESPONSABLES")
    print("=" * 60)

    # Verificar cada archivo protegido
    for file_path, resp_info in RESPONSIBILITY_MATRIX.items():
        primary_agent = resp_info["primary"]
        backup_agent = resp_info["backup"]
        department = resp_info["department"]

        backup_dept = resp_info.get("backup_department", department)

        file_status = {
            "primary_agent": primary_agent,
            "backup_agent": backup_agent,
            "department": department,
            "backup_department": backup_dept,
            "primary_office_exists": check_agent_office_exists(primary_agent, department),
            "backup_office_exists": check_agent_office_exists(backup_agent, backup_dept),
            "metadata_exists": check_metadata_exists(file_path),
            "metadata_complete": check_metadata_has_contact_info(file_path),
            "status": "OK"
        }

        issues = []

        # Verificar oficina del agente principal
        if not file_status["primary_office_exists"]:
            issues.append(f"Oficina faltante: {primary_agent}")
            report["summary"]["missing_offices"] += 1

        # Verificar oficina del agente backup
        if not file_status["backup_office_exists"]:
            issues.append(f"Oficina backup faltante: {backup_agent}")

        # Verificar metadatos
        if not file_status["metadata_exists"]:
            issues.append("Metadatos faltantes")
            report["summary"]["missing_metadata"] += 1

        # Verificar metadatos completos
        if file_status["metadata_exists"] and not file_status["metadata_complete"]:
            issues.append("Metadatos incompletos (falta info contacto)")
            report["summary"]["incomplete_metadata"] += 1

        if issues:
            file_status["status"] = "ISSUES"
            file_status["issues"] = issues
            report["issues"].extend([f"{file_path}: {issue}" for issue in issues])
        else:
            report["summary"]["fully_configured"] += 1

        report["files_status"][file_path] = file_status

        # Status visual
        status_icon = "✅" if file_status["status"] == "OK" else "❌"
        print(f"{status_icon} {file_path}")
        print(f"   Principal: {primary_agent} ({'✅' if file_status['primary_office_exists'] else '❌'})")
        print(f"   Backup: {backup_agent} ({'✅' if file_status['backup_office_exists'] else '❌'})")
        print(f"   Metadatos: {'✅' if file_status['metadata_complete'] else '❌'}")

        if issues:
            for issue in issues:
                print(f"   🔸 {issue}")

    # Generar estadísticas de agentes
    agents_count = {}
    for resp_info in RESPONSIBILITY_MATRIX.values():
        primary = resp_info["primary"]
        backup = resp_info["backup"]

        agents_count[primary] = agents_count.get(primary, 0) + 1
        agents_count[backup] = agents_count.get(backup, 0) + 1

    report["agents_status"] = agents_count

    print("\n📊 RESUMEN")
    print("=" * 30)
    print(f"✅ Completamente configurados: {report['summary']['fully_configured']}")
    print(f"❌ Con problemas: {len(RESPONSIBILITY_MATRIX) - report['summary']['fully_configured']}")
    print(f"🏢 Oficinas faltantes: {report['summary']['missing_offices']}")
    print(f"📄 Metadatos faltantes: {report['summary']['missing_metadata']}")
    print(f"📝 Metadatos incompletos: {report['summary']['incomplete_metadata']}")

    if report["issues"]:
        print(f"\n🚨 PROBLEMAS DETECTADOS ({len(report['issues'])})")
        for issue in report["issues"]:
            print(f"   🔸 {issue}")

    # Guardar reporte
    reports_dir = ".workspace/reports"
    os.makedirs(reports_dir, exist_ok=True)

    report_file = f"{reports_dir}/agent_availability_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n📊 Reporte guardado: {report_file}")

    return report

def suggest_fixes(report):
    """Sugerir soluciones para problemas detectados"""
    if not report["issues"]:
        print("\n🎉 SISTEMA COMPLETAMENTE CONFIGURADO")
        return

    print("\n🔧 SOLUCIONES SUGERIDAS")
    print("=" * 30)

    # Agrupar problemas por tipo
    missing_offices = [issue for issue in report["issues"] if "Oficina faltante" in issue]
    missing_metadata = [issue for issue in report["issues"] if "Metadatos faltantes" in issue]
    incomplete_metadata = [issue for issue in report["issues"] if "Metadatos incompletos" in issue]

    if missing_offices:
        print("🏢 CREAR OFICINAS FALTANTES:")
        for issue in missing_offices:
            agent = issue.split(": Oficina faltante: ")[1]
            print(f"   mkdir -p .workspace/departments/*//{agent}/")

    if missing_metadata:
        print("\n📄 CREAR METADATOS FALTANTES:")
        for issue in missing_metadata:
            file_path = issue.split(": Metadatos faltantes")[0]
            print(f"   Crear: .workspace/project/{file_path}.md")

    if incomplete_metadata:
        print("\n📝 ACTUALIZAR METADATOS INCOMPLETOS:")
        for issue in incomplete_metadata:
            file_path = issue.split(": Metadatos incompletos")[0]
            print(f"   Actualizar: .workspace/project/{file_path}.md")
            print(f"   Agregar: info de contacto y cadena de responsabilidad")

def main():
    """Función principal"""
    print("🤖 VERIFICADOR DE DISPONIBILIDAD DE AGENTES RESPONSABLES")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    report = generate_availability_report()
    suggest_fixes(report)

    # Resultado final
    if not report["issues"]:
        print("\n✅ TODOS LOS ARCHIVOS PROTEGIDOS TIENEN AGENTES RESPONSABLES DISPONIBLES")
        return 0
    else:
        print(f"\n❌ {len(report['issues'])} PROBLEMAS DETECTADOS - REVISAR Y CORREGIR")
        return 1

if __name__ == "__main__":
    exit(main())