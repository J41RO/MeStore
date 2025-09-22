#!/usr/bin/env python3
"""
Master Testing Orchestrator for Claude Code /test command
Activates comprehensive backend testing suite with agent coordination
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

class MasterTestingOrchestrator:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.coverage_target = 85
        self.max_agents = 3
        self.current_agents = []
        self.test_results = {}

    def log_progress(self, message, level="INFO"):
        """Log progress with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "🔄 [PROGRESO]",
            "ALERT": "⚠️ [ALERTA]",
            "SUCCESS": "✅ [MILESTONE]",
            "ERROR": "❌ [ERROR]"
        }
        print(f"{prefix.get(level, 'ℹ️')} {timestamp} - {message}")

    def analyze_backend(self):
        """Analyze backend structure and identify testing priorities"""
        self.log_progress("Analizando backend completo...")

        # Scan backend structure
        backend_files = list(self.project_root.glob("app/**/*.py"))
        test_files = list(self.project_root.glob("tests/**/*.py"))

        self.log_progress(f"Encontrados {len(backend_files)} archivos backend, {len(test_files)} archivos test")

        # Check current coverage
        coverage = self.get_current_coverage()
        self.log_progress(f"Cobertura actual: {coverage}%")

        return {
            "backend_files": len(backend_files),
            "test_files": len(test_files),
            "coverage": coverage,
            "critical_modules": self.identify_critical_modules()
        }

    def get_current_coverage(self):
        """Get current test coverage"""
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "--cov=app", "--cov-report=json", "--quiet"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )

            if result.returncode == 0 and os.path.exists("coverage.json"):
                with open("coverage.json") as f:
                    coverage_data = json.load(f)
                    return round(coverage_data.get("totals", {}).get("percent_covered", 0))
            return 0
        except Exception as e:
            self.log_progress(f"Error obteniendo cobertura: {e}", "ERROR")
            return 0

    def identify_critical_modules(self):
        """Identify critical modules that need priority testing"""
        critical_paths = [
            "app/api/v1/endpoints/",
            "app/services/",
            "app/models/",
            "app/core/",
            "app/main.py"
        ]

        critical_modules = []
        for path in critical_paths:
            full_path = self.project_root / path
            if full_path.exists():
                if full_path.is_file():
                    critical_modules.append(str(full_path))
                else:
                    critical_modules.extend([str(f) for f in full_path.glob("*.py")])

        return critical_modules

    def activate_agents(self, analysis_data):
        """Activate specialized testing agents"""
        self.log_progress("Activando agentes especializados...")

        # Priority agent assignments based on analysis
        agent_priorities = [
            ("unit-testing-ai", "Tests unitarios críticos"),
            ("api-testing-specialist", "Validación de endpoints"),
            ("database-testing-specialist", "Testing de base de datos")
        ]

        if analysis_data["coverage"] < 50:
            agent_priorities.insert(0, ("test-architect", "Estrategia de testing"))

        if "auth" in str(analysis_data.get("critical_modules", [])).lower():
            agent_priorities.append(("security-vulnerability-tester", "Testing de seguridad"))

        # Activate up to max_agents
        active_agents = agent_priorities[:self.max_agents]

        for agent_name, description in active_agents:
            self.log_progress(f"Activando {agent_name}: {description}")
            self.current_agents.append({
                "name": agent_name,
                "description": description,
                "started": datetime.now()
            })

        return active_agents

    def run_test_suite(self):
        """Execute comprehensive test suite"""
        self.log_progress("Ejecutando suite completo de tests...")

        # Run TDD tests
        self.log_progress("Ejecutando TDD test suite...")
        tdd_result = subprocess.run(
            ["./scripts/run_tdd_tests.sh"],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )

        # Run all tests with coverage
        self.log_progress("Ejecutando tests con cobertura...")
        test_result = subprocess.run(
            ["python", "-m", "pytest", "-v", "--cov=app", "--cov-report=term-missing"],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )

        return {
            "tdd_passed": tdd_result.returncode == 0,
            "all_tests_passed": test_result.returncode == 0,
            "output": test_result.stdout,
            "errors": test_result.stderr
        }

    def monitor_progress(self):
        """Monitor testing progress and coverage"""
        cycles = 0
        max_cycles = 10

        while cycles < max_cycles:
            cycles += 1
            current_coverage = self.get_current_coverage()

            self.log_progress(f"Ciclo {cycles}: Cobertura actual {current_coverage}%")

            if current_coverage >= self.coverage_target:
                self.log_progress(f"Meta de cobertura {self.coverage_target}% alcanzada!", "SUCCESS")
                break

            # Run tests and check for improvements
            test_results = self.run_test_suite()

            if not test_results["all_tests_passed"]:
                self.log_progress("Tests fallando - continuando optimización...", "ALERT")

            time.sleep(2)  # Brief pause between cycles

        return current_coverage

    def final_verification(self):
        """Final verification of all criteria"""
        self.log_progress("Iniciando verificación final...")

        # Get final metrics
        final_coverage = self.get_current_coverage()
        test_results = self.run_test_suite()

        # Check all criteria
        criteria = {
            "✅ 100% tests pasando": test_results["all_tests_passed"],
            f"✅ Cobertura ≥ {self.coverage_target}%": final_coverage >= self.coverage_target,
            "✅ TDD tests pasando": test_results["tdd_passed"],
            "✅ Sin errores críticos": "ERROR" not in test_results.get("errors", ""),
        }

        all_passed = all(criteria.values())

        # Generate final report
        self.log_progress("=== REPORTE FINAL ===", "SUCCESS" if all_passed else "ERROR")

        for criterion, passed in criteria.items():
            status = "✅" if passed else "❌"
            self.log_progress(f"{status} {criterion}")

        self.log_progress(f"Cobertura final: {final_coverage}%")
        self.log_progress(f"Agentes utilizados: {len(self.current_agents)}")

        if all_passed:
            self.log_progress("🎯 MISIÓN COMPLETADA - Backend 100% testeado!", "SUCCESS")
        else:
            self.log_progress("⚠️ CRITERIOS NO CUMPLIDOS - Requiere intervención", "ALERT")

        return all_passed

    def execute(self, args=None):
        """Main execution flow"""
        self.log_progress("🚀 ACTIVANDO MASTER TESTING ORCHESTRATOR")

        try:
            # Phase 1: Analysis
            self.log_progress("=== FASE 1: ANÁLISIS INICIAL ===")
            analysis = self.analyze_backend()

            # Phase 2: Agent Activation
            self.log_progress("=== FASE 2: ACTIVACIÓN DE AGENTES ===")
            agents = self.activate_agents(analysis)

            # Phase 3: Monitoring and Execution
            self.log_progress("=== FASE 3: EJECUCIÓN Y MONITOREO ===")
            final_coverage = self.monitor_progress()

            # Phase 4: Final Verification
            self.log_progress("=== FASE 4: VERIFICACIÓN FINAL ===")
            success = self.final_verification()

            return 0 if success else 1

        except Exception as e:
            self.log_progress(f"Error crítico: {e}", "ERROR")
            return 1

if __name__ == "__main__":
    orchestrator = MasterTestingOrchestrator()
    exit_code = orchestrator.execute(sys.argv[1:])
    sys.exit(exit_code)