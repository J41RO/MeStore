#!/usr/bin/env python3
"""
Script para analizar dependencias de código Python y generar información
completa para que la IA cree tests efectivos y robustos.
"""

import ast
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union


class DependencyAnalyzer:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.local_imports = set()
        self.external_imports = set()
        self.missing_files = set()

        # Patrones para detectar frameworks y dominios
        self.framework_patterns = {
            "fastapi": ["fastapi", "starlette"],
            "django": ["django"],
            "flask": ["flask"],
            "asyncio": ["asyncio", "aiohttp", "async"],
            "database": [
                "sqlalchemy",
                "psycopg2",
                "mysql",
                "sqlite",
                "redis",
                "chromadb",
            ],
            "api_client": ["requests", "httpx", "aiohttp"],
            "data_processing": ["pandas", "numpy", "matplotlib", "seaborn"],
            "ml_ai": [
                "sklearn",
                "tensorflow",
                "torch",
                "transformers",
                "sentence_transformers",
            ],
            "testing": ["pytest", "unittest", "mock"],
            "logging": ["logging", "loguru", "structlog"],
            "config": ["pydantic", "configparser", "environs"],
            "validation": ["pydantic", "marshmallow", "cerberus"],
            "security": ["cryptography", "bcrypt", "jwt", "passlib"],
            "messaging": ["celery", "rq", "kafka", "rabbitmq"],
            "monitoring": ["prometheus", "sentry", "newrelic"],
        }

    def analyze_file(self, file_path: Union[str, Path]) -> Dict:
        """Analiza un archivo Python y extrae sus dependencias."""
        file_path = Path(file_path).resolve()

        if not file_path.exists():
            return {"error": f"El archivo {file_path} no existe"}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            basic_analysis = self._extract_dependencies(tree, file_path)

            # Análisis avanzado
            advanced_analysis = self._analyze_code_patterns(content, tree, file_path)

            # Combinar análisis
            basic_analysis.update(advanced_analysis)
            return basic_analysis

        except Exception as e:
            return {"error": f"Error al analizar {file_path}: {str(e)}"}

    def _extract_dependencies(self, tree: ast.AST, file_path: Path) -> Dict:
        """Extrae imports del AST del archivo."""
        local_imports = []
        external_imports = []
        missing_locals = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if self._is_local_import(alias.name, file_path):
                        local_imports.append(alias.name)
                        if not self._find_local_file(alias.name, file_path):
                            missing_locals.append(alias.name)
                    else:
                        external_imports.append(alias.name)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    if self._is_local_import(node.module, file_path):
                        local_imports.append(node.module)
                        if not self._find_local_file(node.module, file_path):
                            missing_locals.append(node.module)
                    else:
                        external_imports.append(node.module)

        return {
            "file_path": str(file_path),
            "relative_path": str(file_path.relative_to(self.project_root)),
            "local_imports": sorted(list(set(local_imports))),
            "external_imports": sorted(list(set(external_imports))),
            "missing_local_files": sorted(list(set(missing_locals))),
            "suggested_test_path": self._suggest_test_path(file_path),
        }

    def _is_local_import(self, module_name: str, current_file: Path) -> bool:
        """Determina si un import es local al proyecto."""
        # Si empieza con . es relativo
        if module_name.startswith("."):
            return True

        # Buscar si existe como archivo local
        return bool(self._find_local_file(module_name, current_file))

    def _find_local_file(self, module_name: str, current_file: Path) -> Optional[Path]:
        """Busca el archivo correspondiente a un módulo local."""
        # Convertir module.submodule a ruta
        module_parts = module_name.split(".")

        # Buscar desde el directorio del archivo actual
        search_dirs = [
            current_file.parent,
            self.project_root,
        ]

        for search_dir in search_dirs:
            # Buscar como archivo .py
            file_path = search_dir / f"{'/'.join(module_parts)}.py"
            if file_path.exists():
                return file_path

            # Buscar como paquete (__init__.py)
            package_path = search_dir / "/".join(module_parts) / "__init__.py"
            if package_path.exists():
                return package_path

        return None

    def _suggest_test_path(self, file_path: Path) -> Dict[str, str]:
        """Sugiere dónde crear el archivo de test."""
        relative_path = file_path.relative_to(self.project_root)

        # Opción 1: tests/ en el root
        test_dir = self.project_root / "tests"
        test_file = f"test_{file_path.stem}.py"

        # Opción 2: mismo directorio
        same_dir = file_path.parent / f"test_{file_path.name}"

        return {
            "option_1": str(test_dir / test_file),
            "option_2": str(same_dir),
            "recommended": str(test_dir / test_file),
        }

    def _analyze_code_patterns(
        self, content: str, tree: ast.AST, file_path: Path
    ) -> Dict:
        """Análisis avanzado de patrones de código para tests robustos."""

        analysis = {
            "detected_frameworks": [],
            "domain_type": "general",
            "edge_cases": [],
            "performance_considerations": [],
            "error_patterns": [],
            "integration_points": [],
            "testing_strategies": [],
        }

        # Detectar frameworks y dominio
        all_imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                all_imports.extend([alias.name for alias in node.names])
            elif isinstance(node, ast.ImportFrom) and node.module:
                all_imports.append(node.module)

        detected_frameworks = self._detect_frameworks(all_imports)
        analysis["detected_frameworks"] = detected_frameworks
        analysis["domain_type"] = self._determine_domain_type(
            detected_frameworks, content
        )

        # Análisis de casos edge
        analysis["edge_cases"] = self._analyze_edge_cases(tree, content)

        # Consideraciones de performance
        analysis["performance_considerations"] = self._analyze_performance_patterns(
            tree, content
        )

        # Patrones de error
        analysis["error_patterns"] = self._analyze_error_patterns(tree, content)

        # Puntos de integración
        analysis["integration_points"] = self._analyze_integration_points(
            tree, content, all_imports
        )

        # Estrategias de testing
        analysis["testing_strategies"] = self._suggest_testing_strategies(analysis)

        return analysis

    def _detect_frameworks(self, imports: List[str]) -> List[str]:
        """Detecta frameworks basándose en los imports."""
        detected = []
        for framework, patterns in self.framework_patterns.items():
            if any(
                pattern in import_name or import_name.startswith(pattern + ".")
                for import_name in imports
                for pattern in patterns
            ):
                detected.append(framework)
        return detected

    def _determine_domain_type(self, frameworks: List[str], content: str) -> str:
        """Determina el tipo de dominio basándose en frameworks y contenido."""
        if any(fw in frameworks for fw in ["fastapi", "django", "flask"]):
            if "middleware" in content.lower():
                return "web_middleware"
            elif any(
                word in content.lower() for word in ["router", "endpoint", "route"]
            ):
                return "web_api"
            return "web_application"
        elif "database" in frameworks:
            return "data_access"
        elif any(fw in frameworks for fw in ["data_processing", "ml_ai"]):
            return "data_science"
        elif "messaging" in frameworks:
            return "message_processing"
        elif "security" in frameworks:
            return "security"
        return "general"

    def _analyze_edge_cases(self, tree: ast.AST, content: str) -> List[str]:
        """Identifica posibles casos edge basándose en el código."""
        edge_cases = []

        # Buscar validaciones
        if "raise ValueError" in content or "raise TypeError" in content:
            edge_cases.append("Valores inválidos o tipos incorrectos")

        # Buscar manejo de None
        if " is None" in content or " is not None" in content:
            edge_cases.append("Valores None/null")

        # Buscar listas vacías
        if "len(" in content or "empty" in content.lower():
            edge_cases.append("Colecciones vacías")

        # Buscar límites numéricos
        if any(op in content for op in [">", "<", ">=", "<="]):
            edge_cases.append("Valores límite y rangos")

        # Buscar async/await
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                edge_cases.append("Operaciones asíncronas y timeouts")
                break

        # Buscar try/except
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                edge_cases.append("Manejo de excepciones")
                break

        return edge_cases

    def _analyze_performance_patterns(self, tree: ast.AST, content: str) -> List[str]:
        """Identifica consideraciones de performance."""
        performance = []

        # Loops anidados
        loop_depth = self._find_max_loop_depth(tree)
        if loop_depth > 1:
            performance.append(
                f"Loops anidados (profundidad: {loop_depth}) - testear con datasets grandes"
            )

        # Operaciones async
        if "async" in content or "await" in content:
            performance.append(
                "Operaciones asíncronas - testear timeouts y concurrencia"
            )

        # Database queries
        if any(
            word in content.lower()
            for word in ["query", "select", "insert", "update", "delete"]
        ):
            performance.append("Consultas de base de datos - testear con datos grandes")

        # File operations
        if any(word in content for word in ["open(", "read(", "write("]):
            performance.append("Operaciones de archivo - testear con archivos grandes")

        # Network calls
        if any(word in content for word in ["requests.", "httpx.", "urllib"]):
            performance.append(
                "Llamadas de red - testear latencia y fallos de conexión"
            )

        return performance

    def _analyze_error_patterns(self, tree: ast.AST, content: str) -> List[str]:
        """Identifica patrones de error comunes."""
        error_patterns = []

        # Tipos de excepciones encontradas
        exceptions = []
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Raise)
                and hasattr(node, "exc")
                and node.exc is not None
            ):
                exc = node.exc
                # ast.Name: direct exception type (e.g., ValueError)
                if isinstance(exc, ast.Name):
                    exceptions.append(exc.id)
                # ast.Attribute: e.g., module.Error
                elif isinstance(exc, ast.Attribute):
                    exceptions.append(exc.attr)
                # ast.Call: e.g., ValueError("msg")
                elif isinstance(exc, ast.Call):
                    if isinstance(exc.func, ast.Name):
                        exceptions.append(exc.func.id)
                    elif isinstance(exc.func, ast.Attribute):
                        exceptions.append(exc.func.attr)

        if exceptions:
            error_patterns.append(
                f"Excepciones específicas: {', '.join(set(exceptions))}"
            )

        # Patrones comunes de error
        if "ConnectionError" in content or "timeout" in content.lower():
            error_patterns.append("Errores de conexión y timeouts")

        if "ValidationError" in content or "validate" in content.lower():
            error_patterns.append("Errores de validación de datos")

        if "PermissionError" in content or "Forbidden" in content:
            error_patterns.append("Errores de permisos y autorización")

        if "FileNotFoundError" in content or "IOError" in content:
            error_patterns.append("Errores de sistema de archivos")

        return error_patterns

    def _analyze_integration_points(
        self, tree: ast.AST, content: str, imports: List[str]
    ) -> List[str]:
        """Identifica puntos de integración con servicios externos."""
        integrations = []

        # APIs externas
        if any(lib in imports for lib in ["requests", "httpx", "aiohttp"]):
            integrations.append("APIs REST externas")

        # Bases de datos
        if any(lib in imports for lib in ["sqlalchemy", "psycopg2", "mysql", "sqlite"]):
            integrations.append("Base de datos SQL")

        if any(lib in imports for lib in ["redis", "mongodb"]):
            integrations.append("Base de datos NoSQL")

        # ChromaDB específicamente
        if any("chromadb" in lib for lib in imports):
            integrations.append("Base de datos vectorial (ChromaDB)")

        # Sistemas de mensajería
        if any(lib in imports for lib in ["celery", "rq", "kafka", "rabbitmq"]):
            integrations.append("Sistemas de colas/mensajería")

        # Almacenamiento en la nube
        if any(word in content for word in ["boto3", "s3", "gcs", "azure"]):
            integrations.append("Servicios de nube")

        # Autenticación externa
        if any(word in content for word in ["oauth", "jwt", "ldap"]):
            integrations.append("Servicios de autenticación")

        return integrations

    def _suggest_testing_strategies(self, analysis: Dict) -> List[str]:
        """Sugiere estrategias de testing basándose en el análisis."""
        strategies = []

        domain = analysis["domain_type"]
        frameworks = analysis["detected_frameworks"]

        # Estrategias por dominio
        if domain == "web_middleware":
            strategies.extend(
                [
                    "Tests de middleware con requests simulados",
                    "Verificación de headers y modificación de request/response",
                    "Tests de performance con carga simulada",
                ]
            )
        elif domain == "web_api":
            strategies.extend(
                [
                    "Tests de endpoints con diferentes payloads",
                    "Validación de schemas de request/response",
                    "Tests de autenticación y autorización",
                ]
            )
        elif domain == "data_access":
            strategies.extend(
                [
                    "Tests con base de datos en memoria",
                    "Mocking de conexiones de BD",
                    "Tests de transacciones y rollback",
                ]
            )
        elif domain == "data_science":
            strategies.extend(
                [
                    "Mocking de modelos ML y embeddings",
                    "Tests con datasets sintéticos",
                    "Validación de dimensiones de vectores",
                    "Tests de performance con datos grandes ML",
                ]
            )

        # Estrategias por frameworks
        if "asyncio" in frameworks:
            strategies.append("Tests asíncronos con pytest-asyncio")

        if "database" in frameworks or "ml_ai" in frameworks:
            strategies.append("Fixtures de BD/vectorial con datos de prueba")

        if "api_client" in frameworks:
            strategies.append("Mocking de respuestas HTTP con responses/httpx_mock")

        if "ml_ai" in frameworks:
            strategies.extend(
                [
                    "Mocking de sentence_transformers",
                    "Tests unitarios para transformaciones de embeddings",
                    "Validación de similitudes coseno",
                ]
            )

        # Estrategias por casos edge
        if analysis["edge_cases"]:
            strategies.append("Tests parametrizados para casos edge")

        if analysis["integration_points"]:
            strategies.append("Tests de integración con servicios externos mockeados")

        return strategies

    def _find_max_loop_depth(self, tree: ast.AST) -> int:
        """Encuentra la profundidad máxima de loops anidados."""
        max_depth = 0

        def count_depth(node, current_depth=0):
            nonlocal max_depth
            if isinstance(node, (ast.For, ast.While)):
                current_depth += 1
                max_depth = max(max_depth, current_depth)

            for child in ast.iter_child_nodes(node):
                count_depth(child, current_depth)

        count_depth(tree)
        return max_depth

    def find_related_files(self, file_path: str) -> List[str]:
        """Encuentra recursivamente todos los archivos relacionados."""
        analyzed = set()
        to_analyze = [Path(file_path).resolve()]
        related_files = []

        while to_analyze:
            current = to_analyze.pop()
            if current in analyzed:
                continue

            analyzed.add(current)
            result = self.analyze_file(str(current))

            if "error" not in result:
                related_files.append(str(current))

                # Agregar imports locales para análisis
                for local_import in result["local_imports"]:
                    local_file = self._find_local_file(local_import, current)
                    if local_file and local_file not in analyzed:
                        to_analyze.append(local_file)

        return sorted(related_files)

    def generate_ai_prompt_data(self, file_path: str) -> Dict:
        """Genera toda la información necesaria para el prompt de la IA."""
        main_analysis = self.analyze_file(file_path)
        if "error" in main_analysis:
            return main_analysis

        related_files = self.find_related_files(file_path)

        # Analizar cada archivo relacionado
        files_analysis = {}
        all_advanced_data = {
            "edge_cases": set(),
            "performance_considerations": set(),
            "error_patterns": set(),
            "integration_points": set(),
            "testing_strategies": set(),
            "detected_frameworks": set(),
        }

        for rel_file in related_files:
            analysis = self.analyze_file(rel_file)
            files_analysis[rel_file] = analysis

            # Agregar datos avanzados
            if "error" not in analysis:
                for key in all_advanced_data.keys():
                    if key in analysis:
                        if isinstance(analysis[key], list):
                            all_advanced_data[key].update(analysis[key])
                        elif isinstance(analysis[key], str):
                            all_advanced_data[key].add(analysis[key])

        # Convertir sets a listas ordenadas
        advanced_analysis = {}
        for key in all_advanced_data:
            advanced_analysis[key] = sorted(list(all_advanced_data[key]))

        return {
            "main_file": main_analysis,
            "related_files": related_files,
            "files_analysis": files_analysis,
            "advanced_analysis": advanced_analysis,
            "summary": {
                "total_local_files": len(related_files),
                "external_dependencies": sorted(
                    list(
                        set(
                            dep
                            for analysis in files_analysis.values()
                            for dep in analysis.get("external_imports", [])
                        )
                    )
                ),
                "files_to_provide_to_ai": [
                    rel_file
                    for rel_file in related_files
                    if rel_file != main_analysis["file_path"]
                ],
            },
        }


