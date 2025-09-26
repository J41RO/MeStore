#!/usr/bin/env python3
"""
🤖 SISTEMA DE DELEGACIÓN AUTOMÁTICA MEJORADO
Activa automáticamente al agente responsable y transfiere instrucciones completas
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

# Archivos protegidos con agentes responsables
PROTECTED_FILES = {
    "app/main.py": "system-architect-ai",
    "frontend/vite.config.ts": "frontend-performance-ai",
    "docker-compose.yml": "cloud-infrastructure-ai",
    "app/api/v1/deps/auth.py": "security-backend-ai",
    "app/services/auth_service.py": "security-backend-ai",
    "app/models/user.py": "database-architect-ai",
    "tests/conftest.py": "tdd-specialist",
    "app/core/config.py": "configuration-management",
    "app/database.py": "database-architect-ai",
    "app/core/security.py": "security-backend-ai",
    "app/models/order.py": "database-architect-ai",
    "frontend/src/contexts/AuthContext.tsx": "security-frontend-ai",
    "frontend/src/services/authService.ts": "security-frontend-ai"
}

# Agentes backup para escalación
BACKUP_AGENTS = {
    "system-architect-ai": "solution-architect-ai",
    "frontend-performance-ai": "react-specialist-ai",
    "cloud-infrastructure-ai": "devops-integration-ai",
    "security-backend-ai": "api-security",
    "database-architect-ai": "backend-framework-ai",
    "tdd-specialist": "unit-testing-ai",
    "configuration-management": "system-architect-ai",
    "security-frontend-ai": "frontend-security-ai"
}

class AutoDelegationSystem:
    def __init__(self):
        self.requests_dir = ".workspace/requests"
        self.logs_dir = ".workspace/logs"
        self.ensure_directories()

    def ensure_directories(self):
        """Crear directorios necesarios"""
        os.makedirs(self.requests_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)

    def detect_protected_file_access(self, current_agent, target_file, user_instruction):
        """
        Detectar cuando un agente intenta modificar archivo protegido
        y activar automáticamente delegación
        """
        print(f"🔍 Detectando acceso protegido: {current_agent} → {target_file}")

        # Verificar si archivo está protegido
        if target_file not in PROTECTED_FILES:
            return {"status": "allowed", "message": "Archivo no protegido, proceder"}

        responsible_agent = PROTECTED_FILES[target_file]

        # Si es el agente responsable o master-orchestrator, permitir
        if current_agent == responsible_agent or current_agent == "master-orchestrator":
            return {"status": "allowed", "message": f"Agente autorizado: {current_agent}"}

        # Activar delegación automática
        return self.auto_delegate_to_responsible_agent(
            current_agent, responsible_agent, target_file, user_instruction
        )

    def auto_delegate_to_responsible_agent(self, requesting_agent, responsible_agent, target_file, user_instruction):
        """
        Activar automáticamente al agente responsable con instrucciones completas
        """
        print(f"🚀 ACTIVANDO DELEGACIÓN AUTOMÁTICA")
        print(f"📤 De: {requesting_agent}")
        print(f"📥 Para: {responsible_agent}")
        print(f"📁 Archivo: {target_file}")

        # Crear request único
        request_id = self.generate_request_id()

        # Crear solicitud completa con toda la información
        delegation_request = {
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "requesting_agent": requesting_agent,
            "responsible_agent": responsible_agent,
            "backup_agent": BACKUP_AGENTS.get(responsible_agent, "master-orchestrator"),
            "target_file": target_file,
            "user_instruction": user_instruction,
            "status": "DELEGATED",
            "priority": self.calculate_priority(target_file),
            "escalation_timeout": (datetime.now() + timedelta(minutes=15)).isoformat(),
            "delegation_chain": [requesting_agent, responsible_agent],
            "auto_activation": True
        }

        # Guardar solicitud
        request_file = f"{self.requests_dir}/delegation_{request_id}.json"
        with open(request_file, 'w') as f:
            json.dump(delegation_request, f, indent=2)

        # Log de delegación
        self.log_delegation_activity(delegation_request)

        # Activar automáticamente al agente responsable
        activation_result = self.activate_responsible_agent(delegation_request)

        return {
            "status": "DELEGATED",
            "request_id": request_id,
            "responsible_agent": responsible_agent,
            "message": f"Delegación automática iniciada. Agente {responsible_agent} activado.",
            "activation_result": activation_result,
            "estimated_response_time": "5-15 minutos",
            "backup_escalation": f"Escalará a {BACKUP_AGENTS.get(responsible_agent, 'master-orchestrator')} si no responde"
        }

    def activate_responsible_agent(self, delegation_request):
        """
        Activar automáticamente al agente responsable usando el Task tool
        """
        responsible_agent = delegation_request["responsible_agent"]
        target_file = delegation_request["target_file"]
        user_instruction = delegation_request["user_instruction"]
        request_id = delegation_request["request_id"]

        print(f"⚡ ACTIVANDO AGENTE: {responsible_agent}")

        # Crear instrucción completa para el agente responsable
        enhanced_instruction = self.create_enhanced_instruction(
            delegation_request["requesting_agent"],
            responsible_agent,
            target_file,
            user_instruction,
            request_id
        )

        # Crear archivo de activación para el agente responsable
        activation_file = f"{self.requests_dir}/activation_{responsible_agent}_{request_id}.md"

        activation_content = f"""# 🚨 ACTIVACIÓN AUTOMÁTICA DE AGENTE RESPONSABLE

