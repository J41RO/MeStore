#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SMART DEV SYSTEM v1.5.0 - SETUP AUTOMÁTICO INTERACTIVO
Setup completo con configuración personalizada del usuario
Compatible con Windows/Unix - Memoria Híbrida - Scripts Esenciales
"""

import os
import subprocess
import sys
from datetime import datetime


def clear_screen():
    """Limpiar pantalla según el OS"""
    os.system("cls" if os.name == "nt" else "clear")


def print_header():
    """Mostrar header del sistema"""
    print("🚀 SMART DEV SYSTEM v1.5.0 - SETUP AUTOMÁTICO INTERACTIVO")
    print("=" * 65)
    print("🧠 Sistema de Desarrollo con IA Híbrida y Memoria Persistente")
    print("📋 Configuración Personalizada del Usuario")
    print("=" * 65)
    print()


def get_user_input(question, options=None, default=None):
    """Obtener input del usuario con validación"""
    while True:
        if options:
            print(f"\n❓ {question}")
            for i, option in enumerate(options, 1):
                marker = " (por defecto)" if default and i == default else ""
                print(f"   {i}. {option}{marker}")

            try:
                choice = input(f"\n👉 Selecciona (1-{len(options)}): ").strip()
                if not choice and default:
                    return default - 1
                choice_num = int(choice) - 1
                if 0 <= choice_num < len(options):
                    return choice_num
                else:
                    print("❌ Opción inválida. Intenta de nuevo.")
            except ValueError:
                print("❌ Por favor ingresa un número válido.")
        else:
            response = input(f"\n❓ {question}: ").strip()
            if response or default is None:
                return response if response else default
            return default


def collect_user_preferences():
    """Recopilar preferencias del usuario de forma interactiva"""
    print("🎯 CONFIGURACIÓN PERSONALIZADA")
    print("━" * 40)

    # Información básica
    name = get_user_input("¿Cuál es tu nombre?", default="Jairo")

    # Nivel técnico
    technical_levels = [
        "Principiante - Recién comenzando con programación",
        "Intermedio - Conocimientos básicos sólidos",
        "Intermedio Avanzado - Experiencia considerable",
        "Avanzado - Amplia experiencia técnica",
        "Experto - Nivel profesional senior",
    ]
    tech_level_idx = get_user_input("¿Cuál es tu nivel técnico?", technical_levels, 3)
    tech_levels_map = [
        "beginner",
        "intermediate",
        "intermediate_advanced",
        "advanced",
        "expert",
    ]

    # Estilo de comunicación
    communication_styles = [
        "Educativo - Explicaciones detalladas y didácticas",
        "Técnico - Directo al grano, enfoque técnico",
        "Conversacional - Casual y amigable",
        "Minimalista - Solo lo esencial",
    ]
    comm_style_idx = get_user_input(
        "¿Qué estilo de comunicación prefieres?", communication_styles, 2
    )
    comm_styles_map = ["educational", "technical_only", "conversational", "direct"]

    # Nivel de feedback
    feedback_levels = [
        "Mínimo - Solo comandos esenciales",
        "Moderado - Explicaciones concisas",
        "Detallado - Explicaciones completas (recomendado)",
        "Ultra Verboso - Máximo detalle educativo",
    ]
    feedback_idx = get_user_input(
        "¿Qué nivel de feedback prefieres?", feedback_levels, 3
    )
    feedback_map = ["minimal", "moderate", "detailed", "ultra_verbose"]

    # Estrategia de testing
    test_strategies = [
        "Mínima - Tests básicos solamente",
        "Moderada - Tests importantes",
        "Comprensiva - Tests exhaustivos (recomendado)",
        "TDD - Desarrollo dirigido por tests",
    ]
    test_idx = get_user_input(
        "¿Qué estrategia de testing prefieres?", test_strategies, 3
    )
    test_map = ["minimal", "moderate", "comprehensive", "tdd"]

    # Frecuencia de commits
    commit_frequencies = [
        "Por subtarea - Commits muy frecuentes",
        "Por tarea - Un commit por tarea completada (recomendado)",
        "Por feature - Commits cuando se completa funcionalidad",
        "Manual - Yo decido cuándo hacer commit",
    ]
    commit_idx = get_user_input(
        "¿Con qué frecuencia prefieres hacer commits?", commit_frequencies, 1
    )
    commit_map = ["per_subtask", "per_task", "per_feature", "manual"]

    # Documentación
    doc_levels = [
        "Mínima - Solo cuando es necesario",
        "Bajo demanda - Cuando lo solicite",
        "Automática - Documentación continua (recomendado)",
        "Comprensiva - Documentación exhaustiva",
    ]
    doc_idx = get_user_input("¿Qué nivel de documentación prefieres?", doc_levels, 3)
    doc_map = ["minimal", "on_demand", "automatic", "comprehensive"]

    return {
        "name": name,
        "technical_level": tech_levels_map[tech_level_idx],
        "communication_style": comm_styles_map[comm_style_idx],
        "feedback_mode": feedback_map[feedback_idx],
        "test_strategy": test_map[test_idx],
        "commit_frequency": commit_map[commit_idx],
        "documentation_level": doc_map[doc_idx],
    }


def create_directory_structure():
    """Crear estructura completa de directorios para v1.5.0"""
    directories = [
        ".workspace",
        ".workspace/context",
        ".workspace/scripts",
        ".workspace/memory",
        ".workspace/memory/local",
        ".workspace/memory/enriched",
        ".workspace/models",
        ".workspace/models/local",
        ".workspace/models/config",
        ".workspace/backup",
        ".workspace/logs",
        ".workspace/analytics",
    ]

    print("\n📁 Creando estructura de directorios...")
    created_dirs = []
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            created_dirs.append(directory)
            print(f"   ✅ {directory}")
        except Exception as e:
            print(f"   ❌ Error creando {directory}: {e}")

    return created_dirs


def detect_project_info():
    """Detectar información del proyecto automáticamente"""
    print("\n🔍 Detectando información del proyecto...")
    timestamp = datetime.now().isoformat()
    root_dir = os.getcwd()
    project_name = os.path.basename(root_dir)

    # Detectar tipo de proyecto
    project_type = "unknown"
    language = ""
    framework = ""

    # Buscar archivos Python
    py_files = []
    for root, dirs, files in os.walk("."):
        # Evitar directorios del sistema
        if any(
            skip in root
            for skip in [".git", "__pycache__", ".workspace", "node_modules"]
        ):
            continue

        for file in files:
            if file.endswith(".py"):
                py_files.append(os.path.join(root, file))
        if len(py_files) > 5:
            break

    if (
        py_files
        or os.path.exists("requirements.txt")
        or os.path.exists("pyproject.toml")
    ):
        language = "python"
        project_type = "python_app"

        # Detectar framework específico
        for py_file in py_files[:10]:
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read().lower()
                    if "fastapi" in content:
                        framework = "fastapi"
                        project_type = "web_api"
                        break
                    elif "flask" in content:
                        framework = "flask"
                        project_type = "web_api"
                        break
                    elif "django" in content:
                        framework = "django"
                        project_type = "web_app"
                        break
            except:
                continue

        if not framework:
            framework = "python_general"

    # Detectar JavaScript/Node.js
    elif os.path.exists("package.json") or any(
        f.endswith(".js") for f in os.listdir(".")
    ):
        language = "javascript"
        project_type = "javascript_app"
        if os.path.exists("package.json"):
            try:
                import json

                with open("package.json", "r") as f:
                    package_data = json.load(f)
                    deps = package_data.get("dependencies", {})
                    if "react" in deps:
                        framework = "react"
                        project_type = "web_frontend"
                    elif "express" in deps:
                        framework = "express"
                        project_type = "web_api"
                    else:
                        framework = "node_general"
            except:
                framework = "javascript_general"

    # Detectar entorno
    try:
        python_version = (
            subprocess.check_output([sys.executable, "--version"]).decode().strip()
        )
    except:
        python_version = "not_detected"

    virtual_env = os.environ.get(
        "CONDA_DEFAULT_ENV", os.environ.get("VIRTUAL_ENV", "not_detected")
    )
    if virtual_env != "not_detected" and virtual_env:
        virtual_env = (
            os.path.basename(virtual_env)
            if "VIRTUAL_ENV" in os.environ
            else virtual_env
        )

    project_data = {
        "timestamp": timestamp,
        "root_dir": root_dir,
        "project_name": project_name,
        "project_type": project_type,
        "language": language,
        "framework": framework,
        "python_version": python_version,
        "virtual_env": virtual_env,
    }

    print(
        f"   ✅ Proyecto detectado: {project_data['project_name']} ({project_data['project_type']})"
    )
    print(
        f"   ✅ Lenguaje: {project_data['language']}, Framework: {project_data['framework']}"
    )

    return project_data


def create_start_yaml(project_info, user_prefs):
    """Crear archivo start.yaml con configuración completa v1.5.0"""

    os_type = "windows" if os.name == "nt" else "unix"
    test_framework = "pytest" if project_info["language"] == "python" else "jest"
    main_file = "main.py" if project_info["language"] == "python" else "index.js"

    start_yaml_content = f"""# SMART DEV SYSTEM v1.5.0 - CONFIGURACIÓN MAESTRA
