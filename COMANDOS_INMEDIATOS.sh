#!/bin/bash
# 🚨 COMANDOS INMEDIATOS - MESTORE ACTIVACIÓN
# Ejecutar HOY para seguridad
# Fecha: 2025-10-21

echo "🚀 MESTORE - Activación de Seguridad"
echo "===================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Directorio del proyecto
PROJECT_DIR="/home/admin-jairo/MeStore"
cd "$PROJECT_DIR" || exit 1

echo -e "${YELLOW}PASO 1: Verificación de Seguridad${NC}"
echo "-----------------------------------"

# Verificar si .env existe
if [ -f ".env" ]; then
    echo -e "${RED}⚠️  .env encontrado${NC}"
    echo "Contraseñas expuestas detectadas:"
    grep "PASSWORD\|SECRET" .env | sed 's/=.*/=***OCULTO***/'
else
    echo -e "${GREEN}✅ .env no encontrado en directorio actual${NC}"
fi

# Verificar si .env está en git
if git ls-files --error-unmatch .env > /dev/null 2>&1; then
    echo -e "${RED}🚨 CRÍTICO: .env ESTÁ EN GIT TRACKING${NC}"
    echo ""
    echo "Para removerlo del historial, ejecuta manualmente:"
    echo ""
    echo "git filter-branch --force --index-filter \\"
    echo "  'git rm --cached --ignore-unmatch .env' \\"
    echo "  --prune-empty --tag-name-filter cat -- --all"
    echo ""
    echo -e "${YELLOW}⚠️  ADVERTENCIA: Esto reescribe el historial de git${NC}"
    echo "Si tienes remote (GitHub), necesitarás force push después."
    echo ""
else
    echo -e "${GREEN}✅ .env no está en git tracking${NC}"
fi

echo ""
echo -e "${YELLOW}PASO 2: Crear .env.example (plantilla sin secretos)${NC}"
echo "---------------------------------------------------"

if [ -f ".env" ]; then
    # Crear .env.example con valores de ejemplo
    cat > .env.example << 'EOF'
# DATABASE
DATABASE_URL=postgresql://user:password@localhost:5432/mestore_db
DATABASE_PASSWORD=tu_password_aqui

# SECURITY
SECRET_KEY=genera_con_openssl_rand_hex_32
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# EMAIL
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_password_de_aplicacion_aqui

# REDIS
REDIS_URL=redis://localhost:6379/0

# FRONTEND
FRONTEND_URL=http://localhost:5173

# ENVIRONMENT
ENVIRONMENT=development

# COLOMBIAN APIS (opcional)
WOMPI_PUBLIC_KEY=tu_public_key_aqui
WOMPI_PRIVATE_KEY=tu_private_key_aqui
PAYU_API_KEY=tu_api_key_aqui
TWILIO_ACCOUNT_SID=tu_account_sid_aqui
TWILIO_AUTH_TOKEN=tu_auth_token_aqui

# STORAGE
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=5242880
EOF
    echo -e "${GREEN}✅ .env.example creado${NC}"
    echo "Revisa este archivo y ajusta según necesites."
else
    echo -e "${YELLOW}⚠️  .env no encontrado, .env.example no creado${NC}"
fi

echo ""
echo -e "${YELLOW}PASO 3: Verificar .gitignore${NC}"
echo "------------------------------"

# Verificar que .env está en .gitignore
if grep -q "^\.env$" .gitignore 2>/dev/null; then
    echo -e "${GREEN}✅ .env está en .gitignore${NC}"
else
    echo -e "${YELLOW}⚠️  Agregando .env a .gitignore${NC}"
    echo "" >> .gitignore
    echo "# Environment variables" >> .gitignore
    echo ".env" >> .gitignore
    echo ".env.local" >> .gitignore
    echo -e "${GREEN}✅ .env agregado a .gitignore${NC}"
fi

echo ""
echo -e "${YELLOW}PASO 4: Generar nuevo SECRET_KEY${NC}"
echo "--------------------------------"

if command -v openssl &> /dev/null; then
    NEW_SECRET_KEY=$(openssl rand -hex 32)
    echo -e "${GREEN}✅ Nuevo SECRET_KEY generado:${NC}"
    echo ""
    echo "SECRET_KEY=$NEW_SECRET_KEY"
    echo ""
    echo "Copia este valor y agrégalo a tu .env y Railway secrets"
else
    echo -e "${RED}⚠️  openssl no encontrado${NC}"
    echo "Genera manualmente con: openssl rand -hex 32"
fi

echo ""
echo -e "${YELLOW}PASO 5: Instrucciones para Railway${NC}"
echo "-----------------------------------"
echo ""
echo "1. Instalar Railway CLI (si no lo tienes):"
echo "   npm install -g @railway/cli"
echo ""
echo "2. Login en Railway:"
echo "   railway login"
echo ""
echo "3. Configurar secrets en Railway:"
echo "   railway variables set EMAIL_HOST_PASSWORD='tu_nueva_password'"
echo "   railway variables set SECRET_KEY='$NEW_SECRET_KEY'"
echo "   railway variables set DATABASE_PASSWORD='tu_db_password'"
echo ""
echo "4. Verificar variables:"
echo "   railway variables"
echo ""

echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}ACCIÓN REQUERIDA MANUAL (HOY):${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo -e "${RED}1. CAMBIAR CONTRASEÑA DE GMAIL${NC}"
echo "   Email: jlcmbc0259@gmail.com"
echo "   Ir a: https://myaccount.google.com/security"
echo "   Cambiar contraseña: jlcmbc0259*a → nueva_password"
echo "   Generar 'Contraseña de aplicación' para SMTP"
echo ""
echo -e "${YELLOW}2. ACTUALIZAR .env CON NUEVA PASSWORD${NC}"
echo "   Editar .env y reemplazar:"
echo "   EMAIL_HOST_PASSWORD=tu_nueva_password_de_aplicacion"
echo ""
echo -e "${YELLOW}3. CONFIGURAR RAILWAY SECRETS${NC}"
echo "   Ejecutar comandos de Railway arriba"
echo ""
echo -e "${YELLOW}4. REMOVER .env DE GIT (si aplica)${NC}"
echo "   Ejecutar el comando git filter-branch mostrado arriba"
echo "   SOLO si .env está en git tracking"
echo ""

echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}DESPUÉS DE SEGURIDAD, ACTIVACIÓN:${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo "Ver archivo: GUIA_ACTIVACION_MESTORE.md"
echo ""
echo "Siguientes pasos:"
echo "1. Levantar ambiente local (docker-compose up -d)"
echo "2. Correr tests (pytest tests/api/test_critical_endpoints_mvp.py)"
echo "3. Deploy a Railway"
echo "4. Registrar primer vendedor de prueba"
echo ""
echo -e "${GREEN}✅ Tu proyecto ESTÁ LISTO para activar${NC}"
echo -e "${GREEN}✅ Timeline: 2-4 semanas${NC}"
echo -e "${GREEN}✅ NO necesitas empezar desde cero${NC}"
echo ""
echo "¡Éxito con MeStore! 🚀"