## 📋 INFORMACIÓN DE DELEGACIÓN
- **Request ID**: {request_id}
- **Timestamp**: {delegation_request["timestamp"]}
- **Agente solicitante**: {delegation_request["requesting_agent"]}
- **Agente responsable**: {responsible_agent}
- **Archivo objetivo**: {target_file}
- **Prioridad**: {delegation_request["priority"]}

## 🎯 INSTRUCCIONES ORIGINALES DEL USUARIO
{user_instruction}

## 🤖 INSTRUCCIONES MEJORADAS PARA EL AGENTE
{enhanced_instruction}

## 🔍 EVALUACIÓN REQUERIDA
Como {responsible_agent}, debes evaluar:

1. **Seguridad**: ¿Es seguro modificar {target_file}?
2. **Impacto**: ¿Qué sistemas se verán afectados?
3. **Alternativas**: ¿Hay formas más seguras de lograr el objetivo?
4. **Riesgo**: ¿Cuál es el nivel de riesgo técnico?

## 🚦 DECISIONES POSIBLES

### ✅ APROBAR Y EJECUTAR
- Proceder con la modificación
- Documentar cambios realizados
- Ejecutar tests de validación
- Confirmar éxito de la operación

### ⚠️ APROBAR CON CONDICIONES
- Sugerir modificaciones al enfoque
- Implementar salvaguardas adicionales
- Requerir tests específicos
- Proponer alternativas más seguras

### ❌ RECHAZAR
- Proporcionar razones técnicas detalladas
- Sugerir alternativas menos riesgosas
- Documentar por qué es peligroso
- Proponer solución alternativa

## 📊 INFORMACIÓN ADICIONAL
- **Backup Agent**: {delegation_request["backup_agent"]}
- **Escalación automática**: 15 minutos
- **Status inicial**: DELEGATED
- **Auto-activation**: TRUE