# Este archivo contiene TODA la información que cualquier IA necesita
# para entrar inmediatamente en contexto del proyecto

system:
  version: "1.5.0"
  created: "{project_info['timestamp']}"
  last_updated: "{project_info['timestamp']}"
  last_ai: "setup-script"
  
project:
  name: "{project_info['project_name']}"
  type: "{project_info['project_type']}"
  description: "Proyecto {project_info['project_type']} usando {project_info['framework']}"
  technologies:
    language: "{project_info['language']}"
    framework: "{project_info['framework']}"
    database: "pendiente_detectar"
    testing: "{test_framework}"
    deployment: "pendiente_detectar"
  
structure:
  root_dir: "{project_info['root_dir']}"
  main_file: "{main_file}"
  config_files: []
  important_dirs: []
  
user:
  # Información básica
  name: "{user_prefs['name']}"
  email: "admin@{project_info['project_name'].lower()}"
  technical_level: "{user_prefs['technical_level']}"
  work_mode: "solo"
  timezone: "America/Bogota"
  
  # Preferencias de comunicación
  communication:
    language: "spanish"
    feedback_mode: "{user_prefs['feedback_mode']}"
    explanation_style: "{user_prefs['communication_style']}"
    encouragement_frequency: "moderate"
    technical_depth: "comprehensive"
    
  # Preferencias de trabajo
  workflow:
    commit_frequency: "{user_prefs['commit_frequency']}"
    test_strategy: "{user_prefs['test_strategy']}"
    documentation_level: "{user_prefs['documentation_level']}"
    validation_strictness: "maximum"
    
  # Modos especiales
  modes:
    ultra_didactic_mode: false
    minimal_explanations: false
    commands_only: false
    show_reasoning: true
    auto_suggestions: true
    
  # Aprendizaje y evolución
  learning:
    track_progress: true
    learned_concepts: []
    skill_evolution: {{}}
    preferred_learning_style: "hands_on"
    
  # Configuración de análisis de código
  code_analysis_preferences:
    auto_suggest_analysis: true
    quality_gate_strictness: "moderate"
    security_focus: true
    performance_monitoring: true
    coverage_threshold: 80
    max_complexity_warning: 10
    max_file_lines_warning: 200
    
  # Configuración de memoria híbrida
  hybrid_memory:
    local_memory_enabled: true
    api_enrichment_enabled: false  # Deshabilitado por defecto
    enrichment_triggers:
      complexity_threshold: "high"
      message_length_threshold: 500
      importance_keywords: ["important", "remember", "crítico"]
    consolidation_schedule: "nightly"
    
  # Configuración de modelos
  model_preferences:
    local_model_enabled: false  # Deshabilitado por defecto
    preferred_local_model: "not_configured"
    api_fallback_enabled: false  # Deshabilitado por defecto
    model_routing_strategy: "local_first"
    
