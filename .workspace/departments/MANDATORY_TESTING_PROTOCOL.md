# PROTOCOLO OBLIGATORIO DE TESTING - TODOS LOS DEPARTAMENTOS
**VIGENCIA: INMEDIATA - SIN EXCEPCIONES**

## 🎯 OBJETIVO CRÍTICO
**TODOS LOS 1,876 TESTS DEBEN PASAR - SIN EXCEPCIÓN**

## ⚠️ REGLAS OBLIGATORIAS PARA TODOS LOS AGENTES

### 📋 REGLA #1: CÓDIGO NUEVO = TESTS OBLIGATORIOS
```bash
# ANTES de escribir cualquier código:
1. Crear el test correspondiente
2. Validar que el test pase
3. Verificar cobertura mínima 90%
```

### 📋 REGLA #2: VERIFICACIÓN OBLIGATORIA PRE-COMMIT
```bash
# ANTES de cualquier modificación:
python -m pytest tests/ -x --tb=short
# Si falla CUALQUIER test -> NO CONTINUAR
```

### 📋 REGLA #3: COVERAGE MÍNIMO OBLIGATORIO
```bash
# Cobertura requerida:
- Nuevos servicios: 95% coverage
- Modificaciones: 90% coverage
- APIs: 100% coverage
- Modelos: 85% coverage
```

## 🚨 DEPARTAMENTOS ESPECÍFICOS

### 🔧 BACKEND-SENIOR-DEVELOPER
**RESPONSABILIDAD:** Implementar servicios faltantes con tests completos
- `commission_service.py` -> Crear tests unitarios + integración
- `transaction_service.py` -> Implementar + tests completos
- `fraud_detection_service.py` -> Tests de seguridad obligatorios

### 🎨 FRONTEND-UNIVERSAL-SPECIALIST
**RESPONSABILIDAD:** Tests frontend obligatorios
- Nuevos componentes -> Jest tests + Cypress E2E
- Modificaciones -> Actualizar tests existentes
- Coverage mínimo: 90%

### 🛡️ SECURITY-AUDIT-SPECIALIST
**RESPONSABILIDAD:** Tests de seguridad obligatorios
- Auditorías -> Tests de validación
- Vulnerabilidades -> Tests de regresión
- Compliance -> Tests automatizados

### ⚙️ DEVOPS-DEPLOYMENT-SPECIALIST
**RESPONSABILIDAD:** Tests de infraestructura
- CI/CD -> Incluir TODOS los tests
- Deployment -> Tests de smoke obligatorios
- Docker -> Tests de contenedores

### 🧪 QA-ENGINEER-PYTEST
**RESPONSABILIDAD:** LÍDER DE TESTING
- **MISIÓN PRINCIPAL:** Corregir todos los 1,876 tests
- Supervisar cumplimiento de protocolos
- Reportar progreso cada 200 tests corregidos

## ⚡ COMANDOS OBLIGATORIOS

### ✅ Pre-Development Check
```bash
# Ejecutar SIEMPRE antes de trabajar:
python -m pytest tests/core/ tests/api/ tests/debugging/ -v
# Debe mostrar: 113/113 tests PASSING
```

### ✅ Full Project Validation
```bash
# Meta final - TODOS deben pasar:
python -m pytest tests/ -v
# Meta: 1,876/1,876 tests PASSING ✅
```

### ✅ Coverage Validation
```bash
# Verificar coverage después de cambios:
python -m pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
```

## 🚨 PROTOCOLO DE EMERGENCIA

### ❌ Si un agente rompe tests:
1. **STOP INMEDIATO** - No continuar desarrollo
2. Reportar al manager (tú) inmediatamente
3. Rollback cambios si es necesario
4. Corregir tests antes de continuar

### ⚠️ Si tests fallan después de modificación:
```bash
# Comando de diagnóstico obligatorio:
python -m pytest tests/ -v --tb=short --maxfail=5
# Identificar causa raíz
# Corregir TODOS los errores
# Re-ejecutar hasta 100% passing
```

## 📊 MÉTRICAS OBLIGATORIAS

### 🎯 ESTADO ACTUAL:
- **Tests pasando:** 113/1,876 (6%)
- **Tests objetivo:** 1,876/1,876 (100%)
- **Coverage actual:** 36.27%
- **Coverage objetivo:** 90%+

### 📈 REPORTES REQUERIDOS:
- **QA Agent:** Progreso cada 200 tests corregidos
- **Otros agentes:** Status tests con cada entrega
- **Manager:** Dashboard semanal de métricas

## 🔒 VERIFICACIÓN FINAL

### ✅ Checklist Pre-Entrega (OBLIGATORIO):
- [ ] Todos los tests del área pasan ✅
- [ ] Coverage >= 90% ✅
- [ ] No hay imports faltantes ✅
- [ ] No hay warnings críticos ✅
- [ ] Tests de regresión ejecutados ✅

## 🚀 EJECUCIÓN INMEDIATA

**FASE 1 - YA INICIADA:** QA Agent corrigiendo servicios backend
**FASE 2:** Infraestructura y fixtures
**FASE 3:** Corrección sistemática 1,876 tests
**FASE 4:** Validación final y métricas

---
**MENSAJE FINAL:** Sin tests pasando = Sin deployment = Sin MVP ready
**RESPONSABILIDAD:** Todos los agentes - No hay excepciones

🎯 **OBJETIVO:** pytest tests/ -> 1,876/1,876 PASSING ✅