---
**⏰ TIEMPO LÍMITE**: 15 minutos para evaluación
**🔄 ESCALACIÓN**: Automática a {delegation_request["backup_agent"]} si no respondes
**📝 LOG**: Toda la actividad se registra automáticamente
"""

        # Guardar archivo de activación
        with open(activation_file, 'w') as f:
            f.write(activation_content)

        print(f"📁 Archivo de activación creado: {activation_file}")

        # Marcar como activado
        delegation_request["activation_file"] = activation_file
        delegation_request["activation_time"] = datetime.now().isoformat()
        delegation_request["status"] = "AGENT_ACTIVATED"

        # Actualizar solicitud
        request_file = f"{self.requests_dir}/delegation_{request_id}.json"
        with open(request_file, 'w') as f:
            json.dump(delegation_request, f, indent=2)

        return {
            "status": "ACTIVATED",
            "agent": responsible_agent,
            "activation_file": activation_file,
            "enhanced_instruction": enhanced_instruction,
            "timeout": "15 minutos",
            "message": f"Agente {responsible_agent} activado con instrucciones completas"
        }

    def create_enhanced_instruction(self, requesting_agent, responsible_agent, target_file, original_instruction, request_id):
        """
        Crear instrucción mejorada con contexto completo para el agente responsable
        """
        context_info = self.get_file_context(target_file)

        enhanced = f"""
🤖 DELEGACIÓN AUTOMÁTICA DE {requesting_agent}

OBJETIVO ORIGINAL: {original_instruction}

CONTEXTO DEL ARCHIVO:
- Archivo: {target_file}
- Responsable: {responsible_agent}
- Nivel de protección: CRÍTICO
{context_info}

INSTRUCCIONES ESPECÍFICAS:
1. EVALUAR la seguridad de la modificación solicitada
2. VERIFICAR que no rompa funcionalidad existente
3. CONSIDERAR alternativas más seguras si las hay
4. IMPLEMENTAR la solución si es segura
5. DOCUMENTAR todos los cambios realizados
6. EJECUTAR tests para validar que todo funciona
7. REPORTAR el resultado (éxito/fallo/alternativa)

CRITERIOS DE EVALUACIÓN:
- ¿Rompe la funcionalidad existente?
- ¿Introduce vulnerabilidades de seguridad?
- ¿Afecta otros sistemas o servicios?
- ¿Hay una forma más segura de lograr el objetivo?

ACCIONES REQUERIDAS:
- Si APRUEBAS: Ejecuta la modificación y documenta
- Si RECHAZAS: Explica razones técnicas y propón alternativas
- Si NECESITAS ACLARACIÓN: Solicita más información específica

Request ID: {request_id}
Tiempo límite: 15 minutos
"""
        return enhanced

    def get_file_context(self, target_file):
        """Obtener contexto específico del archivo"""
        contexts = {
            "app/main.py": "- Puerto 8000 FastAPI server\n- NO cambiar configuración de puertos\n- Crítico para toda la aplicación",
            "app/api/v1/deps/auth.py": "- Sistema JWT authentication\n- NO romper login existente\n- Afecta todos los endpoints protegidos",
            "app/models/user.py": "- Modelo crítico usuarios\n- NO crear usuarios duplicados en tests\n- Cambios afectan toda autenticación",
            "docker-compose.yml": "- Orquestación completa servicios\n- Puertos: backend:8000, frontend:5173\n- NO cambiar configuración de red",
            "tests/conftest.py": "- Fixtures centrales de testing\n- NO modificar fixtures existentes\n- Usado por todo el sistema de tests"
        }
        return contexts.get(target_file, "- Archivo protegido nivel crítico\n- Requiere evaluación cuidadosa")

    def calculate_priority(self, target_file):
        """Calcular prioridad basada en criticidad del archivo"""
        critical_files = ["app/main.py", "docker-compose.yml", "app/api/v1/deps/auth.py"]
        if target_file in critical_files:
            return "CRÍTICA"
        return "ALTA"

    def generate_request_id(self):
        """Generar ID único para la solicitud"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"REQ_{timestamp}_{hash(time.time()) % 10000:04d}"

    def log_delegation_activity(self, delegation_request):
        """Registrar actividad de delegación"""
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = f"{self.logs_dir}/auto_delegation_{today}.json"

        # Leer log existente
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []

        # Agregar nueva entrada
        log_entry = {
            "timestamp": delegation_request["timestamp"],
            "request_id": delegation_request["request_id"],
            "event": "AUTO_DELEGATION_INITIATED",
            "requesting_agent": delegation_request["requesting_agent"],
            "responsible_agent": delegation_request["responsible_agent"],
            "target_file": delegation_request["target_file"],
            "status": delegation_request["status"]
        }

        logs.append(log_entry)

        # Guardar log actualizado
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)

        print(f"📝 Delegación registrada en: {log_file}")

    def check_delegation_status(self, request_id):
        """Verificar estado de una delegación"""
        request_file = f"{self.requests_dir}/delegation_{request_id}.json"

        if not os.path.exists(request_file):
            return {"error": f"Request {request_id} no encontrado"}

        with open(request_file, 'r') as f:
            delegation = json.load(f)

        # Verificar si necesita escalación
        escalation_time = datetime.fromisoformat(delegation["escalation_timeout"])
        if datetime.now() > escalation_time and delegation["status"] == "AGENT_ACTIVATED":
            return self.escalate_to_backup(delegation)

        return delegation

    def escalate_to_backup(self, delegation_request):
        """Escalar automáticamente al agente backup"""
        backup_agent = delegation_request["backup_agent"]

        print(f"🚨 ESCALANDO A BACKUP AGENT: {backup_agent}")

        delegation_request["status"] = "ESCALATED_TO_BACKUP"
        delegation_request["escalation_time"] = datetime.now().isoformat()
        delegation_request["escalation_reason"] = "Timeout - no response from primary agent"
        delegation_request["delegation_chain"].append(backup_agent)

        # Crear nueva activación para backup
        backup_activation = self.activate_responsible_agent({
            **delegation_request,
            "responsible_agent": backup_agent
        })

        # Actualizar request
        request_file = f"{self.requests_dir}/delegation_{delegation_request['request_id']}.json"
        with open(request_file, 'w') as f:
            json.dump(delegation_request, f, indent=2)

        return {
            "status": "ESCALATED",
            "backup_agent": backup_agent,
            "escalation_reason": "Primary agent timeout",
            "new_timeout": "10 minutos adicionales"
        }