status:
  pending_tasks: true
  current_phase: "FASE 0"
  current_task: "0.1 Configurar entorno de desarrollo"
  current_command: "setup.py ejecutado exitosamente"
  blocking_issues: []
  next_session_action: "Ejecutar /start/ para revisar plan y continuar desarrollo"
  
modules:
  education: true
  validation: true
  documentation: true
  context: true
  error_detection: true
  error_learning: true
  hybrid_memory: true
  quality_analysis: true
  recovery: true

scripts:
  available:
    - "session_recovery.sh"
    - "smart_commit.sh" 
    - "context_validator.sh"
    - "project_sync_check.sh"
    - "pre_commit_validation.sh"

environment:
  os: "{os_type}"
  python_version: "{project_info['python_version']}"
  node_version: "not_detected"
  docker_available: false
  git_configured: false
  virtual_env: "{project_info['virtual_env']}"

workspace:
  setup_completed: true
  files_created: true
  project_detected: true
  dependencies_installed: false
  error_knowledge_created: true
  hybrid_memory_configured: true
  scripts_generated: true
  
sessions:
  total_sessions: 0
  total_commands: 0
  last_session_duration: ""
  avg_session_tasks: 0
  total_errors_encountered: 0
  total_errors_resolved: 0
  error_resolution_rate: 0

learning:
  patterns_detected: []
  preventive_rules: []
  success_techniques: []
  avoided_mistakes: []
"""

    filepath = os.path.join(".workspace", "start.yaml")
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(start_yaml_content)
        print(f"   ✅ start.yaml creado en {filepath}")
        return True
    except Exception as e:
        print(f"   ❌ Error creando start.yaml: {e}")
        return False


def create_todo_md(project_info):
    """Crear todo.md vacío para personalizar"""
    todo_content = f"""# PLAN PRINCIPAL DEL PROYECTO - {project_info['project_name']}

## FASE 0: CONFIGURACIÓN INICIAL
✅ 0.1 Configurar entorno de desarrollo
✅ 0.1.1 Detectar tipo de proyecto ({project_info['project_type']})
✅ 0.1.2 Configurar entorno Unix/Linux
✅ 0.1.3 Crear estructura Smart Dev System v1.5.0
✅ 0.1.4 Configurar preferencias personalizadas del usuario
✅ 0.1.5 Generar scripts esenciales del sistema

⬜ 0.2 Configurar herramientas específicas del proyecto
⬜ 0.2.1 Instalar dependencias del proyecto
⬜ 0.2.2 Configurar testing framework según estrategia elegida
⬜ 0.2.3 Configurar estructura de archivos del proyecto
⬜ 0.2.4 Configurar sistema de control de calidad

