#!/usr/bin/env python3
"""
📊 REPORTE DIARIO DE CUMPLIMIENTO WORKSPACE
Genera reporte automático de actividad de agentes y cumplimiento de protocolos
"""

import os
import json
import glob
from datetime import datetime, timedelta
from collections import defaultdict

def load_daily_logs(date_str):
    """Cargar logs de actividad del día"""
    log_file = f".workspace/logs/agent_activity_{date_str}.json"

    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            return json.load(f)
    return []

def analyze_protected_file_access():
    """Analizar accesos a archivos protegidos"""
    protected_files = [
        "app/main.py",
        "frontend/vite.config.ts",
        "docker-compose.yml",
        "app/api/v1/deps/auth.py",
        "app/models/user.py",
        "tests/conftest.py"
    ]

    # Buscar modificaciones en archivos protegidos en últimos 7 días
    violations = []

    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        logs = load_daily_logs(date)

        for log in logs:
            if log['file'] in protected_files:
                if log['status'] == 'self-authorized' and log['agent'] != 'master-orchestrator':
                    violations.append({
                        'date': date,
                        'agent': log['agent'],
                        'file': log['file'],
                        'timestamp': log['timestamp']
                    })

    return violations

def check_git_commits_compliance():
    """Verificar cumplimiento en commits recientes"""
    import subprocess

    try:
        # Obtener commits de últimas 24 horas
        result = subprocess.run([
            'git', 'log', '--since=24.hours.ago', '--pretty=format:%H|%s|%an|%ad'
        ], capture_output=True, text=True)

        commits = []
        non_compliant = []

        for line in result.stdout.strip().split('\n'):
            if line:
                hash_commit, message, author, date = line.split('|', 3)
                commits.append({
                    'hash': hash_commit,
                    'message': message,
                    'author': author,
                    'date': date
                })

                # Verificar si tiene Workspace-Check
                if 'Workspace-Check: ✅' not in message:
                    non_compliant.append({
                        'hash': hash_commit,
                        'message': message,
                        'author': author,
                        'issue': 'Sin Workspace-Check'
                    })

        return commits, non_compliant

    except Exception as e:
        return [], [{'error': str(e)}]

def generate_agent_statistics():
    """Generar estadísticas por agente"""
    agent_stats = defaultdict(lambda: {
        'total_actions': 0,
        'protected_file_access': 0,
        'authorized_access': 0,
        'violations': 0
    })

    # Analizar logs de últimos 7 días
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        logs = load_daily_logs(date)

        for log in logs:
            agent = log['agent']
            agent_stats[agent]['total_actions'] += 1

            if log['file'] in [
                "app/main.py", "frontend/vite.config.ts", "docker-compose.yml",
                "app/api/v1/deps/auth.py", "app/models/user.py", "tests/conftest.py"
            ]:
                agent_stats[agent]['protected_file_access'] += 1

                if log['approved_by'] or agent == 'master-orchestrator':
                    agent_stats[agent]['authorized_access'] += 1
                else:
                    agent_stats[agent]['violations'] += 1

    return dict(agent_stats)

