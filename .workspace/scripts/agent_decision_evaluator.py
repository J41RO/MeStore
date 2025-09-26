#!/usr/bin/env python3
"""
🧠 EVALUADOR DE DECISIONES PARA AGENTES RESPONSABLES
Sistema que ayuda a los agentes a evaluar modificaciones de archivos protegidos
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

class AgentDecisionEvaluator:
    def __init__(self):
        self.requests_dir = ".workspace/requests"
        self.decisions_dir = ".workspace/decisions"
        self.risk_rules = self.load_risk_evaluation_rules()
        self.ensure_directories()

    def ensure_directories(self):
        """Crear directorios necesarios"""
        os.makedirs(self.decisions_dir, exist_ok=True)
        os.makedirs(self.requests_dir, exist_ok=True)

    def load_risk_evaluation_rules(self):
        """Cargar reglas de evaluación de riesgo por archivo"""
        return {
            "app/main.py": {
                "risk_level": "CRÍTICO",
                "forbidden_changes": [
                    "cambiar puerto 8000",
                    "modificar configuración uvicorn",
                    "alterar imports críticos",
                    "cambiar configuración CORS"
                ],
                "safe_changes": [
                    "agregar nuevos endpoints",
                    "agregar middleware opcional",
                    "agregar logging adicional",
                    "agregar documentación"
                ],
                "required_tests": [
                    "servidor inicia correctamente",
                    "endpoints existentes responden",
                    "CORS funciona",
                    "tests de integración pasan"
                ]
            },
            "app/api/v1/deps/auth.py": {
                "risk_level": "CRÍTICO",
                "forbidden_changes": [
                    "modificar validación JWT",
                    "cambiar estructura de tokens",
                    "alterar verificación de roles",
                    "remover validaciones existentes"
                ],
                "safe_changes": [
                    "agregar validaciones adicionales",
                    "mejorar mensajes de error",
                    "agregar logging de seguridad",
                    "optimizar performance sin cambiar lógica"
                ],
                "required_tests": [
                    "login funciona correctamente",
                    "tokens JWT son válidos",
                    "autorización por roles funciona",
                    "tests de seguridad pasan"
                ]
            },
            "app/models/user.py": {
                "risk_level": "CRÍTICO",
                "forbidden_changes": [
                    "cambiar campos existentes",
                    "modificar relaciones de base de datos",
                    "alterar validaciones críticas",
                    "crear usuarios duplicados en tests"
                ],
                "safe_changes": [
                    "agregar campos opcionales nuevos",
                    "agregar métodos de utilidad",
                    "mejorar validaciones existentes",
                    "optimizar queries"
                ],
                "required_tests": [
                    "migraciones se ejecutan correctamente",
                    "no hay usuarios duplicados",
                    "relaciones funcionan",
                    "validaciones son efectivas"
                ]
            },
            "docker-compose.yml": {
                "risk_level": "CRÍTICO",
                "forbidden_changes": [
                    "cambiar puertos expuestos",
                    "modificar redes Docker",
                    "alterar variables de entorno críticas",
                    "cambiar configuración de volúmenes"
                ],
                "safe_changes": [
                    "agregar servicios opcionales",
                    "ajustar recursos (memoria, CPU)",
                    "agregar variables de entorno no críticas",
                    "mejorar etiquetas y metadatos"
                ],
                "required_tests": [
                    "todos los servicios inician correctamente",
                    "red Docker funciona",
                    "backend accesible en puerto 8000",
                    "frontend accesible en puerto 5173"
                ]
            },
            "tests/conftest.py": {
                "risk_level": "ALTO",
                "forbidden_changes": [
                    "modificar fixtures existentes",
                    "cambiar configuración de base de datos",
                    "alterar setup de testing",
                    "crear usuarios duplicados"
                ],
                "safe_changes": [
                    "agregar nuevas fixtures",
                    "mejorar aislamiento de tests",
                    "optimizar setup/teardown",
                    "agregar utilidades de testing"
                ],
                "required_tests": [
                    "todos los tests existentes pasan",
                    "fixtures se crean/limpian correctamente",
                    "no hay interferencia entre tests",
                    "base de datos se resetea correctamente"
                ]
            }
        }

    def evaluate_modification_request(self, request_id):
        """Evaluar una solicitud de modificación específica"""
        request_file = f"{self.requests_dir}/delegation_{request_id}.json"

        if not os.path.exists(request_file):
            return {"error": f"Request {request_id} no encontrado"}

        with open(request_file, 'r') as f:
            delegation_request = json.load(f)

        target_file = delegation_request["target_file"]
        user_instruction = delegation_request["user_instruction"]
        responsible_agent = delegation_request["responsible_agent"]

        # Realizar evaluación de riesgo
        risk_evaluation = self.perform_risk_analysis(target_file, user_instruction)

        # Generar recomendación
        recommendation = self.generate_recommendation(
            target_file, user_instruction, risk_evaluation, responsible_agent
        )

        # Crear documento de evaluación
        evaluation = {
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "evaluator": "agent_decision_evaluator",
            "target_file": target_file,
            "user_instruction": user_instruction,
            "responsible_agent": responsible_agent,
            "risk_evaluation": risk_evaluation,
            "recommendation": recommendation,
            "evaluation_summary": self.create_evaluation_summary(risk_evaluation, recommendation)
        }

        # Guardar evaluación
        evaluation_file = f"{self.decisions_dir}/evaluation_{request_id}.json"
        with open(evaluation_file, 'w') as f:
            json.dump(evaluation, f, indent=2)

        return evaluation

    def perform_risk_analysis(self, target_file, user_instruction):
        """Realizar análisis de riesgo de la modificación"""
        file_rules = self.risk_rules.get(target_file, {
            "risk_level": "MEDIO",
            "forbidden_changes": [],
            "safe_changes": [],
            "required_tests": []
        })

        instruction_lower = user_instruction.lower()

        # Verificar cambios prohibidos
        forbidden_matches = []
        for forbidden in file_rules.get("forbidden_changes", []):
            if any(word in instruction_lower for word in forbidden.lower().split()):
                forbidden_matches.append(forbidden)

        # Verificar cambios seguros
        safe_matches = []
        for safe in file_rules.get("safe_changes", []):
            if any(word in instruction_lower for word in safe.lower().split()):
                safe_matches.append(safe)

        # Calcular score de riesgo
        risk_score = self.calculate_risk_score(
            file_rules["risk_level"],
            len(forbidden_matches),
            len(safe_matches),
            instruction_lower
        )

        return {
            "file_risk_level": file_rules["risk_level"],
            "forbidden_matches": forbidden_matches,
            "safe_matches": safe_matches,
            "risk_score": risk_score,
            "risk_factors": self.identify_risk_factors(instruction_lower),
            "required_tests": file_rules.get("required_tests", [])
        }

    def calculate_risk_score(self, base_risk, forbidden_count, safe_count, instruction):
        """Calcular score numérico de riesgo (0-100)"""
        base_scores = {"BAJO": 20, "MEDIO": 40, "ALTO": 60, "CRÍTICO": 80}
        score = base_scores.get(base_risk, 40)

        # Penalizar cambios prohibidos
        score += forbidden_count * 20

        # Premiar cambios seguros identificados
        score -= safe_count * 5

        # Factores adicionales de riesgo
        risk_keywords = [
            ("eliminar", 15), ("borrar", 15), ("quitar", 10),
            ("cambiar", 10), ("modificar", 5), ("alterar", 10),
            ("reemplazar", 15), ("override", 20), ("forzar", 25)
        ]

        for keyword, penalty in risk_keywords:
            if keyword in instruction:
                score += penalty

        # Factores que reducen riesgo
        safe_keywords = [
            ("agregar", -5), ("añadir", -5), ("crear nuevo", -5),
            ("mejorar", -3), ("optimizar", -3), ("documentar", -5)
        ]

        for keyword, bonus in safe_keywords:
            if keyword in instruction:
                score += bonus

        return max(0, min(100, score))

    def identify_risk_factors(self, instruction):
        """Identificar factores específicos de riesgo"""
        factors = []

        risk_patterns = {
            "configuración crítica": ["puerto", "host", "cors", "ssl", "https"],
            "autenticación": ["jwt", "token", "auth", "login", "password", "hash"],
            "base de datos": ["modelo", "migración", "campo", "tabla", "relación"],
            "servicios externos": ["api", "servicio", "webhook", "integración"],
            "testing": ["test", "fixture", "mock", "usuario de prueba"],
            "infraestructura": ["docker", "compose", "container", "red", "volumen"]
        }

        for category, keywords in risk_patterns.items():
            if any(keyword in instruction for keyword in keywords):
                factors.append(category)

        return factors

    def generate_recommendation(self, target_file, instruction, risk_evaluation, agent):
        """Generar recomendación basada en evaluación"""
        risk_score = risk_evaluation["risk_score"]
        forbidden_matches = risk_evaluation["forbidden_matches"]

        if forbidden_matches:
            return {
                "decision": "RECHAZAR",
                "confidence": "ALTA",
                "reason": f"Modificación incluye cambios prohibidos: {', '.join(forbidden_matches)}",
                "alternative_approach": self.suggest_alternative_approach(target_file, instruction),
                "required_consultation": "Consultar con master-orchestrator si es absolutamente necesario"
            }

        elif risk_score >= 80:
            return {
                "decision": "RECHAZAR",
                "confidence": "ALTA",
                "reason": "Riesgo excesivamente alto para la aplicación",
                "alternative_approach": self.suggest_alternative_approach(target_file, instruction),
                "required_consultation": "Buscar enfoque alternativo más seguro"
            }

        elif risk_score >= 60:
            return {
                "decision": "APROBAR_CON_CONDICIONES",
                "confidence": "MEDIA",
                "reason": "Riesgo alto pero manejable con precauciones",
                "conditions": self.generate_safety_conditions(target_file, risk_evaluation),
                "required_tests": risk_evaluation["required_tests"]
            }

        elif risk_score >= 40:
            return {
                "decision": "APROBAR",
                "confidence": "MEDIA",
                "reason": "Riesgo moderado, proceder con tests de validación",
                "required_tests": risk_evaluation["required_tests"],
                "monitoring": "Monitorear impacto después de implementar"
            }

        else:
            return {
                "decision": "APROBAR",
                "confidence": "ALTA",
                "reason": "Riesgo bajo, modificación segura",
                "required_tests": ["tests básicos de funcionalidad"],
                "fast_track": True
            }

    def suggest_alternative_approach(self, target_file, instruction):
        """Sugerir enfoques alternativos más seguros"""
        alternatives = {
            "app/main.py": "Considerar crear un nuevo endpoint en lugar de modificar configuración principal",
            "app/api/v1/deps/auth.py": "Crear nuevas funciones de validación sin modificar las existentes",
            "app/models/user.py": "Agregar nuevo modelo relacionado en lugar de modificar User directamente",
            "docker-compose.yml": "Usar docker-compose.override.yml para cambios locales",
            "tests/conftest.py": "Crear fixtures específicas en archivos separados"
        }

        return alternatives.get(target_file, "Buscar enfoque que agregue funcionalidad sin modificar código existente")

    def generate_safety_conditions(self, target_file, risk_evaluation):
        """Generar condiciones de seguridad específicas"""
        conditions = [
            "Crear backup completo antes de modificar",
            "Implementar en branch separado primero",
            "Ejecutar suite completa de tests",
            "Validar en entorno de desarrollo local"
        ]

        if risk_evaluation["file_risk_level"] == "CRÍTICO":
            conditions.extend([
                "Revisión de código obligatoria",
                "Testing en entorno staging",
                "Plan de rollback preparado"
            ])

        return conditions

    def create_evaluation_summary(self, risk_evaluation, recommendation):
        """Crear resumen ejecutivo de la evaluación"""
        return f"""