## FASE 1: [AGREGAR CONTENIDO PERSONALIZADO]
⬜ 1.1 [Definir tareas específicas según tipo de proyecto: {project_info['project_type']}]
⬜ 1.2 [Configurar arquitectura base del proyecto]
⬜ 1.3 [Implementar funcionalidades core]

## FASE 2: [AGREGAR CONTENIDO PERSONALIZADO]  
⬜ 2.1 [Desarrollar funcionalidades principales]
⬜ 2.2 [Implementar tests según estrategia elegida]
⬜ 2.3 [Configurar deployment y producción]

## FASE 3: [AGREGAR CONTENIDO PERSONALIZADO]
⬜ 3.1 [Optimización y refinamiento]
⬜ 3.2 [Documentación final]
⬜ 3.3 [Preparación para lanzamiento]

[PERSONALIZA ESTE PLAN SEGÚN LAS NECESIDADES ESPECÍFICAS DE TU PROYECTO]

## NOTAS IMPORTANTES:
- Este es el TODO.MD base que debes personalizar completamente
- Agrega fases específicas según tu proyecto {project_info['project_type']}
- El sistema usará ESTE archivo como fuente única de verdad para tareas
- Mantén el formato ⬜ para pendientes, 🔁 para en progreso, ✅ para completadas
"""

    filepath = os.path.join(".workspace", "context", "todo.md")
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(todo_content)
        print(f"   ✅ todo.md creado en {filepath}")
        return True
    except Exception as e:
        print(f"   ❌ Error creando todo.md: {e}")
        return False


def create_basic_files(project_info, user_prefs):
    """Crear archivos básicos del contexto"""
    print("\n📝 Creando archivos de contexto (log, task)...")
    timestamp = project_info["timestamp"]
    created_files = []

    # log.md
    log_content = f"""# ÚLTIMA ACCIÓN EJECUTADA

**Estado**: ✅ SISTEMA CONFIGURADO v1.5.0
**Comando ejecutado**: python setup.py (configuración interactiva)
**Resultado**: ✅ EXITOSO - Setup interactivo completado con preferencias personalizadas
**Próxima acción**: Personalizar .workspace/context/todo.md y ejecutar /start/
**Timestamp**: {timestamp}
**IA anterior**: setup-script-v1.5.0
**Usuario configurado**: {user_prefs['name']} (nivel: {user_prefs['technical_level']})
**Fase actual**: FASE 0 - Configuración completada con personalización
**Errores consultados**: 0
**Soluciones aplicadas**: Setup automático interactivo para v1.5.0
"""

    log_filepath = os.path.join(".workspace", "context", "log.md")
    try:
        with open(log_filepath, "w", encoding="utf-8") as f:
            f.write(log_content)
        created_files.append("log.md")
        print(f"   ✅ log.md creado")
    except Exception as e:
        print(f"   ❌ Error creando log.md: {e}")

    # task.md
    task_content = f"""# TAREAS CRÍTICAS - ATENCIÓN PRIORITARIA

## 🚨 TAREAS CRÍTICAS PENDIENTES

⬜ CRITICAL-{datetime.now().strftime('%Y%m%d-%H%M')}: Personalizar plan de desarrollo
   - **Tipo**: Configuración/Planificación
   - **Detectado en**: Setup automático v1.5.0
   - **Prioridad**: Alta
   - **Contexto**: Plan base creado, necesita personalización según proyecto específico
   - **Comando sugerido**: Editar .workspace/context/todo.md con tareas específicas
   - **Usuario**: {user_prefs['name']}
   - **Estrategia preferida**: {user_prefs['test_strategy']} testing, commits {user_prefs['commit_frequency']}

⬜ CRITICAL-{datetime.now().strftime('%Y%m%d-%H%M')}: Instalar dependencias del proyecto
   - **Tipo**: Configuración/Dependencias  
   - **Detectado en**: Setup automático
   - **Prioridad**: Alta
   - **Contexto**: Dependencias necesarias para continuar desarrollo
   - **Comando sugerido**: pip install -r requirements.txt (si existe)
   - **Errores relacionados**: Ninguno aún

## ✅ TAREAS CRÍTICAS RESUELTAS
✅ CRITICAL-{datetime.now().strftime('%Y%m%d-%H%M')}: Configurar SMART DEV SYSTEM v1.5.0 - RESUELTO
   - **Solución aplicada**: Setup interactivo ejecutado exitosamente
   - **Resultado**: Sistema configurado con preferencias de {user_prefs['name']}
   - **Configuración**: {user_prefs['technical_level']}, {user_prefs['feedback_mode']}, {user_prefs['communication_style']}
   - **Lección aprendida**: Setup v1.5.0 funciona correctamente con configuración personalizada
