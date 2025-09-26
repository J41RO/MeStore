#!/usr/bin/env python3
"""
🛡️ INTERCEPTOR MAESTRO DE CLAUDE CODE
Sistema que intercepta modificaciones de Claude Code y gestiona delegación automática
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

class ClaudeCodeInterceptor:
    def __init__(self):
        self.workspace_root = ".workspace"
        self.scripts_dir = f"{self.workspace_root}/scripts"
        self.requests_dir = f"{self.workspace_root}/requests"
        self.ensure_directories()

    def ensure_directories(self):
        """Crear directorios necesarios"""
        os.makedirs(self.requests_dir, exist_ok=True)
        os.makedirs(f"{self.workspace_root}/logs", exist_ok=True)
        os.makedirs(f"{self.workspace_root}/decisions", exist_ok=True)

    def intercept_claude_code_modification(self, user_instruction, target_files=None):
        """
        Interceptar modificación de Claude Code y activar delegación si es necesario
        """
        print("🛡️ INTERCEPTOR DE CLAUDE CODE ACTIVADO")
        print(f"📝 Instrucción del usuario: {user_instruction}")
        print("-" * 70)

        # Identificar archivos objetivo si no se proporcionaron
        if not target_files:
            target_files = self.identify_target_files_from_instruction(user_instruction)

        protected_files_detected = []
        delegations_created = []

        # Procesar cada archivo objetivo
        for target_file in target_files:
            print(f"🔍 Analizando archivo: {target_file}")

            # Verificar si es archivo protegido
            delegation_result = self.check_and_delegate_if_protected(
                "claude-code-ai",  # Claude Code como agente solicitante
                target_file,
                user_instruction
            )

            if delegation_result["status"] == "DELEGATED":
                protected_files_detected.append(target_file)
                delegations_created.append(delegation_result)
                print(f"🔄 Delegación creada para {target_file} → {delegation_result['responsible_agent']}")

            elif delegation_result["status"] == "ALLOWED":
                print(f"✅ Archivo {target_file} puede ser modificado directamente")

        # Generar reporte de interceptación
        return self.generate_interception_report(
            user_instruction, target_files, protected_files_detected, delegations_created
        )

    def identify_target_files_from_instruction(self, instruction):
        """
        Identificar archivos objetivo basándose en la instrucción del usuario
        """
        # Lista de archivos críticos que comúnmente se mencionan
        critical_files_keywords = {
            "app/main.py": ["main.py", "servidor", "fastapi", "uvicorn", "puerto"],
            "docker-compose.yml": ["docker", "compose", "servicios", "contenedor"],
            "app/api/v1/deps/auth.py": ["auth", "autenticación", "login", "jwt", "token"],
            "app/models/user.py": ["usuario", "user", "modelo", "user.py"],
            "tests/conftest.py": ["test", "fixture", "conftest", "testing"],
            "app/core/config.py": ["config", "configuración", "settings"],
            "frontend/vite.config.ts": ["vite", "frontend", "react", "configuración frontend"]
        }

        identified_files = []
        instruction_lower = instruction.lower()

        for file_path, keywords in critical_files_keywords.items():
            if any(keyword in instruction_lower for keyword in keywords):
                identified_files.append(file_path)

        # Si no se identificaron archivos específicos, asumir que podría afectar archivos críticos
        if not identified_files:
            print("⚠️ No se pudieron identificar archivos específicos de la instrucción")
            print("🔍 Se realizará análisis completo de archivos críticos")
            # Retornar los más probables basándose en keywords genéricos
            if any(word in instruction_lower for word in ["endpoint", "api", "ruta"]):
                identified_files.append("app/main.py")
            if any(word in instruction_lower for word in ["usuario", "user", "login"]):
                identified_files.extend(["app/models/user.py", "app/api/v1/deps/auth.py"])

        return identified_files or ["app/main.py"]  # Default fallback

    def check_and_delegate_if_protected(self, requesting_agent, target_file, instruction):
        """
        Verificar si archivo está protegido y delegar automáticamente
        """
        try:
            result = subprocess.run([
                "python", f"{self.scripts_dir}/auto_delegate_to_responsible_agent.py",
                requesting_agent, target_file, instruction
            ], capture_output=True, text=True, cwd=".")

            if result.returncode == 0:
                # Parsear salida para extraer información
                output = result.stdout

                if "PUEDE PROCEDER" in output:
                    return {"status": "ALLOWED", "message": "Archivo no protegido"}

                elif "DELEGACIÓN AUTOMÁTICA ACTIVADA" in output:
                    # Extraer información de la delegación
                    request_id = self.extract_from_output(output, "Request ID:")
                    responsible_agent = self.extract_from_output(output, "Agente responsable:")

                    return {
                        "status": "DELEGATED",
                        "request_id": request_id,
                        "responsible_agent": responsible_agent,
                        "target_file": target_file,
                        "output": output
                    }

                else:
                    return {"status": "ERROR", "message": "Respuesta inesperada del sistema"}

            else:
                return {"status": "ERROR", "message": f"Error en delegación: {result.stderr}"}

        except Exception as e:
            return {"status": "ERROR", "message": f"Error técnico: {str(e)}"}

    def extract_from_output(self, output, pattern):
        """Extraer información específica de la salida"""
        for line in output.split('\n'):
            if pattern in line:
                return line.split(pattern)[1].strip()
        return "UNKNOWN"

    def generate_interception_report(self, user_instruction, target_files, protected_files, delegations):
        """
        Generar reporte completo de la interceptación
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_id = f"INTERCEPT_{timestamp}"

        report = {
            "report_id": report_id,
            "timestamp": datetime.now().isoformat(),
            "user_instruction": user_instruction,
            "target_files_analyzed": target_files,
            "protected_files_detected": protected_files,
            "total_delegations_created": len(delegations),
            "delegations": delegations,
            "status": "PARTIALLY_DELEGATED" if delegations else "DIRECT_EXECUTION",
            "next_steps": self.generate_next_steps(delegations)
        }

        # Guardar reporte
        report_file = f"{self.requests_dir}/interception_report_{report_id}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        return report

    def generate_next_steps(self, delegations):
        """Generar próximos pasos basándose en las delegaciones creadas"""
        if not delegations:
            return ["Claude Code puede proceder con la modificación directamente"]

        steps = [
            f"⏳ Esperando evaluación de {len(delegations)} agente(s) especializado(s)",
            "🔍 Los agentes responsables evaluarán automáticamente los riesgos",
            "📊 Se generarán reportes de decisión automáticos",
            "⚡ Tiempo estimado total: 5-15 minutos",
            "🔄 Escalación automática si no hay respuesta en 15 minutos"
        ]

        # Agregar pasos específicos por delegación
        for delegation in delegations:
            steps.append(
                f"   • {delegation['responsible_agent']} evaluará {delegation['target_file']}"
            )

        steps.extend([
            "",
            "📋 Para monitorear el progreso:",
            f"   python .workspace/scripts/check_delegation_status.py dashboard"
        ])

        return steps

    def display_interception_summary(self, report):
        """Mostrar resumen de la interceptación al usuario"""
        print("\n" + "="*70)
        print("🛡️ RESUMEN DE INTERCEPTACIÓN DE CLAUDE CODE")
        print("="*70)

        print(f"📋 Report ID: {report['report_id']}")
        print(f"📝 Instrucción: {report['user_instruction']}")
        print(f"📂 Archivos analizados: {len(report['target_files_analyzed'])}")
        print(f"🔒 Archivos protegidos: {len(report['protected_files_detected'])}")
        print(f"🔄 Delegaciones creadas: {report['total_delegations_created']}")

        if report['delegations']:
            print("\n🤖 AGENTES ACTIVADOS:")
            for delegation in report['delegations']:
                print(f"   • {delegation['responsible_agent']} → {delegation['target_file']}")
                print(f"     Request ID: {delegation['request_id']}")

        print(f"\n📊 Estado: {report['status']}")

        print("\n🎯 PRÓXIMOS PASOS:")
        for step in report['next_steps']:
            print(f"   {step}")

        print("\n" + "="*70)

