#!/usr/bin/env python3
"""
📊 SISTEMA DE TRAZABILIDAD DEPARTAMENTAL
Maneja reportes de modificaciones y trazabilidad en oficinas de agentes
Creado por: Agent Recruiter AI
Fecha: 2025-09-26
Version: 1.0.0
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import shutil

class DepartmentalTraceabilityManager:
    def __init__(self):
        self.workspace_root = "/home/admin-jairo/MeStore/.workspace"
        self.departments_root = f"{self.workspace_root}/departments"
        self.logs_root = f"{self.workspace_root}/logs"

    def create_modification_report(self, agent_name, file_path, operation, status, approved_by=None):
        """Crear reporte de modificación en la oficina del agente responsable"""

        # Identificar agente responsable del archivo
        responsible_agent = self._identify_responsible_agent(file_path)

        if not responsible_agent:
            responsible_agent = "master-orchestrator"  # Escalación por defecto

        # Buscar oficina del agente responsable
        agent_office = self._find_agent_office(responsible_agent)

        if not agent_office:
            print(f"⚠️ No se encontró oficina para {responsible_agent}, creando oficina temporal")
            agent_office = self._create_temporary_office(responsible_agent)

        # Crear reporte de modificación
        reports_dir = f"{agent_office}/modification_reports"
        os.makedirs(reports_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_id = f"mod_{timestamp}_{hash(file_path) % 10000:04d}"

        report_data = {
            "report_id": report_id,
            "timestamp": datetime.now().isoformat(),
            "file_path": file_path,
            "requesting_agent": agent_name,
            "responsible_agent": responsible_agent,
            "operation": operation,
            "status": status,
            "approved_by": approved_by,
            "impact_assessment": self._assess_impact(file_path),
            "related_systems": self._identify_related_systems(file_path),
            "followup_required": status == "BLOCKED_PENDING_APPROVAL"
        }

        # Guardar reporte
        report_file = f"{reports_dir}/{report_id}.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)

        # Crear notificación para el agente responsable
        self._create_agent_notification(agent_office, report_data)

        print(f"📊 Reporte creado en oficina de {responsible_agent}: {report_id}")

        return report_id

    def _identify_responsible_agent(self, file_path):
        """Identificar agente responsable basado en el archivo"""

        responsibility_map = {
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

        # Verificación exacta
        if file_path in responsibility_map:
            return responsibility_map[file_path]

        # Verificación por patrones
        patterns = {
            "app/models/": "database-architect-ai",
            "app/api/": "api-architect-ai",
            "frontend/src/": "react-specialist-ai",
            "tests/": "tdd-specialist",
            "app/services/": "backend-framework-ai",
            "docker": "cloud-infrastructure-ai",
            "alembic/": "database-architect-ai"
        }

        for pattern, agent in patterns.items():
            if pattern in file_path:
                return agent

        return None

    def _find_agent_office(self, agent_name):
        """Encontrar la oficina de un agente"""

        for dept in os.listdir(self.departments_root):
            dept_path = f"{self.departments_root}/{dept}"

            if not os.path.isdir(dept_path):
                continue

            for item in os.listdir(dept_path):
                item_path = f"{dept_path}/{item}"

                if os.path.isdir(item_path):
                    # Verificar si es la oficina del agente
                    if agent_name in item or item == agent_name:
                        return item_path

                    # Verificar subdirectorios
                    if os.path.isdir(item_path):
                        for subitem in os.listdir(item_path):
                            if agent_name in subitem or subitem == agent_name:
                                return f"{item_path}/{subitem}"

        return None

    def _create_temporary_office(self, agent_name):
        """Crear oficina temporal para agente"""

        # Determinar departamento apropiado
        dept_mapping = {
            "system-architect-ai": "architecture",
            "security-backend-ai": "backend",
            "database-architect-ai": "architecture",
            "tdd-specialist": "testing",
            "cloud-infrastructure-ai": "infrastructure",
            "react-specialist-ai": "frontend"
        }

        department = dept_mapping.get(agent_name, "general")
        office_path = f"{self.departments_root}/{department}/{agent_name}"

        os.makedirs(office_path, exist_ok=True)
        os.makedirs(f"{office_path}/modification_reports", exist_ok=True)
        os.makedirs(f"{office_path}/notifications", exist_ok=True)

        # Crear archivo README de la oficina
        readme_content = f"""# Oficina de {agent_name}