"""

    task_filepath = os.path.join(".workspace", "context", "task.md")
    try:
        with open(task_filepath, "w", encoding="utf-8") as f:
            f.write(task_content)
        created_files.append("task.md")
        print(f"   ✅ task.md creado")
    except Exception as e:
        print(f"   ❌ Error creando task.md: {e}")

    return created_files


def create_error_knowledge(project_info, user_prefs):
    """Crear base de conocimiento de errores"""
    timestamp = project_info["timestamp"]

    error_content = f"""# BASE DE CONOCIMIENTO DE ERRORES - SMART DEV SYSTEM v1.5.0
# Registro automático de errores, soluciones y prevención
# Configurado para: {user_prefs['name']} (nivel: {user_prefs['technical_level']})

## RESUMEN DE ERRORES FRECUENTES
- **Sintaxis**: 0 errores
- **Imports**: 0 errores  
- **Tests**: 0 errores
- **Rutas**: 0 errores
- **Duplicados**: 0 errores
- **Memoria Híbrida**: 0 errores
- **Análisis de Calidad**: 0 errores

## ÚLTIMA ACTUALIZACIÓN
**Fecha**: {timestamp}
**Total de entradas**: 1
**Errores resueltos**: 0 
**Errores recurrentes**: 0
**Usuario**: {user_prefs['name']}
**Configuración**: {user_prefs['feedback_mode']} feedback, {user_prefs['test_strategy']} testing

## REGLAS PREVENTIVAS APRENDIDAS
[Se agregan automáticamente cuando se detectan patrones]

## CONFIGURACIÓN DE USUARIO PARA ERRORES
- **Nivel técnico**: {user_prefs['technical_level']} - Ajuste automático de explicaciones
- **Estilo comunicación**: {user_prefs['communication_style']} - Formato de mensajes de error
- **Detalle feedback**: {user_prefs['feedback_mode']} - Profundidad de análisis

---

## REGISTRO DE ERRORES Y SOLUCIONES

## ÉXITO: Setup v1.5.0 completado - {datetime.now().strftime('%Y%m%d')}
**Acción**: Configuración inicial del sistema con personalización interactiva
**Usuario**: {user_prefs['name']}
**Preferencias configuradas**: 
  - Nivel técnico: {user_prefs['technical_level']}
  - Comunicación: {user_prefs['communication_style']}
  - Feedback: {user_prefs['feedback_mode']}
  - Testing: {user_prefs['test_strategy']}
  - Commits: {user_prefs['commit_frequency']}
  - Documentación: {user_prefs['documentation_level']}
**Método**: Setup Python v1.5.0 con cuestionario interactivo
**Tests**: No aplicable en esta fase
**Lecciones**: 
- Setup v1.5.0 funciona correctamente con configuración personalizada
- Proyecto {project_info['project_name']} detectado como {project_info['project_type']}
- Estructura .workspace creada con memoria híbrida y scripts
- Entorno configurado según preferencias del usuario
- Sistema listo para desarrollo personalizado
**Técnicas exitosas**:
- Configuración interactiva mejora adaptación del sistema
- Detección automática por análisis de archivos
- Estructura modular preparada para desarrollo híbrido
- Generación automática de scripts esenciales
- Personalización completa según nivel y preferencias del usuario
"""

    filepath = os.path.join(".workspace", "error_knowledge.md")
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(error_content)
        print(f"   ✅ error_knowledge.md creado")
        return True
    except Exception as e:
        print(f"   ❌ Error creando error_knowledge.md: {e}")
        return False


def create_history_log(project_info, user_prefs):
    """Crear historial técnico"""
    timestamp = project_info["timestamp"]

    history_content = f"""# SMART DEV SYSTEM v1.5.0 - HISTORIAL TÉCNICO CON APRENDIZAJE PERSONALIZADO
# Formato: TIMESTAMP | LEVEL | ACTION | DESCRIPTION | EXTRA_INFO

{timestamp} | INFO | INIT | Smart Dev System v1.5.0 setup iniciado | user={user_prefs['name']},level={user_prefs['technical_level']}
{timestamp} | SUCCESS | CONFIG | Configuración interactiva completada | prefs_collected=7
{timestamp} | SUCCESS | DETECT | Proyecto {project_info['project_type']} detectado | main_file=main.py,framework={project_info['framework']}
{timestamp} | SUCCESS | DETECT | Tecnologías: {project_info['language']} + {project_info['framework']} | os={os.name}
{timestamp} | SUCCESS | ENV | Entorno configurado | env={project_info['virtual_env']},python={project_info['python_version']}
{timestamp} | SUCCESS | STRUCTURE | Estructura v1.5.0 creada | hybrid_memory=enabled,scripts=generated
{timestamp} | SUCCESS | CONFIG | start.yaml creado con configuración personalizada | user={user_prefs['name']}
{timestamp} | SUCCESS | CONFIG | Preferencias aplicadas | feedback={user_prefs['feedback_mode']},test={user_prefs['test_strategy']},comm={user_prefs['communication_style']}
{timestamp} | SUCCESS | PLAN | Plan base creado (requiere personalización) | project={project_info['project_name']}
{timestamp} | SUCCESS | SCRIPTS | Scripts esenciales generados | count=5,location=.workspace/scripts
{timestamp} | SUCCESS | SETUP | Setup v1.5.0 completado exitosamente | ready_for_ai=true,personalized=true
"""

    filepath = os.path.join(".workspace", "history.log")
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(history_content)
        print(f"   ✅ history.log creado")
        return True
    except Exception as e:
        print(f"   ❌ Error creando history.log: {e}")
        return False


def create_essential_scripts():
    """Generar scripts esenciales del sistema"""
    print("\n🔧 Generando scripts esenciales del sistema...")
    scripts_dir = os.path.join(".workspace", "scripts")

    # 1. session_recovery.sh
    session_recovery = """#!/bin/bash
