# 🚨 ALERTA URGENTE - DEPARTAMENTO BACKEND

**Fecha**: 2025-10-01
**De**: Director Enterprise CEO
**Para**: TODOS los agentes del departamento Backend
**Prioridad**: CRÍTICA

---

## 📢 DIRECTIVA CEO: ESTANDARIZACIÓN DE CÓDIGO

Se ha emitido una **directiva ejecutiva obligatoria** sobre estandarización de código.

### ⚡ CAMBIOS INMEDIATOS PARA BACKEND:

#### ❌ PROHIBIDO desde hoy:
```python
# ❌ Endpoints en español
@router.get("/api/v1/productos/")
@router.get("/api/v1/vendedores/")
@router.get("/api/v1/comisiones/")

# ❌ Variables/funciones en español
def crear_producto(datos_producto):
    precio_total = calcular_total()
```

#### ✅ OBLIGATORIO desde hoy:
```python
# ✅ Endpoints en inglés
@router.get("/api/v1/products/")
@router.get("/api/v1/vendors/")
@router.get("/api/v1/commissions/")

# ✅ Variables/funciones en inglés
def create_product(product_data):
    total_price = calculate_total()
```

#### ✅ MANTENER mensajes de usuario en español:
```python
# ✅ CORRECTO
raise HTTPException(
    status_code=400,
    detail="El producto ya existe en tu inventario"
)
```

---

## 🎯 AGENTES BACKEND CON RESPONSABILIDAD DIRECTA:

### LÍDER DE CONSOLIDACIÓN:
**backend-framework-ai** - Responsable principal de consolidar APIs

### ARQUITECTURA:
**api-architect-ai** - Diseño de APIs consolidadas

### OTROS RESPONSABLES:
- **security-backend-ai** - Validación seguridad
- **api-security** - Seguridad APIs
- **database-performance** - Performance
- **error-handling-specialist** - Manejo errores

---

## 📋 ARCHIVOS EN DEPRECACIÓN (Backend):

| Archivo | Estado | Acción Requerida |
|---------|--------|------------------|
| `app/api/v1/endpoints/productos.py` | DEPRECATED | Migrar a products.py |
| `app/api/v1/endpoints/vendedores.py` | DEPRECATED | Migrar a vendors.py |
| `app/api/v1/endpoints/comisiones.py` | DEPRECATED | Migrar a commissions.py |
| `app/api/v1/endpoints/pagos.py` | DEPRECATED | Migrar a payments.py |

**Timeline**: 6-7 semanas para eliminación completa

---

## 📝 NUEVO TEMPLATE DE COMMITS:

```
tipo(área): descripción en inglés

Workspace-Check: ✅ Consultado
File: ruta/del/archivo
Agent: [tu-nombre]
Protocol: FOLLOWED
Tests: PASSED
Code-Standard: ✅ ENGLISH_CODE
API-Duplication: [NONE/CONSOLIDATED/DEPRECATED]

Description:
[Descripción del cambio]
```

**Campo OBLIGATORIO**: `Code-Standard: ✅ ENGLISH_CODE`

---

## ✅ ACCIÓN REQUERIDA:

1. **Leer directiva completa**: `.workspace/URGENT_BROADCAST_CEO_CODE_STANDARDIZATION.md`
2. **Confirmar lectura**:
   ```bash
   python .workspace/scripts/confirm_directive_read.py [tu-agente] CEO-CODE-STANDARDS-2025-10-01
   ```
3. **Aplicar desde próximo commit**

---

## 🔗 RECURSOS:

- **Directiva Completa**: `.workspace/URGENT_BROADCAST_CEO_CODE_STANDARDIZATION.md`
- **Resumen Ejecutivo**: `.workspace/EXECUTIVE_SUMMARY_CODE_STANDARDIZATION.md`
- **Análisis Técnico**: `/home/admin-jairo/MeStore/API_DUPLICATIONS_ANALYSIS.md`

---

**Esta directiva es de cumplimiento OBLIGATORIO para todo el departamento Backend**