EVALUACIÓN AUTOMÁTICA COMPLETADA

🎯 DECISIÓN RECOMENDADA: {recommendation['decision']}
📊 SCORE DE RIESGO: {risk_evaluation['risk_score']}/100
🔍 NIVEL BASE: {risk_evaluation['file_risk_level']}
✅ CONFIANZA: {recommendation['confidence']}

FACTORES CLAVE:
{'🚫 Cambios prohibidos detectados' if risk_evaluation['forbidden_matches'] else '✅ No hay cambios prohibidos'}
{'✅ Patrones seguros identificados' if risk_evaluation['safe_matches'] else '⚠️ No se identificaron patrones seguros'}

RAZÓN: {recommendation['reason']}
"""

    def create_decision_report_for_agent(self, request_id, agent_name):
        """Crear reporte de decisión personalizado para el agente responsable"""
        evaluation = self.evaluate_modification_request(request_id)

        if "error" in evaluation:
            return evaluation

        # Crear reporte específico para el agente
        report_content = f"""# 🤖 REPORTE DE EVALUACIÓN AUTOMÁTICA

## 📋 INFORMACIÓN GENERAL
- **Request ID**: {request_id}
- **Agente Responsable**: {agent_name}
- **Archivo**: {evaluation['target_file']}
- **Timestamp**: {evaluation['timestamp']}