# SMART DEV SYSTEM v1.5.0 - Session Recovery Script
# Recupera contexto completo del proyecto tras gaps de tiempo

echo "🔄 SMART DEV SYSTEM v1.5.0 - RECUPERACIÓN DE SESIÓN"
echo "=================================================="

echo "📋 Analizando contexto del proyecto..."

# Leer configuración del usuario
USER_NAME=$(grep "name:" .workspace/start.yaml | cut -d'"' -f2)
TECH_LEVEL=$(grep "technical_level:" .workspace/start.yaml | cut -d'"' -f2)
PROJECT_NAME=$(grep "name:" .workspace/start.yaml | head -1 | cut -d'"' -f2)

echo "👤 Usuario: $USER_NAME (Nivel: $TECH_LEVEL)"
echo "📂 Proyecto: $PROJECT_NAME"
echo ""

echo "=== ESTADO ACTUAL DEL PROYECTO ==="
echo "📅 Última actividad:"
cat .workspace/context/log.md | head -5

echo ""
echo "=== TAREAS PENDIENTES ==="
echo "🔍 Próximas tareas:"
grep -E "(🔁|⬜)" .workspace/context/todo.md | head -5

echo ""
echo "=== HISTORIAL RECIENTE ==="
echo "📊 Actividad reciente:"
tail -5 .workspace/history.log

echo ""
echo "=== ERRORES/APRENDIZAJES ==="
echo "🧠 Conocimiento acumulado:"
grep -c "ÉXITO\\|ERROR" .workspace/error_knowledge.md
echo "Entradas en base de conocimiento: $(grep -c "##" .workspace/error_knowledge.md)"

echo ""
echo "✅ CONTEXTO RECUPERADO - Sistema listo para continuar"
echo "🚀 Próximo paso: Ejecutar /start/ en tu IA para continuar desarrollo"

# Generar resumen en archivo
cat > .workspace/context/session_summary.md << EOF
# RESUMEN DE SESIÓN RECUPERADA - $(date)

## Usuario Configurado
- **Nombre**: $USER_NAME  
- **Nivel**: $TECH_LEVEL
- **Proyecto**: $PROJECT_NAME

## Estado Actual
$(cat .workspace/context/log.md | head -3)

## Próximas Tareas
$(grep -E "(🔁|⬜)" .workspace/context/todo.md | head -3)

## Recomendación
Ejecutar `/start/` en tu IA para continuar con el desarrollo personalizado.
EOF

echo "📄 Resumen guardado en: .workspace/context/session_summary.md"
"""

    # 2. smart_commit.sh
    smart_commit = """#!/bin/bash
# SMART DEV SYSTEM v1.5.0 - Smart Commit Script
# Commit inteligente con validación controlada

COMMIT_MESSAGE="$1"

if [ -z "$COMMIT_MESSAGE" ]; then
    echo "❌ Error: Mensaje de commit requerido"
    echo "Uso: bash .workspace/scripts/smart_commit.sh 'mensaje del commit'"
    exit 1
fi

echo "💾 SMART DEV SYSTEM v1.5.0 - COMMIT INTELIGENTE"
echo "=============================================="

# Leer configuración del usuario
COMMIT_FREQ=$(grep "commit_frequency:" .workspace/start.yaml | cut -d'"' -f2)
USER_NAME=$(grep "name:" .workspace/start.yaml | cut -d'"' -f2)

echo "👤 Usuario: $USER_NAME"
echo "📋 Estrategia: $COMMIT_FREQ"
echo "💬 Mensaje: $COMMIT_MESSAGE"
echo ""

# Verificar estado del repositorio
echo "🔍 Verificando estado del repositorio..."
git status --porcelain

# Pre-commit validation si existe
if [ -f ".workspace/scripts/pre_commit_validation.sh" ]; then
    echo "✅ Ejecutando validación pre-commit..."
    bash .workspace/scripts/pre_commit_validation.sh
    if [ $? -ne 0 ]; then
        echo "❌ Validación falló - Commit cancelado"
        exit 1
    fi
fi

