#!/usr/bin/env python3
"""
create_workspace.py - Generador de Estructura Workspace Completa
Crea la estructura completa del .workspace con todas las carpetas y archivos base
"""

import os
from pathlib import Path
from datetime import datetime

def create_workspace_structure():
    """
    Crea la estructura completa del .workspace
    """
    print("🏗️ Creando estructura completa del workspace...")
    
    # Directorio base
    workspace_root = Path(".workspace")
    
    # Lista completa de directorios a crear
    directories = [
        # Context
        "context",
        "context/requirements", 
        "context/architecture",
        
        # CEO Office
        "ceo-office",
        "ceo-office/project-analysis",
        "ceo-office/agent-recommendations",
        "ceo-office/department-structure", 
        "ceo-office/strategic-decisions",
        
        # Personal Office
        "personal-office",
        "personal-office/assistants",
        "personal-office/reports",
        
        # Departments
        "departments",
        "departments/command-center",
        "departments/command-center/roles",
        "departments/core-architecture", 
        "departments/core-architecture/roles",
        "departments/development-engines",
        "departments/development-engines/roles",
        "departments/specialized-domains",
        "departments/specialized-domains/roles",
        "departments/quality-operations",
        "departments/quality-operations/roles",
        "departments/automation-utilities",
        "departments/automation-utilities/roles",
        
        # Channels
        "channels",
        "channels/management",
        "channels/frontend", 
        "channels/backend",
        "channels/devops",
        "channels/integration",
        
        # Status
        "status",
        "status/daily-reports",
        
        # Standards
        "standards",
        "standards/coding-standards",
        
        # Tasks
        "tasks",
        "tasks/backlog",
        "tasks/in-progress",
        "tasks/review", 
        "tasks/done",
        
        # Knowledge
        "knowledge",
        "knowledge/troubleshooting",
        
        # Changes
        "changes",
        
        # Alerts
        "alerts",
        "alerts/incident-reports",
        
        # Metrics
        "metrics",
        
        # Security
        "security",
        
        # Templates
        "templates",
        
        # Coordination
        "coordination"
    ]
    
    # Crear todos los directorios
    for dir_path in directories:
        full_path = workspace_root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {dir_path}")
    
    print(f"\n📁 Creados {len(directories)} directorios")
    
    # Crear archivos base esenciales
    create_base_files(workspace_root)
    
    print("🎉 ¡Estructura del workspace creada exitosamente!")