def generate_html_report():
    """Generar reporte HTML completo"""
    violations = analyze_protected_file_access()
    commits, non_compliant_commits = check_git_commits_compliance()
    agent_stats = generate_agent_statistics()

    today = datetime.now().strftime("%Y-%m-%d")

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>📊 Reporte Cumplimiento Workspace - {today}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f0f8ff; padding: 20px; border-radius: 8px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .violation {{ background: #ffe6e6; }}
        .success {{ background: #e6ffe6; }}
        .warning {{ background: #fff3cd; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background: #f2f2f2; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #f8f9fa; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚨 Reporte Diario Cumplimiento Workspace</h1>
        <p><strong>Fecha:</strong> {today}</p>
        <p><strong>Generado:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>

    <div class="section">
        <h2>📊 Métricas Generales</h2>
        <div class="metric">
            <strong>Violaciones Detectadas:</strong> {len(violations)}
        </div>
        <div class="metric">
            <strong>Commits No Conformes:</strong> {len(non_compliant_commits)}
        </div>
        <div class="metric">
            <strong>Agentes Activos:</strong> {len(agent_stats)}
        </div>
    </div>

    <div class="section {'violation' if violations else 'success'}">
        <h2>🚨 Violaciones de Archivos Protegidos</h2>
"""

    if violations:
        html += """
        <table>
            <tr>
                <th>Fecha</th>
                <th>Agente</th>
                <th>Archivo</th>
                <th>Timestamp</th>
            </tr>
"""
        for v in violations:
            html += f"""
            <tr>
                <td>{v['date']}</td>
                <td>{v['agent']}</td>
                <td>{v['file']}</td>
                <td>{v['timestamp']}</td>
            </tr>
"""
        html += "</table>"
    else:
        html += "<p>✅ No se detectaron violaciones en archivos protegidos</p>"

    html += "</div>"

    # Commits no conformes
    html += f"""
    <div class="section {'violation' if non_compliant_commits else 'success'}">
        <h2>📝 Commits No Conformes</h2>
"""

    if non_compliant_commits:
        html += """
        <table>
            <tr>
                <th>Hash</th>
                <th>Mensaje</th>
                <th>Autor</th>
                <th>Problema</th>
            </tr>
"""
        for c in non_compliant_commits:
            if 'error' not in c:
                html += f"""
                <tr>
                    <td>{c['hash'][:8]}</td>
                    <td>{c['message']}</td>
                    <td>{c['author']}</td>
                    <td>{c['issue']}</td>
                </tr>
"""
        html += "</table>"
    else:
        html += "<p>✅ Todos los commits cumplen con el template obligatorio</p>"

    html += "</div>"

    # Estadísticas por agente
    html += """
    <div class="section">
        <h2>🤖 Estadísticas por Agente</h2>
        <table>
            <tr>
                <th>Agente</th>
                <th>Acciones Totales</th>
                <th>Acceso Archivos Protegidos</th>
                <th>Accesos Autorizados</th>
                <th>Violaciones</th>
            </tr>
"""

    for agent, stats in agent_stats.items():
        html += f"""
        <tr>
            <td>{agent}</td>
            <td>{stats['total_actions']}</td>
            <td>{stats['protected_file_access']}</td>
            <td>{stats['authorized_access']}</td>
            <td>{stats['violations']}</td>
        </tr>
"""

    html += """
        </table>
    </div>

    <div class="section">
        <h2>📋 Recomendaciones</h2>
        <ul>
"""

    if violations:
        html += "<li>🚨 Investigar violaciones de archivos protegidos y aplicar correcciones</li>"

    if non_compliant_commits:
        html += "<li>📝 Educar sobre template obligatorio de commits</li>"

    if not violations and not non_compliant_commits:
        html += "<li>✅ Sistema funcionando correctamente, mantener vigilancia</li>"

    html += """
        </ul>
    </div>

    <div class="section">
        <h2>🔧 Acciones Sugeridas</h2>
        <ol>
            <li>Revisar violaciones con agentes responsables</li>
            <li>Actualizar documentación si es necesario</li>
            <li>Ejecutar scripts de validación en commits futuros</li>
            <li>Programar training para agentes no conformes</li>
        </ol>
    </div>
</body>
</html>
"""

    # Guardar reporte
    report_dir = ".workspace/reports"
    os.makedirs(report_dir, exist_ok=True)
    report_file = f"{report_dir}/compliance_report_{today}.html"

    with open(report_file, 'w') as f:
        f.write(html)

    print(f"📊 Reporte generado: {report_file}")
    return report_file

def main():
    """Función principal"""
    print("📊 GENERANDO REPORTE DIARIO DE CUMPLIMIENTO...")

    report_file = generate_html_report()

    # Generar también resumen en consola
    violations = analyze_protected_file_access()
    commits, non_compliant_commits = check_git_commits_compliance()

    print(f"""
🚨 RESUMEN EJECUTIVO
==================
📅 Fecha: {datetime.now().strftime("%Y-%m-%d")}
🔴 Violaciones: {len(violations)}
📝 Commits no conformes: {len(non_compliant_commits)}
📊 Reporte completo: {report_file}

{"🚨 ACCIÓN REQUERIDA" if violations or non_compliant_commits else "✅ SISTEMA CONFORME"}
""")

if __name__ == "__main__":
    main()