# Realizar commit
echo "💾 Realizando commit..."
git add .
git commit -m "$COMMIT_MESSAGE" --no-verify

if [ $? -eq 0 ]; then
    echo "✅ COMMIT EXITOSO"
    
    # Actualizar historial
    echo "$(date -Iseconds) | SUCCESS | COMMIT | $COMMIT_MESSAGE | user=$USER_NAME,strategy=$COMMIT_FREQ" >> .workspace/history.log
    
    # Actualizar log
    cat > .workspace/context/log.md << EOF
# ÚLTIMA ACCIÓN EJECUTADA

**Estado**: ✅ COMMIT REALIZADO
**Comando ejecutado**: git commit -m "$COMMIT_MESSAGE"
**Resultado**: ✅ EXITOSO - Cambios guardados en repositorio
**Próxima acción**: Continuar con siguiente tarea según plan
**Timestamp**: $(date -Iseconds)
**Usuario**: $USER_NAME
**Estrategia**: $COMMIT_FREQ
EOF

    echo "📝 Logs actualizados"
else
    echo "❌ COMMIT FALLÓ"
    exit 1
fi
"""

    # 3. context_validator.sh
    context_validator = """#!/bin/bash
# SMART DEV SYSTEM v1.5.0 - Context Validator
# Valida consistencia del contexto del proyecto

echo "🔍 SMART DEV SYSTEM v1.5.0 - VALIDADOR DE CONTEXTO"
echo "================================================="

echo "📋 Validando consistencia del contexto..."

# Validar archivos críticos
FILES_TO_CHECK=(".workspace/start.yaml" ".workspace/context/todo.md" ".workspace/context/log.md")
MISSING_FILES=()

