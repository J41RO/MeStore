# 🚀 MESTOCKER SCRIPT MANAGERS

Scripts modernos para gestión de desarrollo con menús organizados, logs en tiempo real y control completo.

## 📋 Scripts Disponibles

### 🐍 Backend Manager
```bash
./scripts/backend_manager.sh
```

**Funcionalidades:**
- ✅ **Iniciar Backend** - FastAPI + Uvicorn con health check
- 🔄 **Reload Backend** - Reinicio rápido
- 🔥 **Reset Completo** - Detener + limpiar logs + iniciar
- 🛑 **Detener Backend** - Parada limpia de procesos
- 📋 **Logs en Tiempo Real** - Visualización colorizada
- 📊 **Estado del Servicio** - PID, uptime, URLs

**URLs del Backend:**
- API: `http://192.168.1.137:8000`
- Documentación: `http://192.168.1.137:8000/docs`

---

### ⚛️ Frontend Manager
```bash
./scripts/frontend_manager.sh
```

**Funcionalidades:**
- ✅ **Iniciar Frontend** - React + Vite con HMR
- 🔄 **Reload Frontend** - Reinicio rápido
- 🔥 **Reset Completo** - Detener + limpiar cache + iniciar
- 🛑 **Detener Frontend** - Parada limpia de procesos
- 📦 **Build Producción** - Compilación optimizada
- 📋 **Logs en Tiempo Real** - Visualización colorizada
- 📊 **Estado del Servicio** - PID, uptime, URLs

**URLs del Frontend:**
- Desarrollo: `http://192.168.1.137:5173`

---

## 🎛️ Características Avanzadas

### ✨ **Interfaz Visual Mejorada**
- Headers con información del sistema
- Colores y emojis para mejor UX
- Barras de estado visuales
- Menús organizados por categorías

### 🏥 **Health Checks Robustos**
- Verificación automática de puertos ocupados
- Intentos múltiples de conexión (15-20 reintentos)
- Validación de procesos por PID y nombre
- Limpieza automática de procesos zombi

### 📋 **Logging Avanzado**
- Logs colorizados por nivel (INFO, ERROR, WARN)
- Timestamps en tiempo real
- Rotación automática de logs
- Logs separados por servicio en `/logs/`

### 🔄 **Gestión de Procesos**
- Tracking de PIDs en `/tmp/mestocker_*.pid`
- Terminación grácil con fallback a SIGKILL
- Limpieza por nombre de proceso y puerto
- Detección de servicios ya ejecutándose

### ⚡ **Configuración Flexible**
- Variables configurables en `config.env`
- Hosts y puertos personalizables
- Rutas de logs configurables
- Detección automática de entorno virtual

---

## 📁 Estructura de Archivos

```
scripts/
├── backend_manager.sh     # 🐍 Gestor del backend FastAPI
├── frontend_manager.sh    # ⚛️ Gestor del frontend React
└── README.md             # 📚 Esta documentación

logs/
├── backend.log           # 📋 Logs del backend
├── frontend.log          # 📋 Logs del frontend
└── *.log.*              # 🗄️ Logs rotados (auto-limpieza 7 días)

/tmp/
├── mestocker_backend.pid  # 🆔 PID del backend
└── mestocker_frontend.pid # 🆔 PID del frontend
```

---

## 🚀 Inicio Rápido

### Para Backend:
```bash
cd /home/admin-jairo/MeStore
./scripts/backend_manager.sh
# Presiona 1 para iniciar
# Presiona 5 para ver logs en tiempo real
```

### Para Frontend:
```bash
cd /home/admin-jairo/MeStore
./scripts/frontend_manager.sh
# Presiona 1 para iniciar
# Presiona 6 para ver logs en tiempo real
```

---

## ⌨️ Atajos de Teclado

### Backend Manager:
- `1` - Iniciar Backend
- `2` - Reload Backend
- `3` - Reset Completo
- `4` - Detener Backend
- `5` - Ver Logs
- `6` - Actualizar Estado
- `0` - Salir

### Frontend Manager:
- `1` - Iniciar Frontend
- `2` - Reload Frontend
- `3` - Reset Completo
- `4` - Detener Frontend
- `5` - Build Producción
- `6` - Ver Logs
- `7` - Actualizar Estado
- `0` - Salir

---

## 🔧 Configuración Avanzada

Crea un archivo `config.env` en la raíz del proyecto para personalizar:

```bash
# config.env
BACKEND_HOST="0.0.0.0"
BACKEND_PORT=8001
FRONTEND_HOST="0.0.0.0"
FRONTEND_PORT=3000
LOG_DIR="/custom/log/path"
```

---

## 🏆 Beneficios

### ✅ **Productividad**
- Inicio/parada de servicios en 1 click
- Logs en tiempo real sin comandos complejos
- Estado visual inmediato de servicios
- No más búsqueda manual de PIDs

### 🛡️ **Robustez**
- Detección automática de conflictos de puerto
- Limpieza completa de procesos huérfanos
- Health checks con reintentos automáticos
- Manejo elegante de errores

### 👁️ **Visibilidad**
- Estado en tiempo real de servicios
- Logs colorizados por importancia
- Información de uptime y PIDs
- URLs directas para acceso rápido

### 🧹 **Mantenimiento**
- Rotación automática de logs
- Limpieza de archivos temporales
- Detección de entornos virtuales
- Auto-instalación de dependencias

---

## 📞 Soporte

Los scripts están diseñados para ser **self-contained** y manejar la mayoría de escenarios automáticamente. Si encuentras algún problema:

1. Verifica que los directorios existan
2. Revisa los logs en tiempo real (opción 5/6)
3. Usa la opción de reset completo (opción 3)
4. Verifica configuración en `config.env`

---

**🎯 Creado para maximizar la productividad del desarrollo de MeStore**