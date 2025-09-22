# 🚀 Comandos de Testing - Master Orchestrator

## Comandos Disponibles

### 1. Comando Rápido (Recomendado)
```bash
test                        # Alias configurado - Versión rápida
./test-command-fast.sh      # Comando directo
```
**Características:**
- ⚡ Ejecución rápida (30-60 segundos)
- 📊 Análisis básico de cobertura
- 🤖 Activación de 3 agentes especializados
- 📋 Reporte resumido

### 2. Comando Completo (Análisis Profundo)
```bash
./test-command.sh           # Comando directo - Versión completa
```
**Características:**
- 🔍 Análisis exhaustivo (2-5 minutos)
- 📊 Cobertura detallada con métricas
- 🤖 Monitoreo cíclico de agentes
- 📋 Reporte completo con verificación final

### 3. Script Python Directo (Máximo Control)
```bash
python .workspace/scripts/master_testing_orchestrator.py
```
**Características:**
- 🛠️ Control total del proceso
- ⚙️ Parámetros personalizables
- 📊 Métricas avanzadas
- 🔄 Ciclos de optimización

## Configuración Actual

✅ **Alias `test`** → `./test-command-fast.sh` (Versión rápida)

## Uso Recomendado

**Para desarrollo diario:**
```bash
test
```

**Para validación completa:**
```bash
./test-command.sh
```

**Para debugging:**
```bash
python .workspace/scripts/master_testing_orchestrator.py
```

## Características de Cada Versión

| Comando | Tiempo | Cobertura | Agentes | Reportes |
|---------|--------|-----------|---------|----------|
| `test` | 30-60s | Básica | 3 | Resumido |
| `./test-command.sh` | 2-5min | Completa | 3 | Detallado |
| Script Python | Variable | Avanzada | Hasta 3 | Completo |