def main():
    if len(sys.argv) < 2:
        print(
            "Uso: python dependency_analyzer.py <archivo_python> [directorio_proyecto]"
        )
        print("Ejemplo: python dependency_analyzer.py src/texto.py")
        return

    file_path = sys.argv[1]
    project_root = sys.argv[2] if len(sys.argv) > 2 else "."

    analyzer = DependencyAnalyzer(project_root)
    result = analyzer.generate_ai_prompt_data(file_path)

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return

    print("🔍 ANÁLISIS DE DEPENDENCIAS PARA TESTS")
    print("=" * 50)

    print(f"\n📁 Archivo principal: {result['main_file']['relative_path']}")
    print(
        f"📍 Ruta sugerida para test: {result['main_file']['suggested_test_path']['recommended']}"
    )

    # Información del dominio detectado
    if "domain_type" in result["main_file"]:
        print(f"🎯 Dominio detectado: {result['main_file']['domain_type']}")

    if (
        "detected_frameworks" in result["main_file"]
        and result["main_file"]["detected_frameworks"]
    ):
        print(f"🚀 Frameworks: {', '.join(result['main_file']['detected_frameworks'])}")

    print(
        f"\n📦 Dependencias externas ({len(result['summary']['external_dependencies'])}):"
    )
    for dep in result["summary"]["external_dependencies"]:
        print(f"  - {dep}")

    print(
        f"\n📋 Archivos locales relacionados ({len(result['summary']['files_to_provide_to_ai'])}):"
    )
    for file in result["summary"]["files_to_provide_to_ai"]:
        try:
            rel_path = Path(file).relative_to(Path(project_root).resolve())
            print(f"  - {rel_path}")
        except ValueError:
            # Si no puede calcular la ruta relativa, usar la absoluta
            print(f"  - {file}")

    if result["main_file"]["missing_local_files"]:
        print(f"\n⚠️  Archivos faltantes:")
        for missing in result["main_file"]["missing_local_files"]:
            print(f"  - {missing}")

    # Información avanzada
    advanced = result.get("advanced_analysis", {})

    if advanced.get("edge_cases"):
        print(f"\n🔍 Casos edge detectados ({len(advanced['edge_cases'])}):")
        for case in advanced["edge_cases"]:
            print(f"  - {case}")

    if advanced.get("performance_considerations"):
        print(
            f"\n📈 Consideraciones de performance ({len(advanced['performance_considerations'])}):"
        )
        for perf in advanced["performance_considerations"]:
            print(f"  - {perf}")

    if advanced.get("error_patterns"):
        print(f"\n🚨 Patrones de error ({len(advanced['error_patterns'])}):")
        for error in advanced["error_patterns"]:
            print(f"  - {error}")

    if advanced.get("integration_points"):
        print(f"\n🔄 Puntos de integración ({len(advanced['integration_points'])}):")
        for integration in advanced["integration_points"]:
            print(f"  - {integration}")

    # Combinar estrategias del archivo principal y análisis avanzado
    all_strategies = set()
    if "testing_strategies" in result["main_file"]:
        all_strategies.update(result["main_file"]["testing_strategies"])
    if advanced.get("testing_strategies"):
        all_strategies.update(advanced["testing_strategies"])

    if all_strategies:
        print(f"\n🧪 Estrategias de testing recomendadas ({len(all_strategies)}):")
        for strategy in sorted(all_strategies):
            print(f"  - {strategy}")

    print("\n" + "=" * 50)
    print("💡 INSTRUCCIONES PARA LA IA:")
    print("=" * 50)

    instructions = f"""
Para crear tests efectivos para '{result['main_file']['relative_path']}', necesito:

1. 📁 El archivo principal: {result['main_file']['relative_path']}

2. 📋 Los siguientes archivos de dependencias locales:
{chr(10).join(f"   - {Path(f).relative_to(Path(project_root).resolve()) if Path(f).resolve().is_relative_to(Path(project_root).resolve()) else Path(f).name}" for f in result['summary']['files_to_provide_to_ai'])}

3. 📍 Crear el test en: {result['main_file']['suggested_test_path']['recommended']}

4. 📦 Dependencias externas (ya las conozco):
{chr(10).join(f"   - {dep}" for dep in result['summary']['external_dependencies'])}"""

    if "domain_type" in result["main_file"]:
        instructions += (
            f"\n\n🎯 CONTEXTO DEL DOMINIO: {result['main_file']['domain_type']}"
        )

    # Combinar estrategias para las instrucciones
    all_strategies_for_prompt = set()
    if "testing_strategies" in result["main_file"]:
        all_strategies_for_prompt.update(result["main_file"]["testing_strategies"])
    if advanced.get("testing_strategies"):
        all_strategies_for_prompt.update(advanced["testing_strategies"])

    if all_strategies_for_prompt:
        instructions += f"\n\n🧪 ESTRATEGIAS DE TESTING RECOMENDADAS:\n"
        instructions += chr(10).join(
            f"   - {strategy}" for strategy in sorted(all_strategies_for_prompt)
        )

    if advanced.get("edge_cases"):
        instructions += f"\n\n🔍 CASOS EDGE A CONSIDERAR:\n"
        instructions += chr(10).join(f"   - {case}" for case in advanced["edge_cases"])

    if advanced.get("performance_considerations"):
        instructions += f"\n\n📈 MÉTRICAS DE PERFORMANCE A TESTEAR:\n"
        instructions += chr(10).join(
            f"   - {perf}" for perf in advanced["performance_considerations"]
        )

    if advanced.get("error_patterns"):
        instructions += f"\n\n🚨 PATRONES DE ERROR A VALIDAR:\n"
        instructions += chr(10).join(
            f"   - {error}" for error in advanced["error_patterns"]
        )

    if advanced.get("integration_points"):
        instructions += f"\n\n🔄 PUNTOS DE INTEGRACIÓN A MOCKEAR:\n"
        instructions += chr(10).join(
            f"   - {integration}" for integration in advanced["integration_points"]
        )

    instructions += "\n\n¿Puedes crear tests completos y robustos considerando todas estas dependencias y recomendaciones?"

    print(instructions)

    # Guardar resultado en JSON para uso programático
    output_file = f"test_analysis_{Path(file_path).stem}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Análisis completo guardado en: {output_file}")


if __name__ == "__main__":
    main()