## 🎯 INSTRUCCIÓN ORIGINAL
{evaluation['user_instruction']}

## 📊 ANÁLISIS DE RIESGO AUTOMÁTICO
{evaluation['evaluation_summary']}

## 🔍 DETALLES DE LA EVALUACIÓN

### Factores de Riesgo Identificados:
{chr(10).join(f'- {factor}' for factor in evaluation['risk_evaluation']['risk_factors'])}

### Cambios Prohibidos Detectados:
{chr(10).join(f'❌ {match}' for match in evaluation['risk_evaluation']['forbidden_matches']) if evaluation['risk_evaluation']['forbidden_matches'] else '✅ Ninguno detectado'}

### Patrones Seguros Identificados:
{chr(10).join(f'✅ {match}' for match in evaluation['risk_evaluation']['safe_matches']) if evaluation['risk_evaluation']['safe_matches'] else '⚠️ Ninguno identificado'}

## 🚦 RECOMENDACIÓN DEL SISTEMA

**DECISIÓN SUGERIDA**: {evaluation['recommendation']['decision']}
**RAZÓN**: {evaluation['recommendation']['reason']}

"""

        if evaluation['recommendation']['decision'] == "APROBAR":
            report_content += f"""
## ✅ AUTORIZACIÓN SUGERIDA

