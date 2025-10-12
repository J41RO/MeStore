#!/usr/bin/env python3
"""
Backend Structure Analysis with Test Coverage Mapping
Generates comprehensive directory tree with test status indicators
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

class BackendStructureAnalyzer:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.app_dir = self.project_root / "app"
        self.tests_dir = self.project_root / "tests"

        # Test file mappings
        self.test_mappings: Dict[str, List[str]] = {}
        self.coverage_data: Dict[str, float] = {}

    def find_source_files(self) -> List[Path]:
        """Find all Python source files in app directory"""
        source_files = []
        for file_path in self.app_dir.rglob("*.py"):
            if "__pycache__" not in str(file_path):
                source_files.append(file_path)
        return sorted(source_files)

    def find_test_files(self) -> List[Path]:
        """Find all test files"""
        test_files = []
        for file_path in self.tests_dir.rglob("*.py"):
            if "__pycache__" not in str(file_path) and (
                file_path.name.startswith("test_") or
                file_path.name.endswith("_test.py") or
                "test" in file_path.name
            ):
                test_files.append(file_path)
        return sorted(test_files)

    def map_tests_to_source(self, source_files: List[Path], test_files: List[Path]) -> Dict[str, Dict]:
        """Map test files to source files with intelligent matching"""
        mappings = {}

        for source_file in source_files:
            source_rel = str(source_file.relative_to(self.project_root))
            source_name = source_file.stem
            source_parent = source_file.parent.name

            # Initialize mapping
            mappings[source_rel] = {
                "tests": [],
                "test_types": set(),
                "has_tests": False,
                "coverage": "N/A",
                "priority": "Low"
            }

            # Find matching tests
            for test_file in test_files:
                test_rel = str(test_file.relative_to(self.project_root))
                test_name = test_file.stem
                test_parent = test_file.parent.name

                # Matching patterns
                matches = False

                # Direct name match
                if (f"test_{source_name}" in test_name or
                    f"{source_name}_test" in test_name or
                    source_name in test_name):
                    matches = True

                # Parent directory match
                if source_parent in test_name or source_parent in str(test_file):
                    matches = True

                # Module pattern match (e.g., app/models/user.py -> tests/models/test_user.py)
                source_parts = source_file.parts
                test_parts = test_file.parts
                if len(source_parts) >= 2 and len(test_parts) >= 2:
                    if (source_parts[-2] in test_parts and
                        (source_name in test_name or test_name.replace("test_", "") == source_name)):
                        matches = True

                if matches:
                    mappings[source_rel]["tests"].append(test_rel)
                    mappings[source_rel]["has_tests"] = True

                    # Determine test type
                    if "unit" in test_rel:
                        mappings[source_rel]["test_types"].add("unit")
                    elif "integration" in test_rel:
                        mappings[source_rel]["test_types"].add("integration")
                    elif "e2e" in test_rel:
                        mappings[source_rel]["test_types"].add("e2e")
                    else:
                        mappings[source_rel]["test_types"].add("api")

            # Convert set to list for JSON serialization
            mappings[source_rel]["test_types"] = list(mappings[source_rel]["test_types"])

            # Determine priority based on importance
            if self.is_critical_file(source_file):
                mappings[source_rel]["priority"] = "High" if not mappings[source_rel]["has_tests"] else "Medium"
            elif self.is_important_file(source_file):
                mappings[source_rel]["priority"] = "Medium" if not mappings[source_rel]["has_tests"] else "Low"

        return mappings

    def is_critical_file(self, file_path: Path) -> bool:
        """Determine if file is critical and needs tests"""
        critical_patterns = [
            "main.py", "auth.py", "security.py", "payment", "user.py",
            "models/", "services/", "endpoints/"
        ]
        return any(pattern in str(file_path) for pattern in critical_patterns)

    def is_important_file(self, file_path: Path) -> bool:
        """Determine if file is important"""
        important_patterns = [
            "core/", "utils/", "schemas/", "middleware/"
        ]
        return any(pattern in str(file_path) for pattern in important_patterns)

    def generate_tree_structure(self) -> str:
        """Generate tree structure with test indicators"""
        tree_lines = []
        tree_lines.append("📊 MESTORE BACKEND - ESTRUCTURA CON COBERTURA DE TESTS")
        tree_lines.append("=" * 60)
        tree_lines.append("")

        # Leyenda
        tree_lines.append("🔍 LEYENDA:")
        tree_lines.append("✅ = Tiene tests | ❌ = Sin tests | 🔍 = Tests parciales")
        tree_lines.append("📊 = Cobertura conocida | 🏷️ = Tipos: unit/integration/e2e/api")
        tree_lines.append("🔥 = Prioridad alta | ⚠️ = Prioridad media | ℹ️ = Prioridad baja")
        tree_lines.append("")

        source_files = self.find_source_files()
        test_files = self.find_test_files()
        mappings = self.map_tests_to_source(source_files, test_files)

        # Group files by directory structure
        dir_structure = {}
        for source_file in source_files:
            parts = source_file.relative_to(self.app_dir).parts
            current = dir_structure
            for part in parts[:-1]:  # All but filename
                if part not in current:
                    current[part] = {}
                current = current[part]

            # Add file info
            file_info = mappings.get(str(source_file.relative_to(self.project_root)), {})
            current[parts[-1]] = file_info

        # Render tree
        tree_lines.append("app/")
        self._render_directory(dir_structure, tree_lines, "│   ", mappings)

        return "\n".join(tree_lines)

    def _render_directory(self, directory: dict, lines: List[str], prefix: str, mappings: Dict):
        """Recursively render directory structure"""
        items = sorted(directory.items())

        for i, (name, content) in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "

            if isinstance(content, dict) and not content.get("has_tests") is not None:
                # It's a directory
                lines.append(f"{prefix}{current_prefix}{name}/")
                next_prefix = prefix + ("    " if is_last else "│   ")
                self._render_directory(content, lines, next_prefix, mappings)
            else:
                # It's a file
                status_icon = "✅" if content.get("has_tests") else "❌"

                priority_icon = ""
                if content.get("priority") == "High":
                    priority_icon = " 🔥"
                elif content.get("priority") == "Medium":
                    priority_icon = " ⚠️"
                else:
                    priority_icon = " ℹ️"

                test_types = ", ".join(content.get("test_types", []))
                test_info = f" 🏷️[{test_types}]" if test_types else ""

                lines.append(f"{prefix}{current_prefix}{name} {status_icon}{priority_icon}{test_info}")

                # Add test file details
                for test_file in content.get("tests", []):
                    lines.append(f"{prefix}{'    ' if is_last else '│   '}    📁 {test_file}")

    def generate_summary_report(self) -> str:
        """Generate summary statistics"""
        source_files = self.find_source_files()
        test_files = self.find_test_files()
        mappings = self.map_tests_to_source(source_files, test_files)

        total_files = len(source_files)
        files_with_tests = sum(1 for m in mappings.values() if m["has_tests"])
        files_without_tests = total_files - files_with_tests

        high_priority_files = [f for f, m in mappings.items() if m["priority"] == "High"]
        critical_without_tests = [f for f in high_priority_files if not mappings[f]["has_tests"]]

        report = []
        report.append("\n📈 RESUMEN EJECUTIVO DE COBERTURA")
        report.append("=" * 50)
        report.append(f"📊 Total archivos fuente: {total_files}")
        report.append(f"✅ Archivos con tests: {files_with_tests} ({files_with_tests/total_files*100:.1f}%)")
        report.append(f"❌ Archivos sin tests: {files_without_tests} ({files_without_tests/total_files*100:.1f}%)")
        report.append(f"🔥 Archivos críticos sin tests: {len(critical_without_tests)}")
        report.append("")

        # Test type distribution
        test_types_count = {"unit": 0, "integration": 0, "e2e": 0, "api": 0}
        for mapping in mappings.values():
            for test_type in mapping.get("test_types", []):
                if test_type in test_types_count:
                    test_types_count[test_type] += 1

        report.append("🏷️ DISTRIBUCIÓN TIPOS DE TESTS:")
        for test_type, count in test_types_count.items():
            report.append(f"   {test_type}: {count} archivos")
        report.append("")

        # Critical files without tests
        if critical_without_tests:
            report.append("🚨 ARCHIVOS CRÍTICOS SIN TESTS (PRIORIDAD ALTA):")
            for file_path in critical_without_tests[:10]:  # Show top 10
                report.append(f"   ❌ {file_path}")
            if len(critical_without_tests) > 10:
                report.append(f"   ... y {len(critical_without_tests) - 10} más")
        report.append("")

        # Recommendations
        report.append("💡 RECOMENDACIONES:")
        report.append("1. Priorizar tests para archivos críticos marcados con 🔥")
        report.append("2. Implementar tests de integración para servicios complejos")
        report.append("3. Añadir tests E2E para flujos de usuario principales")
        report.append("4. Mantener cobertura >80% en módulos core")
        report.append("")

        # Commands
        report.append("⚡ COMANDOS ÚTILES:")
        report.append("```bash")
        report.append("# Ejecutar todos los tests")
        report.append("python -m pytest tests/ -v")
        report.append("")
        report.append("# Generar reporte de cobertura")
        report.append("python -m pytest --cov=app --cov-report=html tests/")
        report.append("")
        report.append("# Ejecutar solo tests unitarios")
        report.append("python -m pytest tests/unit/ -v")
        report.append("")
        report.append("# Ejecutar tests con marcadores TDD")
        report.append("python -m pytest -m \"tdd\" -v")
        report.append("```")

        return "\n".join(report)

    def run_analysis(self) -> str:
        """Run complete analysis and return formatted report"""
        tree_structure = self.generate_tree_structure()
        summary_report = self.generate_summary_report()

        return tree_structure + "\n" + summary_report

def main():
    analyzer = BackendStructureAnalyzer()
    report = analyzer.run_analysis()
    print(report)

    # Save to file
    with open("BACKEND_STRUCTURE_ANALYSIS.md", "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n✅ Análisis completado. Reporte guardado en: BACKEND_STRUCTURE_ANALYSIS.md")

if __name__ == "__main__":
    main()