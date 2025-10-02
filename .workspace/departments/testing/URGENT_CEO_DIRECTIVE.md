# 🚨 ALERTA URGENTE - DEPARTAMENTO TESTING

**Fecha**: 2025-10-01
**De**: Director Enterprise CEO
**Para**: TODOS los agentes del departamento Testing
**Prioridad**: CRÍTICA

---

## 📢 DIRECTIVA CEO: ESTANDARIZACIÓN DE CÓDIGO

Se ha emitido una **directiva ejecutiva obligatoria** sobre estandarización de código.

### ⚡ CAMBIOS INMEDIATOS PARA TESTING:

#### ❌ PROHIBIDO en tests:
```python
# ❌ Tests con nombres en español
def test_crear_producto():
    datos_producto = {...}
    resultado = crear_producto(datos_producto)

# ❌ Fixtures en español
@pytest.fixture
def datos_vendedor():
    return {...}
```

#### ✅ OBLIGATORIO en tests:
```python
# ✅ Tests con nombres en inglés
def test_create_product():
    product_data = {...}
    result = create_product(product_data)

# ✅ Fixtures en inglés
@pytest.fixture
def vendor_data():
    return {...}
```

---

## 🎯 AGENTES TESTING CON RESPONSABILIDAD DIRECTA:

### TESTS DE APIS CONSOLIDADAS:
**api-testing-specialist** - CRÍTICO: Actualizar tests para nuevas APIs

### TESTS DE REGRESIÓN:
**tdd-specialist** - Validar no se rompa funcionalidad
**integration-testing** - Tests end-to-end

### OTROS RESPONSABLES:
- **unit-testing-ai** - Tests unitarios
- **e2e-testing-specialist** - Tests E2E
- **performance-testing** - Tests performance
- **security-testing** - Tests seguridad

---

## 🧪 ACTUALIZACIÓN DE TESTS (Crítico):

### Tests a actualizar por consolidación APIs:

```python
# ❌ ANTES (deprecado)
response = client.get("/api/v1/productos/")
response = client.post("/api/v1/vendedores/registro")

# ✅ DESPUÉS (obligatorio)
response = client.get("/api/v1/products/")
response = client.post("/api/v1/vendors/register")
```

### Archivos a revisar:
- `tests/test_products.py` - Tests productos
- `tests/test_vendors.py` - Tests vendedores
- `tests/test_commissions.py` - Tests comisiones
- `tests/test_payments.py` - Tests pagos

---

## 📋 TESTS DE DEPRECACIÓN:

Crear tests que verifiquen:

1. **Endpoints deprecados retornan warning**
2. **Redirección a nuevos endpoints funciona**
3. **Nuevos endpoints funcionan correctamente**
4. **No hay breaking changes**

---

## 📝 NUEVO TEMPLATE DE COMMITS:

```
tipo(área): descripción en inglés

Workspace-Check: ✅ Consultado
File: tests/test_[nombre].py
Agent: [tu-nombre]
Protocol: FOLLOWED
Tests: PASSED
Code-Standard: ✅ ENGLISH_CODE
API-Duplication: NONE

Description:
[Descripción del cambio]
```

---

## ✅ ACCIÓN REQUERIDA:

1. **Leer directiva completa**: `.workspace/URGENT_BROADCAST_CEO_CODE_STANDARDIZATION.md`
2. **Confirmar lectura**:
   ```bash
   python .workspace/scripts/confirm_directive_read.py [tu-agente] CEO-CODE-STANDARDS-2025-10-01
   ```
3. **Actualizar tests para nuevas APIs** (Semanas 3-5)
4. **Validar no hay regresiones**

---

## 🔗 RECURSOS:

- **Directiva Completa**: `.workspace/URGENT_BROADCAST_CEO_CODE_STANDARDIZATION.md`
- **Resumen Ejecutivo**: `.workspace/EXECUTIVE_SUMMARY_CODE_STANDARDIZATION.md`
- **Análisis Técnico**: `/home/admin-jairo/MeStore/API_DUPLICATIONS_ANALYSIS.md`

---

**Esta directiva es de cumplimiento OBLIGATORIO para todo el departamento Testing**