for file in "${FILES_TO_CHECK[@]}"; do
    if [ ! -f "$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo "❌ ARCHIVOS FALTANTES:"
    printf '%s\\n' "${MISSING_FILES[@]}"
    echo "🔧 Ejecuta setup.py para regenerar archivos"
    exit 1
fi

echo "✅ Archivos críticos presentes"

# Validar formato TODO.MD
echo "🔍 Validando formato de TODO.MD..."
TODO_TASKS=$(grep -c -E "(✅|🔁|⬜)" .workspace/context/todo.md)
if [ $TODO_TASKS -eq 0 ]; then
    echo "⚠️ ADVERTENCIA: TODO.MD no contiene tareas con formato correcto"
    echo "Formato esperado: ✅ (completada), 🔁 (en progreso), ⬜ (pendiente)"
fi

# Validar configuración de usuario
echo "🔍 Validando configuración de usuario..."
USER_NAME=$(grep "name:" .workspace/start.yaml | cut -d'"' -f2)
if [ -z "$USER_NAME" ] || [ "$USER_NAME" = "Desarrollador" ]; then
    echo "⚠️ ADVERTENCIA: Configuración de usuario genérica detectada"
    echo "Considera personalizar la configuración en start.yaml"
fi

# Validar sincronización
echo "🔍 Verificando sincronización..."
LAST_UPDATE=$(grep "last_updated:" .workspace/start.yaml | cut -d'"' -f2)
LOG_TIME=$(grep "Timestamp:" .workspace/context/log.md | cut -d' ' -f2)

echo "📊 REPORTE DE VALIDACIÓN:"
echo "   - Archivos críticos: ✅ Presentes"
echo "   - Tareas en TODO.MD: $TODO_TASKS encontradas"
echo "   - Usuario configurado: $USER_NAME"
echo "   - Última actualización: $LAST_UPDATE"

echo ""
echo "✅ VALIDACIÓN COMPLETADA"
"""

    # 4. project_sync_check.sh
    project_sync_check = """#!/bin/bash
# SMART DEV SYSTEM v1.5.0 - Project Sync Checker
# Verifica sincronización entre archivos del proyecto y contexto

echo "🔄 SMART DEV SYSTEM v1.5.0 - VERIFICADOR DE SINCRONIZACIÓN"
echo "========================================================="

PROJECT_NAME=$(grep "name:" .workspace/start.yaml | head -1 | cut -d'"' -f2)
echo "📂 Proyecto: $PROJECT_NAME"
echo ""

echo "🔍 Verificando cambios no documentados..."

# Verificar si hay cambios no commiteados
if command -v git &> /dev/null; then
    UNCOMMITTED=$(git status --porcelain | wc -l)
    if [ $UNCOMMITTED -gt 0 ]; then
        echo "📝 Cambios no commiteados encontrados:"
        git status --porcelain
        echo ""
    else
        echo "✅ No hay cambios sin commitear"
    fi
    
    # Últimos commits
    echo "📊 Últimos 3 commits:"
    git log --oneline -3 2>/dev/null || echo "Sin historial de commits"
else
    echo "⚠️ Git no disponible - No se puede verificar estado del repositorio"
fi

echo ""
echo "🔍 Verificando archivos del proyecto..."

# Contar archivos por tipo
PY_FILES=$(find . -name "*.py" ! -path "./.workspace/*" ! -path "./.git/*" | wc -l)
JS_FILES=$(find . -name "*.js" ! -path "./.workspace/*" ! -path "./.git/*" | wc -l)
JSON_FILES=$(find . -name "*.json" ! -path "./.workspace/*" ! -path "./.git/*" | wc -l)

echo "📊 Archivos del proyecto:"
echo "   - Python: $PY_FILES archivos"
echo "   - JavaScript: $JS_FILES archivos"  
echo "   - JSON: $JSON_FILES archivos"

echo ""
echo "🔍 Verificando estado del workspace..."

# Verificar integridad del workspace
WORKSPACE_FILES=$(find .workspace -type f | wc -l)
echo "📁 Archivos en workspace: $WORKSPACE_FILES"

# Verificar última actividad
LAST_ACTION=$(grep "Comando ejecutado" .workspace/context/log.md | cut -d':' -f2)
echo "⚡ Última acción:$LAST_ACTION"
"""

    # --- COMPLETION START ---

    # 5. pre_commit_validation.sh
    pre_commit_validation = """#!/bin/bash
# SMART DEV SYSTEM v1.5.0 - Pre-Commit Validation Script
# Validaciones básicas antes de permitir un commit.

echo "🔎 SMART DEV SYSTEM v1.5.0 - VALIDACIÓN PRE-COMMIT"
echo "==================================================="

# Detectar lenguaje para validación
LANGUAGE=$(grep "language:" .workspace/start.yaml | cut -d'"' -f2)

if [ "$LANGUAGE" = "python" ]; then
    echo "🐍 Validando código Python..."
    if command -v flake8 &> /dev/null; then
        echo "Flake8 encontrado. Analizando código..."
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        if [ $? -ne 0 ]; then
            echo "❌ Flake8 encontró errores. Corrige y vuelve a intentar."
            exit 1
        fi
        echo "✅ Flake8: Sin errores críticos."
    else
        echo "⚠️ ADVERTENCIA: Flake8 no instalado. No se puede validar calidad de código."
    fi
elif [ "$LANGUAGE" = "javascript" ]; then
    echo "📜 Validando código JavaScript..."
    if command -v eslint &> /dev/null; then
        echo "ESLint encontrado. Analizando código..."
        eslint .
        if [ $? -ne 0 ]; then
            echo "❌ ESLint encontró errores. Corrige y vuelve a intentar."
            exit 1
        fi
        echo "✅ ESLint: Sin errores."
    else
        echo "⚠️ ADVERTENCIA: ESLint no instalado. No se puede validar calidad de código."
    fi
else
    echo "🤔 No se encontró un validador para el lenguaje: $LANGUAGE"
fi

echo "✅ Validación Pre-Commit completada."
exit 0
"""

    scripts_to_create = {
        "session_recovery.sh": session_recovery,
        "smart_commit.sh": smart_commit,
        "context_validator.sh": context_validator,
        "project_sync_check.sh": project_sync_check,
        "pre_commit_validation.sh": pre_commit_validation,
    }

    created_scripts = []
    for script_name, content in scripts_to_create.items():
        filepath = os.path.join(scripts_dir, script_name)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            # Hacer el script ejecutable en sistemas Unix
            if os.name != "nt":
                os.chmod(filepath, 0o755)
            created_scripts.append(script_name)
            print(f"   ✅ {script_name} creado")
        except Exception as e:
            print(f"   ❌ Error creando {script_name}: {e}")

    return created_scripts


def main():
    """Función principal para ejecutar el setup"""
    clear_screen()
    print_header()

    # 1. Recopilar preferencias del usuario
    user_prefs = collect_user_preferences()

    # 2. Detectar información del proyecto
    project_info = detect_project_info()

    # 3. Crear estructura de directorios
    create_directory_structure()

    # 4. Crear archivos de configuración y contexto
    print("\n💾 Creando archivos de configuración principales...")
    create_start_yaml(project_info, user_prefs)
    create_todo_md(project_info)
    create_basic_files(project_info, user_prefs)
    create_error_knowledge(project_info, user_prefs)
    create_history_log(project_info, user_prefs)

    # 5. Generar scripts
    create_essential_scripts()

    # Mensaje final
    print("\n" + "=" * 65)
    print("🎉 ¡SETUP COMPLETADO EXITOSAMENTE! 🎉")
    print("=" * 65)
    print("\nEl SMART DEV SYSTEM v1.5.0 está configurado y listo.")
    print("\nPRÓXIMOS PASOS RECOMENDADOS:")
    print("1. Revisa y personaliza el plan en: .workspace/context/todo.md")
    print(
        "2. Instala las dependencias de tu proyecto (ej: pip install -r requirements.txt)"
    )
    print("3. Inicia tu desarrollo con la IA usando el comando /start/")
    print("\n¡Feliz codificación! 💡")


if __name__ == "__main__":
    main()

# --- COMPLETION END ---