**Departamento**: {department}
**Creada**: {datetime.now().isoformat()}
**Tipo**: Oficina Temporal (Auto-generada)

## Responsabilidades
- Archivo de responsabilidades pendiente de configuración

## Reportes de Modificaciones
- Ver carpeta `modification_reports/`

## Notificaciones
- Ver carpeta `notifications/`
"""

        with open(f"{office_path}/README.md", 'w') as f:
            f.write(readme_content)

        print(f"🏢 Oficina temporal creada para {agent_name} en {department}")

        return office_path

    def _create_agent_notification(self, agent_office, report_data):
        """Crear notificación para el agente en su oficina"""

        notifications_dir = f"{agent_office}/notifications"
        os.makedirs(notifications_dir, exist_ok=True)

        notification_data = {
            "notification_id": f"notif_{report_data['report_id']}",
            "timestamp": datetime.now().isoformat(),
            "type": "MODIFICATION_REPORT",
            "priority": self._calculate_priority(report_data),
            "message": f"Modificación {'bloqueada' if report_data['status'] == 'BLOCKED_PENDING_APPROVAL' else 'registrada'} en {report_data['file_path']}",
            "details": {
                "requesting_agent": report_data['requesting_agent'],
                "operation": report_data['operation'],
                "impact": report_data['impact_assessment'],
                "requires_action": report_data['followup_required']
            },
            "read": False,
            "expires_at": (datetime.now() + timedelta(days=7)).isoformat()
        }

        notification_file = f"{notifications_dir}/{notification_data['notification_id']}.json"
        with open(notification_file, 'w') as f:
            json.dump(notification_data, f, indent=2)

    def _calculate_priority(self, report_data):
        """Calcular prioridad de la notificación"""

        # Archivos críticos = alta prioridad
        critical_files = [
            "app/main.py", "app/api/v1/deps/auth.py", "docker-compose.yml",
            "app/models/user.py", "app/database.py"
        ]

        if any(critical in report_data['file_path'] for critical in critical_files):
            return "HIGH"

        # Operaciones bloqueadas = media prioridad
        if report_data['status'] == "BLOCKED_PENDING_APPROVAL":
            return "MEDIUM"

        return "LOW"

    def _assess_impact(self, file_path):
        """Evaluar impacto de la modificación"""

        impact_map = {
            "app/main.py": "CRITICAL - Servidor principal",
            "app/api/v1/deps/auth.py": "CRITICAL - Sistema de autenticación",
            "docker-compose.yml": "HIGH - Infraestructura de servicios",
            "app/models/user.py": "HIGH - Modelo de usuarios",
            "tests/conftest.py": "MEDIUM - Configuración de tests",
            "app/database.py": "HIGH - Conexión a base de datos"
        }

        return impact_map.get(file_path, "LOW - Impacto normal")

    def _identify_related_systems(self, file_path):
        """Identificar sistemas relacionados que podrían verse afectados"""

        relations = {
            "app/main.py": ["FastAPI Server", "All API Endpoints", "CORS", "Middleware"],
            "app/api/v1/deps/auth.py": ["Login System", "JWT Tokens", "User Sessions", "Vendor Access"],
            "docker-compose.yml": ["All Containers", "Network", "Volumes", "Environment"],
            "app/models/user.py": ["User Registration", "Authentication", "Database Integrity"],
            "tests/conftest.py": ["All Tests", "Test Database", "Fixtures"]
        }

        return relations.get(file_path, ["System General"])

    def generate_department_dashboard(self, department_name):
        """Generar dashboard de actividad para un departamento"""

        dept_path = f"{self.departments_root}/{department_name}"

        if not os.path.exists(dept_path):
            print(f"❌ Departamento {department_name} no existe")
            return

        dashboard_data = {
            "department": department_name,
            "generated_at": datetime.now().isoformat(),
            "agents": [],
            "total_reports": 0,
            "pending_approvals": 0,
            "recent_activity": []
        }

        # Recorrer oficinas del departamento
        for item in os.listdir(dept_path):
            item_path = f"{dept_path}/{item}"

            if os.path.isdir(item_path):
                agent_data = self._analyze_agent_office(item, item_path)
                dashboard_data["agents"].append(agent_data)
                dashboard_data["total_reports"] += agent_data["total_reports"]
                dashboard_data["pending_approvals"] += agent_data["pending_approvals"]

        # Guardar dashboard
        dashboard_file = f"{dept_path}/department_dashboard.json"
        with open(dashboard_file, 'w') as f:
            json.dump(dashboard_data, f, indent=2)

        print(f"📊 Dashboard generado para departamento {department_name}")

        return dashboard_data

    def _analyze_agent_office(self, agent_name, office_path):
        """Analizar actividad en la oficina de un agente"""

        agent_data = {
            "agent": agent_name,
            "office_path": office_path,
            "total_reports": 0,
            "pending_approvals": 0,
            "unread_notifications": 0,
            "last_activity": None
        }

        # Contar reportes
        reports_dir = f"{office_path}/modification_reports"
        if os.path.exists(reports_dir):
            reports = [f for f in os.listdir(reports_dir) if f.endswith('.json')]
            agent_data["total_reports"] = len(reports)

            # Analizar reportes pendientes
            for report_file in reports:
                try:
                    with open(f"{reports_dir}/{report_file}", 'r') as f:
                        report = json.load(f)

                    if report.get('followup_required', False):
                        agent_data["pending_approvals"] += 1

                    # Encontrar actividad más reciente
                    if not agent_data["last_activity"] or report["timestamp"] > agent_data["last_activity"]:
                        agent_data["last_activity"] = report["timestamp"]

                except:
                    continue

        # Contar notificaciones no leídas
        notifications_dir = f"{office_path}/notifications"
        if os.path.exists(notifications_dir):
            notifications = [f for f in os.listdir(notifications_dir) if f.endswith('.json')]

            for notif_file in notifications:
                try:
                    with open(f"{notifications_dir}/{notif_file}", 'r') as f:
                        notif = json.load(f)

                    if not notif.get('read', False):
                        agent_data["unread_notifications"] += 1

                except:
                    continue

        return agent_data

    def cleanup_old_reports(self, days_old=30):
        """Limpiar reportes antiguos"""

        cutoff_date = datetime.now() - timedelta(days=days_old)
        cleaned_count = 0

        for dept in os.listdir(self.departments_root):
            dept_path = f"{self.departments_root}/{dept}"

            if not os.path.isdir(dept_path):
                continue

            for agent in os.listdir(dept_path):
                reports_dir = f"{dept_path}/{agent}/modification_reports"

                if not os.path.exists(reports_dir):
                    continue

                for report_file in os.listdir(reports_dir):
                    if not report_file.endswith('.json'):
                        continue

                    report_path = f"{reports_dir}/{report_file}"

                    try:
                        with open(report_path, 'r') as f:
                            report = json.load(f)

                        report_date = datetime.fromisoformat(report['timestamp'].replace('Z', '+00:00').replace('+00:00', ''))

                        if report_date < cutoff_date:
                            os.remove(report_path)
                            cleaned_count += 1

                    except:
                        continue

        print(f"🧹 Limpieza completada: {cleaned_count} reportes antiguos eliminados")

        return cleaned_count

def main():
    """Función principal del gestor de trazabilidad"""

    import sys

    if len(sys.argv) < 2:
        print("❌ Uso: python traceability_manager.py <command> [args...]")
        print("📋 Comandos disponibles:")
        print("  create_report <agent> <file> <operation> <status> [approved_by]")
        print("  department_dashboard <department>")
        print("  cleanup_reports [days]")
        sys.exit(1)

    command = sys.argv[1]
    manager = DepartmentalTraceabilityManager()

    if command == "create_report":
        if len(sys.argv) < 6:
            print("❌ Uso: create_report <agent> <file> <operation> <status> [approved_by]")
            sys.exit(1)

        agent = sys.argv[2]
        file_path = sys.argv[3]
        operation = sys.argv[4]
        status = sys.argv[5]
        approved_by = sys.argv[6] if len(sys.argv) > 6 else None

        report_id = manager.create_modification_report(agent, file_path, operation, status, approved_by)
        print(f"✅ Reporte creado: {report_id}")

    elif command == "department_dashboard":
        if len(sys.argv) < 3:
            print("❌ Uso: department_dashboard <department>")
            sys.exit(1)

        department = sys.argv[2]
        dashboard = manager.generate_department_dashboard(department)
        print(f"📊 Dashboard generado para {department}")

    elif command == "cleanup_reports":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        cleaned = manager.cleanup_old_reports(days)
        print(f"🧹 {cleaned} reportes limpiados")

    else:
        print(f"❌ Comando desconocido: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()