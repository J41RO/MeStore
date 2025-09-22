#!/usr/bin/env python3
"""
📢 DISTRIBUIDOR DE INSTRUCCIONES A AGENTES
Script para copiar guías e instrucciones a todas las oficinas de agentes
"""

import os
import shutil
from pathlib import Path

def find_agent_offices():
    """Encontrar todas las oficinas de agentes"""
    offices = []
    departments_path = Path(".workspace/departments")

    if not departments_path.exists():
        print("❌ No se encontró directorio .workspace/departments")
        return offices

    # Buscar en todos los departamentos
    for dept_dir in departments_path.iterdir():
        if dept_dir.is_dir():
            # Buscar agentes en cada departamento
            for agent_dir in dept_dir.iterdir():
                if agent_dir.is_dir():
                    offices.append({
                        "department": dept_dir.name,
                        "agent": agent_dir.name,
                        "path": agent_dir
                    })

    return offices

def distribute_file(source_file, target_filename, offices):
    """Distribuir archivo a todas las oficinas"""
    if not os.path.exists(source_file):
        print(f"❌ Archivo fuente no encontrado: {source_file}")
        return False

    success_count = 0
    error_count = 0

    for office in offices:
        try:
            target_path = office["path"] / target_filename
            shutil.copy2(source_file, target_path)
            success_count += 1
            print(f"✅ {office['department']}/{office['agent']}")
        except Exception as e:
            error_count += 1
            print(f"❌ {office['department']}/{office['agent']}: {e}")

    print(f"\n📊 RESULTADO: {success_count} exitosos, {error_count} errores")
    return error_count == 0

def create_office_specific_config(office):
    """Crear configuración específica para cada oficina"""
    config_content = f"""# 🤖 CONFIGURACIÓN DE OFICINA: {office['agent']}

## 📍 UBICACIÓN
- **Departamento**: {office['department']}
- **Agente**: {office['agent']}
- **Oficina**: .workspace/departments/{office['department']}/{office['agent']}/

## 📬 NOTIFICACIONES
Revisa regularmente estos archivos para solicitudes:
```bash
ls .workspace/departments/{office['department']}/{office['agent']}/URGENT_REQUEST_*.json
```

## 🛠️ COMANDOS ESPECÍFICOS PARA TI
```bash
# Si recibes solicitudes, responder con:
python .workspace/scripts/respond_to_request.py [request-id] [APPROVE/DENY] "[motivo]"

# Para solicitar modificaciones:
python .workspace/scripts/contact_responsible_agent.py {office['agent']} [archivo] "[motivo]"

# Validar antes de modificar:
python .workspace/scripts/agent_workspace_validator.py {office['agent']} [archivo]
```

## 📚 DOCUMENTACIÓN OBLIGATORIA
- 📋 LEER PRIMERO: ./QUICK_START_GUIDE.md
- 📖 Reglas globales: ../../SYSTEM_RULES.md
- 🛡️ Archivos protegidos: ../../PROTECTED_FILES.md
- 👥 Responsables: ../../RESPONSIBLE_AGENTS.md

---
**🔄 Actualizado automáticamente por distribute_instructions.py**
"""

    config_file = office["path"] / "OFFICE_CONFIG.md"
    try:
        with open(config_file, 'w') as f:
            f.write(config_content)
        return True
    except Exception as e:
        print(f"❌ Error creando config para {office['agent']}: {e}")
        return False

def main():
    """Función principal"""
    print("📢 DISTRIBUIDOR DE INSTRUCCIONES A AGENTES")
    print("=" * 50)

    # Encontrar todas las oficinas
    offices = find_agent_offices()
    print(f"🏢 Encontradas {len(offices)} oficinas de agentes")

    if not offices:
        print("❌ No se encontraron oficinas de agentes")
        return

    # Archivos para distribuir
    files_to_distribute = [
        {
            "source": ".workspace/QUICK_START_GUIDE.md",
            "target": "QUICK_START_GUIDE.md",
            "description": "Guía rápida de comandos"
        },
        {
            "source": ".workspace/SYSTEM_RULES.md",
            "target": "SYSTEM_RULES.md",
            "description": "Reglas globales del sistema"
        }
    ]

    # Distribuir archivos
    for file_info in files_to_distribute:
        print(f"\n📤 Distribuyendo {file_info['description']}...")
        distribute_file(file_info["source"], file_info["target"], offices)

    # Crear configuraciones específicas por oficina
    print(f"\n🔧 Creando configuraciones específicas...")
    success_count = 0
    for office in offices:
        if create_office_specific_config(office):
            success_count += 1

    print(f"✅ {success_count}/{len(offices)} configuraciones creadas")

    # Mostrar resumen por departamento
    print(f"\n📊 RESUMEN POR DEPARTAMENTO:")
    dept_count = {}
    for office in offices:
        dept = office["department"]
        dept_count[dept] = dept_count.get(dept, 0) + 1

    for dept, count in sorted(dept_count.items()):
        print(f"  📁 {dept}: {count} agentes")

    print(f"\n✅ DISTRIBUCIÓN COMPLETADA")
    print(f"📋 Todos los agentes ahora tienen acceso a:")
    print(f"   - Guía rápida de comandos")
    print(f"   - Configuración específica de su oficina")
    print(f"   - Reglas globales del sistema")

if __name__ == "__main__":
    main()