Como {agent_name}, puedes proceder con esta modificación siguiendo estos pasos:

1. **Implementar la modificación** de forma cuidadosa
2. **Ejecutar tests requeridos**:
{chr(10).join(f'   - {test}' for test in evaluation['recommendation'].get('required_tests', []))}
3. **Validar que todo funciona correctamente**
4. **Documentar los cambios realizados**

"""

        elif evaluation['recommendation']['decision'] == "APROBAR_CON_CONDICIONES":
            report_content += f"""
## ⚠️ AUTORIZACIÓN CONDICIONAL

Como {agent_name}, puedes proceder SOLO si cumples estas condiciones:

### Condiciones Obligatorias:
{chr(10).join(f'- {condition}' for condition in evaluation['recommendation'].get('conditions', []))}

### Tests Requeridos:
{chr(10).join(f'- {test}' for test in evaluation['recommendation'].get('required_tests', []))}

"""

        else:  # RECHAZAR
            report_content += f"""
## ❌ NO PROCEDER CON LA MODIFICACIÓN

Como {agent_name}, NO debes proceder con esta modificación por las siguientes razones:

**MOTIVO PRINCIPAL**: {evaluation['recommendation']['reason']}

### Alternativa Sugerida:
{evaluation['recommendation'].get('alternative_approach', 'Consultar con master-orchestrator para encontrar enfoque alternativo')}

### Próximos Pasos:
1. Informar al usuario sobre el rechazo y la razón
2. Proponer la alternativa sugerida
3. {evaluation['recommendation'].get('required_consultation', 'Consultar con supervisores si es absolutamente necesario')}

"""

        report_content += f"""
---
**⚡ Este reporte fue generado automáticamente**
**🕒 Timestamp**: {datetime.now().isoformat()}
**🤖 Evaluador**: Agent Decision Evaluator v1.0
**📊 Confianza**: {evaluation['recommendation']['confidence']}
"""

        # Guardar reporte específico para el agente
        report_file = f"{self.decisions_dir}/agent_report_{agent_name}_{request_id}.md"
        with open(report_file, 'w') as f:
            f.write(report_content)

        return {
            "evaluation": evaluation,
            "report_file": report_file,
            "report_content": report_content
        }

def main():
    """Función principal del evaluador"""
    if len(sys.argv) < 3:
        print("❌ Uso: python agent_decision_evaluator.py <agent_name> <request_id>")
        print("🔧 Ejemplo: python agent_decision_evaluator.py system-architect-ai REQ_20250926_143022_1234")
        sys.exit(1)

    agent_name = sys.argv[1]
    request_id = sys.argv[2]

    evaluator = AgentDecisionEvaluator()

    print(f"🧠 EVALUADOR DE DECISIONES ACTIVADO")
    print(f"🤖 Agente: {agent_name}")
    print(f"📋 Request ID: {request_id}")
    print("-" * 60)

    # Crear reporte de evaluación
    result = evaluator.create_decision_report_for_agent(request_id, agent_name)

    if "error" in result:
        print(f"❌ {result['error']}")
        return

    print("✅ EVALUACIÓN COMPLETADA")
    print(f"📊 Decisión recomendada: {result['evaluation']['recommendation']['decision']}")
    print(f"📁 Reporte generado: {result['report_file']}")
    print("")
    print("🎯 RESUMEN EJECUTIVO:")
    print(result['evaluation']['evaluation_summary'])

if __name__ == "__main__":
    main()