def create_base_files(workspace_root: Path):
    """
    Crea los archivos base esenciales
    """
    print("\n📄 Creando archivos base...")
    
    files_content = {
        # Context files
        "context/project-brief.md": """# Project Brief

## 🎯 Objetivo del Proyecto
[Descripción del objetivo principal]

## 📋 Alcance
[Definir qué incluye y qué no incluye el proyecto]

## 👥 Stakeholders
[Lista de stakeholders principales]

## 📅 Timeline
[Timeline general del proyecto]

## 💰 Budget
[Restricciones de presupuesto]
""",

        "context/requirements/functional.md": """# Requerimientos Funcionales

## 🎯 Características Principales
[ ] Feature 1
[ ] Feature 2 
[ ] Feature 3

## 👤 User Stories
- Como usuario, quiero...
- Como admin, necesito...

## 🔄 Flujos de Trabajo
[Describir flujos principales]
""",

        "context/requirements/non-functional.md": """# Requerimientos No Funcionales

## 🚀 Performance
- Tiempo de carga: < 2 segundos
- Disponibilidad: 99.9%

## 🔐 Security
- Autenticación requerida
- Datos encriptados

## 📱 Usability
- Responsive design
- Accesibilidad WCAG 2.1

## 🔧 Maintainability
- Cobertura de tests > 80%
- Documentación completa
""",

        "context/requirements/business-rules.md": """# Reglas de Negocio

## 📋 Reglas Generales
1. [Regla 1]
2. [Regla 2]

## 💼 Validaciones
- [Validación 1]
- [Validación 2]

## 🚫 Restricciones
- [Restricción 1]
- [Restricción 2]
""",

        "context/constraints.md": """# Limitaciones y Restricciones

## 💰 Budget Constraints
[Limitaciones de presupuesto]

## ⏰ Time Constraints
[Limitaciones de tiempo]

## 🔧 Technical Constraints
[Limitaciones técnicas]

## 📋 Regulatory Constraints
[Limitaciones regulatorias]
""",

        "context/glossary.md": """# Glosario del Proyecto

## Términos Técnicos
- **API**: Application Programming Interface
- **SPA**: Single Page Application

## Términos del Negocio
- **Usuario**: Persona que usa la aplicación
- **Admin**: Administrador del sistema

## Acrónimos
- **MVP**: Minimum Viable Product
- **QA**: Quality Assurance
""",

        # Personal Office
        "personal-office/TODO.md": """# 🎯 PROJECT TODO - Dinámico

## 📊 PROGRESO GENERAL: 0% Completado

### ✅ COMPLETADO (0 tareas)
[Este agente detectará automáticamente las tareas completadas]

### 🔄 EN PROGRESO (0 tareas)
[Este agente detectará automáticamente las tareas en progreso]

### ⭕ PENDIENTE (0 tareas)
[Este agente detectará automáticamente las tareas pendientes]

### 🆕 NUEVAS TAREAS (Detectadas por agentes)
[Las nuevas tareas aparecerán aquí automáticamente]

---
*Última actualización: {timestamp}*
""".format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')),

        "personal-office/project-overview.md": """# 📊 Vista General del Proyecto

## 🎯 Estado Actual
**Progreso**: 0%
**Fase Actual**: Inicialización
**Próximos Hitos**: Por definir

## 👥 Equipo Asignado
[Agentes asignados aparecerán aquí]

## 🚨 Issues Críticos
Ninguno actualmente.

## 📈 Métricas Clave
- Tareas completadas: 0
- Bugs abiertos: 0
- Performance score: N/A

---
*Actualizado automáticamente por Personal Assistant*
""",

        "personal-office/assistants/personal-assistant-spec.md": """# Personal Executive Assistant

## 👤 INFORMACIÓN BÁSICA
**Nombre**: Personal_Executive_Assistant  
**Reporta a**: CEO (TU)  
**Departamento**: Personal Office  

## 🎯 RESPONSABILIDADES
- Monitorear actividad de todos los departamentos
- Generar reportes ejecutivos diarios
- Alertar sobre issues críticos
- Coordinar comunicación entre departamentos
- Gestionar agenda de revisiones del CEO

## 📊 KPIs
- Reportes diarios entregados: 100%
- Tiempo de respuesta a alertas: < 5 min
- Satisfacción del CEO: > 9/10

## 🔄 FLUJO DE TRABAJO
1. Revisar status de todos los departamentos
2. Identificar issues y bloqueadores
3. Generar reporte ejecutivo
4. Alertar sobre situaciones críticas
5. Coordinar reuniones necesarias
""",

        "personal-office/assistants/todo-manager-spec.md": """# Dynamic TODO Manager

## 👤 INFORMACIÓN BÁSICA
**Nombre**: Dynamic_TODO_Manager  
**Reporta a**: CEO (TU)  
**Departamento**: Personal Office  

## 🎯 RESPONSABILIDADES
- Escanear proyecto al inicializar
- Detectar tareas completadas existentes
- Mantener TODO.md actualizado dinámicamente
- Agregar nuevas tareas según decisiones de agentes
- Calcular porcentajes de progreso
- Organizar tareas por prioridad y dependencias

## 📊 KPIs
- Precisión en detección de tareas: > 95%
- Actualizaciones en tiempo real: < 1 min
- Organización clara del TODO: > 9/10

## 🔄 FLUJO DE TRABAJO
1. Escanear código y estructura del proyecto
2. Identificar funcionalidades implementadas
3. Marcar como completadas en TODO.md
4. Escuchar decisiones de otros agentes
5. Agregar nuevas tareas dinámicamente
6. Reorganizar y priorizar
7. Actualizar porcentajes de progreso
""",

        # Status files
        "status/blockers.md": """# Bloqueadores Activos

## 🚫 Bloqueadores Críticos
Ninguno actualmente.

## ⚠️ Bloqueadores Menores
Ninguno actualmente.

---
*Última actualización: {timestamp}*
""".format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')),

        "status/sprint-status.md": """# Estado del Sprint Actual

## 📅 Sprint Info
**Sprint**: No iniciado
**Inicio**: N/A
**Fin**: N/A

## 🎯 Objetivos del Sprint
[ ] Objetivo 1
[ ] Objetivo 2

## 📊 Progreso
**Completado**: 0%
**En progreso**: 0%
**Pendiente**: 100%

## 🚨 Riesgos Identificados
Ninguno actualmente.
""",

        "status/completed-tasks.md": """# Tareas Completadas

## ✅ Hoy ({timestamp})
Ninguna tarea completada aún.

## ✅ Esta Semana
Ninguna tarea completada aún.

## ✅ Este Mes
Ninguna tarea completada aún.

---
*Auto-actualizado por el sistema*
""".format(timestamp=datetime.now().strftime('%Y-%m-%d')),

        "status/health-check.md": """# Estado General del Sistema

## 🟢 Status: HEALTHY

## 📊 Métricas del Sistema
- **Agentes activos**: 0
- **Tareas en cola**: 0
- **Errores últimas 24h**: 0
- **Performance score**: N/A

## 🔧 Componentes
- [ ] Database: No configurada
- [ ] API: No configurada  
- [ ] Frontend: No configurado
- [ ] Tests: No configurados

## 📈 Tendencias
Sin datos históricos aún.

---
*Última verificación: {timestamp}*
""".format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')),

        # Tasks files
        "tasks/dependencies.md": """# Dependencias entre Tareas

## 🔗 Dependencias Críticas
Ninguna dependencia definida aún.

## 📋 Mapa de Dependencias
```
[Sin dependencias actualmente]
```

## 🚨 Bloqueadores por Dependencias
Ninguno actualmente.

---
*Actualizado automáticamente*
""",

        "tasks/backlog/high-priority.md": """# Backlog - Alta Prioridad

## 🔥 Tareas Críticas
[ ] Configuración inicial del proyecto
[ ] Definición de arquitectura
[ ] Setup de base de datos

## ⚠️ Tareas Importantes
[ ] Configuración de CI/CD
[ ] Setup de testing framework

---
*Prioridad: ALTA*
""",

        "tasks/backlog/medium-priority.md": """# Backlog - Prioridad Media

## 📋 Tareas Importantes
[ ] Configuración de linting
[ ] Setup de documentación
[ ] Configuración de monitoreo

---
*Prioridad: MEDIA*
""",

        "tasks/backlog/low-priority.md": """# Backlog - Prioridad Baja

## 📝 Tareas Nice-to-have
[ ] Optimización de build
[ ] Configuración avanzada de IDE

---
*Prioridad: BAJA*
""",

        # Channels
        "channels/management/decisions.md": """# Decisiones Ejecutivas

## 📋 Decisiones Pendientes
Ninguna decisión pendiente.

## ✅ Decisiones Tomadas
*Historial de decisiones aparecerá aquí*

---
*Canal: Management*
""",

        "channels/management/priorities.md": """# Prioridades Actuales

## 🔥 Prioridad 1
Configuración inicial del workspace

## 📋 Prioridad 2
Análisis del proyecto existente

## 📝 Prioridad 3
Definición de arquitectura

---
*Canal: Management*
""",

        # Standards
        "standards/coding-standards/javascript.md": """# Estándares de JavaScript

## 📋 Reglas Generales
- Usar ES6+ features
- Preferir arrow functions
- Usar const/let en lugar de var

## 🔧 Linting
- ESLint configurado
- Prettier para formateo

## 📝 Naming Conventions
- camelCase para variables y funciones
- PascalCase para componentes React
""",

        # Coordination
        "coordination/agent-assignments.md": """# Asignaciones de Agentes

## 👥 Agentes Activos
Ningún agente asignado actualmente.

## 📋 Asignaciones Pendientes
Las asignaciones aparecerán después del análisis del CEO.

---
*Última actualización: {timestamp}*
""".format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')),

        "coordination/communication-protocols.md": """# Protocolos de Comunicación

## 📢 Canales de Comunicación
- **Management**: Decisiones estratégicas
- **Frontend**: Comunicación frontend
- **Backend**: Comunicación backend
- **DevOps**: Deployment y operaciones
- **Integration**: Colaboración entre equipos

## 🔄 Flujo de Comunicación
1. Agente identifica necesidad de comunicar
2. Selecciona canal apropiado
3. Documenta en el canal correspondiente
4. Notifica a agentes relevantes

## 🚨 Escalamiento
- Issues críticos → Management channel
- Conflictos técnicos → Integration channel
""",

        # Alerts
        "alerts/critical-issues.md": """# Issues Críticos

## 🚨 Issues Activos
Ningún issue crítico actualmente.

## ✅ Issues Resueltos
*Historial de issues resueltos*

---
*Monitoreo automático activo*
""",

        # Department info files
        "departments/command-center/department-info.md": """# Centro de Comando

**Propósito**: Liderazgo estratégico y toma de decisiones

**Prioridad**: CRÍTICA

**Roles Requeridos**:
- director-enterprise-ceo
- master-orchestrator  
- solution-architect-ai

## 🎯 Responsabilidades
- Análisis estratégico del proyecto
- Toma de decisiones de alto nivel
- Coordinación general del equipo
- Definición de arquitectura global

## 📊 KPIs
- Decisiones tomadas en tiempo: > 95%
- Satisfacción del equipo: > 8/10
- Cumplimiento de deadlines: > 90%
""",

        "departments/core-architecture/department-info.md": """# Arquitectura Core

**Propósito**: Diseño y arquitectura de sistemas

**Prioridad**: CRÍTICA

**Roles Requeridos**:
- system-architect-ai
- database-architect-ai
- api-architect-ai
- cloud-architect-ai

## 🎯 Responsabilidades
- Diseño de arquitectura de sistemas
- Definición de patrones de datos
- Especificación de APIs
- Arquitectura de infraestructura cloud

## 📊 KPIs
- Documentación de arquitectura: 100%
- Revisión de designs: < 48h
- Compliance con estándares: > 95%
""",

        "departments/development-engines/department-info.md": """# Motores de Desarrollo

**Propósito**: Desarrollo principal frontend/backend

**Prioridad**: CRÍTICA

**Roles Requeridos**:
- react-specialist-ai
- backend-framework-ai
- performance-optimization-ai
- security-backend-ai

## 🎯 Responsabilidades
- Desarrollo de componentes frontend
- Implementación de APIs backend
- Optimización de performance
- Implementación de seguridad

## 📊 KPIs
- Velocidad de desarrollo: > 80% planned
- Code quality score: > 8/10
- Bug rate: < 2% of features
""",

        "departments/specialized-domains/department-info.md": """# Dominios Especializados

**Propósito**: Funcionalidades específicas del negocio

**Prioridad**: ALTA

**Roles Requeridos**:
- payment-systems-ai
- machine-learning-ai
- real-time-analytics-ai
- pwa-specialist-ai

## 🎯 Responsabilidades
- Implementación de sistemas de pago
- Desarrollo de funcionalidades ML/AI
- Analytics en tiempo real
- Experiencia mobile/PWA

## 📊 KPIs
- Integración exitosa: > 95%
- Performance de features: > 90%
- User satisfaction: > 8/10
""",

        "departments/quality-operations/department-info.md": """# Calidad y Operaciones

**Propósito**: Testing, deployment y monitoreo

**Prioridad**: ALTA

**Roles Requeridos**:
- e2e-testing-ai
- devops-integration-ai
- monitoring-ai
- cybersecurity-ai

## 🎯 Responsabilidades
- Testing end-to-end
- CI/CD y deployment
- Monitoreo de sistemas
- Seguridad y compliance

## 📊 KPIs
- Test coverage: > 85%
- Deployment success: > 98%
- Uptime: > 99.5%
- Security vulnerabilities: 0 critical
""",

        "departments/automation-utilities/department-info.md": """# Automatización

**Propósito**: Herramientas y procesos automáticos

**Prioridad**: MEDIA

**Roles Requeridos**:
- task-distribution
- progress-tracker-ai
- workflow-manager

## 🎯 Responsabilidades
- Distribución automática de tareas
- Seguimiento de progreso
- Gestión de workflows

## 📊 KPIs
- Automatización de tareas: > 70%
- Eficiencia de workflows: > 85%
- Reducción de overhead: > 30%
"""
    }
    
    # Crear todos los archivos
    for file_path, content in files_content.items():
        full_path = workspace_root / file_path
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  📄 {file_path}")
    
    print(f"\n📄 Creados {len(files_content)} archivos base")

if __name__ == "__main__":
    print("🚀 Iniciando creación del workspace...")
    print("=" * 50)
    
    # Verificar que estamos en un directorio válido
    if not Path(".").is_dir():
        print("❌ Error: No se puede acceder al directorio actual")
        exit(1)
    
    # Crear estructura
    create_workspace_structure()
    
    print("\n" + "=" * 50)
    print("✅ ¡Workspace creado exitosamente!")
    print(f"📁 Ubicación: {Path.cwd() / '.workspace'}")
    print("\n📋 Próximos pasos:")
    print("1. Ejecutar CEO analyzer para analizar el proyecto")
    print("2. Revisar recomendaciones de agentes")
    print("3. Configurar tus 2 asistentes personales")
    print("4. Empezar a desarrollar con el equipo de agentes")