def main():
    """Función principal para uso directo del script"""
    if len(sys.argv) < 4:
        print("❌ Uso: python auto_delegate_to_responsible_agent.py <current_agent> <target_file> '<user_instruction>'")
        print("🔧 Ejemplo: python auto_delegate_to_responsible_agent.py backend-framework-ai app/main.py 'Agregar endpoint de salud'")
        sys.exit(1)

    current_agent = sys.argv[1]
    target_file = sys.argv[2]
    user_instruction = sys.argv[3]

    # Inicializar sistema de delegación
    delegation_system = AutoDelegationSystem()

    print(f"🤖 SISTEMA DE DELEGACIÓN AUTOMÁTICA ACTIVADO")
    print(f"📤 Agente actual: {current_agent}")
    print(f"📁 Archivo objetivo: {target_file}")
    print(f"📋 Instrucción: {user_instruction}")
    print("-" * 70)

    # Detectar y procesar acceso a archivo protegido
    result = delegation_system.detect_protected_file_access(
        current_agent, target_file, user_instruction
    )

    if result["status"] == "allowed":
        print(f"✅ {result['message']}")
        print("🚀 PUEDE PROCEDER con la modificación")

    elif result["status"] == "DELEGATED":
        print(f"🔄 DELEGACIÓN AUTOMÁTICA ACTIVADA")
        print(f"📋 Request ID: {result['request_id']}")
        print(f"🤖 Agente responsable: {result['responsible_agent']}")
        print(f"⏰ Tiempo estimado: {result['estimated_response_time']}")
        print(f"🔄 Backup: {result['backup_escalation']}")
        print("")
        print("🎯 EL AGENTE RESPONSABLE HA SIDO ACTIVADO AUTOMÁTICAMENTE")
        print("📨 Las instrucciones completas han sido transferidas")
        print("⌛ Esperando evaluación y decisión del agente especializado...")

        # Mostrar información de seguimiento
        print(f"\n📊 SEGUIMIENTO:")
        print(f"🔍 Check status: python .workspace/scripts/check_delegation_status.py {result['request_id']}")
        print(f"📂 Activación: {result['activation_result']['activation_file']}")

if __name__ == "__main__":
    main()