def main():
    """Función principal del interceptor"""
    if len(sys.argv) < 2:
        print("❌ Uso: python claude_code_interceptor.py '<instrucción_usuario>' [archivo1] [archivo2] ...")
        print("🔧 Ejemplos:")
        print('   python claude_code_interceptor.py "Agregar endpoint de salud al servidor"')
        print('   python claude_code_interceptor.py "Modificar autenticación JWT" app/api/v1/deps/auth.py')
        print('   python claude_code_interceptor.py "Crear nuevo usuario para testing" app/models/user.py')
        sys.exit(1)

    user_instruction = sys.argv[1]
    target_files = sys.argv[2:] if len(sys.argv) > 2 else None

    interceptor = ClaudeCodeInterceptor()

    print("🚀 SISTEMA DE INTERCEPTACIÓN CLAUDE CODE INICIADO")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print("")

    # Ejecutar interceptación
    report = interceptor.intercept_claude_code_modification(user_instruction, target_files)

    # Mostrar resumen al usuario
    interceptor.display_interception_summary(report)

    # Exit codes para automatización
    if report['total_delegations_created'] > 0:
        print("\n⚠️ DELEGACIONES CREADAS - Claude Code debe esperar aprobaciones")
        sys.exit(2)  # Código especial para delegaciones
    else:
        print("\n✅ PROCEDER CON MODIFICACIÓN DIRECTA")
        sys.exit(0)  # Todo OK, proceder

if __name__ == "__main__":
    main()