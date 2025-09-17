#!/bin/bash
# COMANDO INTELIGENTE DE ACTUALIZACIÓN MASIVA DEPARTAMENTAL
# Distribuye MANDATORY_INSTRUCTIONS.md a todos los departamentos
# Autor: Manager Enterprise
# Fecha: 14 Septiembre 2025

set -e

echo "🚨 INICIANDO ACTUALIZACIÓN MASIVA DEPARTAMENTAL"
echo "📋 Distribuyendo MANDATORY_INSTRUCTIONS.md a todos los departamentos..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directorio base
BASE_DIR="/home/admin-jairo/MeStore/.workspace/departments"
cd "$BASE_DIR"

# Contador
UPDATED=0
CREATED=0

# Manual principal
MANUAL_SOURCE="$BASE_DIR/MANDATORY_INSTRUCTIONS.md"

if [ ! -f "$MANUAL_SOURCE" ]; then
    echo -e "${RED}❌ ERROR: MANDATORY_INSTRUCTIONS.md no encontrado en $BASE_DIR${NC}"
    exit 1
fi

echo -e "${BLUE}📂 Escaneando departamentos...${NC}"

# Encontrar todos los departamentos
DEPARTMENTS=$(find . -maxdepth 1 -type d | grep -v '^\.$' | sort)

for dept in $DEPARTMENTS; do
    dept_name=$(basename "$dept")
    dept_path="$BASE_DIR/$dept"
    instructions_file="$dept_path/MANDATORY_INSTRUCTIONS.md"

    echo -e "${YELLOW}🔧 Procesando: $dept_name${NC}"

    # Crear el directorio si no existe
    mkdir -p "$dept_path"

    # Copiar el manual
    if cp "$MANUAL_SOURCE" "$instructions_file"; then
        echo -e "${GREEN}✅ Manual distribuido a: $dept_name${NC}"

        # Agregar header específico del departamento
        temp_file=$(mktemp)
        {
            echo "# 🏢 DEPARTAMENTO: $dept_name"
            echo "**INSTRUCCIONES ESPECÍFICAS PARA ESTE DEPARTAMENTO**"
            echo ""
            cat "$instructions_file"
        } > "$temp_file"

        mv "$temp_file" "$instructions_file"

        ((UPDATED++))
    else
        echo -e "${RED}❌ Error copiando a: $dept_name${NC}"
    fi

    # Crear archivo instructions.md específico si no existe
    specific_instructions="$dept_path/instructions.md"
    if [ ! -f "$specific_instructions" ]; then
        cat > "$specific_instructions" << EOF
# INSTRUCCIONES ESPECÍFICAS - DEPARTAMENTO: $dept_name

## 🚨 LECTURA OBLIGATORIA ANTES DE TRABAJAR
**DEBES LEER MANDATORY_INSTRUCTIONS.md PRIMERO**

## 📋 CONFIGURACIONES ESPECÍFICAS PARA $dept_name:

### Estado del Sistema (VERIFICAR ANTES DE TRABAJAR):
- Backend: http://localhost:8000 (DEBE RESPONDER)
- Frontend: http://localhost:5173 (DEBE CARGAR)
- Login: super@mestore.com/123456 (DEBE FUNCIONAR)

### Archivos que NO DEBES TOCAR sin autorización:
- /home/admin-jairo/MeStore/.env
- /home/admin-jairo/MeStore/mestore_production.db
- /home/admin-jairo/MeStore/app/core/security.py
- /home/admin-jairo/MeStore/app/services/auth_service.py

### ANTES de hacer cualquier cambio:
1. Verificar que el sistema funciona
2. Leer PROJECT_CONTEXT.md
3. Coordinar con manager si hay dudas
4. Documentar todos los cambios

### Al terminar tu trabajo:
1. Verificar que el sistema sigue funcionando
2. Actualizar este archivo con lo que hiciste
3. Reportar al manager

---
**ÚLTIMA ACTUALIZACIÓN:** $(date)
**AGENTE RESPONSABLE:** $dept_name
**ESTADO:** Sistema funcionando - NO ROMPER
EOF
        echo -e "${BLUE}📝 Creado instructions.md específico para: $dept_name${NC}"
        ((CREATED++))
    fi

    # Crear README departamental
    readme_file="$dept_path/README.md"
    if [ ! -f "$readme_file" ]; then
        cat > "$readme_file" << EOF
# 🏢 DEPARTAMENTO: $dept_name

## 🚨 ANTES DE TRABAJAR - LECTURA OBLIGATORIA:
1. **MANDATORY_INSTRUCTIONS.md** - Manual obligatorio de coordinación
2. **instructions.md** - Instrucciones específicas de este departamento
3. **PROJECT_CONTEXT.md** - Estado actual del sistema (ruta: ../PROJECT_CONTEXT.md)

## 📊 ESTADO ACTUAL DEL SISTEMA:
- ✅ Backend funcionando: http://localhost:8000
- ✅ Frontend funcionando: http://localhost:5173
- ✅ Autenticación operativa: super@mestore.com/123456
- ✅ Base de datos operativa: mestore_production.db

## ⚠️ RESPONSABILIDADES DE ESTE DEPARTAMENTO:
- Mantener la funcionalidad existente
- Coordinar cambios con otros departamentos
- Documentar todo el trabajo realizado
- No romper el sistema operativo

## 📞 CONTACTO PARA COORDINACIÓN:
- Manager: enterprise-project-manager
- Emergencias: Reportar al usuario
- Dudas: Consultar via Task tool

---
**Departamento creado:** $(date)
**Manual actualizado:** $(date)
**Próxima revisión:** Al hacer cambios en el sistema
EOF
        echo -e "${BLUE}📖 Creado README para: $dept_name${NC}"
    fi
done

echo -e "${GREEN}🎉 ACTUALIZACIÓN MASIVA COMPLETADA${NC}"
echo -e "${YELLOW}📊 Resumen:${NC}"
echo -e "  • Departamentos actualizados: $UPDATED"
echo -e "  • Archivos creados: $CREATED"
echo -e "  • Manual distribuido a todos los departamentos"
echo -e ""
echo -e "${BLUE}📋 Próximos pasos para asegurar coordinación:${NC}"
echo -e "  1. Todos los agentes DEBEN leer MANDATORY_INSTRUCTIONS.md"
echo -e "  2. Verificar el estado del sistema antes de trabajar"
echo -e "  3. Coordinar cambios críticos con el manager"
echo -e "  4. Documentar todo el trabajo realizado"
echo -e ""
echo -e "${GREEN}✅ Sistema de coordinación departamental ACTIVADO${NC}"