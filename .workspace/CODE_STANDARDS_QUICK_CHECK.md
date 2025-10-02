# ✅ CHECKLIST RÁPIDO - ESTÁNDARES DE CÓDIGO

**Versión**: 1.0.0
**Fecha**: 2025-10-01
**Uso**: Verificar antes de CADA commit

---

## 🚀 VERIFICACIÓN EN 30 SEGUNDOS

### ✅ CÓDIGO TÉCNICO (Backend/Frontend)

**Pregunta 1**: ¿Estás creando/modificando código técnico?

#### SI → Verifica que TODO esté en INGLÉS:

- [ ] **Nombres de endpoints/rutas**
  ```python
  ✅ /api/v1/products/
  ❌ /api/v1/productos/
  ```

- [ ] **Nombres de archivos**
  ```
  ✅ product_service.py
  ❌ servicio_productos.py
  ```

- [ ] **Variables y funciones**
  ```python
  ✅ def create_product(product_data):
  ❌ def crear_producto(datos_producto):
  ```

- [ ] **Clases y métodos**
  ```python
  ✅ class ProductService:
  ❌ class ServicioProducto:
  ```

- [ ] **Comentarios en código**
  ```python
  ✅ # Calculate total price with tax
  ❌ # Calcular precio total con impuestos
  ```

- [ ] **Docstrings**
  ```python
  ✅ """Creates a new product"""
  ❌ """Crea un nuevo producto"""
  ```

### ✅ CONTENIDO DE USUARIO (UI/Mensajes)

**Pregunta 2**: ¿Estás creando/modificando contenido visible al usuario?

#### SI → Verifica que TODO esté en ESPAÑOL:

- [ ] **Textos de UI**
  ```typescript
  ✅ <Button>Agregar al Carrito</Button>
  ❌ <Button>Add to Cart</Button>
  ```

- [ ] **Mensajes de error**
  ```python
  ✅ detail="El producto ya existe"
  ❌ detail="Product already exists"
  ```

- [ ] **Notificaciones**
  ```python
  ✅ title="Producto Aprobado"
  ❌ title="Product Approved"
  ```

- [ ] **Labels y placeholders**
  ```tsx
  ✅ <Input placeholder="Nombre del producto" />
  ❌ <Input placeholder="Product name" />
  ```

- [ ] **Emails a clientes**
  ```python
  ✅ subject="Tu pedido ha sido enviado"
  ❌ subject="Your order has been shipped"
  ```

---

## 📝 VERIFICACIÓN DE COMMIT

### Template Obligatorio:

```
tipo(área): descripción en inglés

Workspace-Check: ✅ Consultado
File: ruta/del/archivo
Agent: [tu-nombre]
Protocol: FOLLOWED
Tests: [PASSED/FAILED]
Code-Standard: [✅ ENGLISH_CODE / ✅ SPANISH_UI]
API-Duplication: [NONE/CONSOLIDATED/DEPRECATED]

Description:
[Descripción del cambio]
```

### Campos a verificar:

- [ ] **Code-Standard**: Incluido (OBLIGATORIO)
- [ ] **Descripción en inglés**: Primera línea en inglés
- [ ] **Tests**: Ejecutados y pasando
- [ ] **Agent**: Tu nombre correcto

---

## 🚫 ERRORES COMUNES

### ❌ ERROR 1: Mezclar idiomas
```python
# ❌ INCORRECTO
def create_product(datos_producto):  # Mezcla inglés/español
    precio_total = calculate_price()  # Mezcla inglés/español
```

```python
# ✅ CORRECTO
def create_product(product_data):
    total_price = calculate_price()
```

### ❌ ERROR 2: Código técnico en español
```python
# ❌ INCORRECTO
@router.get("/api/v1/productos/")
async def obtener_productos():
    pass
```

```python
# ✅ CORRECTO
@router.get("/api/v1/products/")
async def get_products():
    pass
```

### ❌ ERROR 3: UI en inglés
```typescript
// ❌ INCORRECTO
<Alert severity="error">
  Product not found
</Alert>
```

```typescript
// ✅ CORRECTO
<Alert severity="error">
  Producto no encontrado
</Alert>
```

---

## 🔍 ARCHIVOS EN DEPRECACIÓN

### ⚠️ NO MODIFICAR (deprecados):

- `app/api/v1/endpoints/productos.py`
- `app/api/v1/endpoints/vendedores.py`
- `app/api/v1/endpoints/comisiones.py`
- `app/api/v1/endpoints/pagos.py`

### ✅ USAR VERSIONES EN INGLÉS:

- `app/api/v1/endpoints/products.py`
- `app/api/v1/endpoints/vendors.py`
- `app/api/v1/endpoints/commissions.py`
- `app/api/v1/endpoints/payments.py`

---

## 🛠️ HERRAMIENTAS DE VALIDACIÓN

### Antes de commit:

```bash
# 1. Validar estándares de código
python .workspace/scripts/validate_code_standards.py [archivo]

# 2. Ejecutar tests
python -m pytest tests/ -v

# 3. Verificar linting
python -m black app/
npm run lint
```

### Ejemplo de validación:

```bash
$ python .workspace/scripts/validate_code_standards.py app/api/v1/endpoints/products.py

✅ Code: ENGLISH ✓
✅ API: /products/ ✓
✅ Functions: English names ✓
✅ Variables: English names ✓
✅ PASS - Code standards compliant
```

---

## ⚡ CHECKLIST FINAL ANTES DE COMMIT

- [ ] ✅ Código técnico en inglés
- [ ] ✅ Contenido usuario en español
- [ ] ✅ Template de commit correcto
- [ ] ✅ Campo Code-Standard incluido
- [ ] ✅ Tests ejecutados y pasando
- [ ] ✅ No modifiqué archivos deprecados
- [ ] ✅ Validador de estándares ejecutado

---

## 🔗 REFERENCIAS RÁPIDAS

- **Directiva completa**: `.workspace/URGENT_BROADCAST_CEO_CODE_STANDARDIZATION.md`
- **Resumen ejecutivo**: `.workspace/EXECUTIVE_SUMMARY_CODE_STANDARDIZATION.md`
- **Reglas globales**: `.workspace/SYSTEM_RULES.md`

---

## 📞 DUDAS O CONSULTAS

```bash
python .workspace/scripts/contact_responsible_agent.py code-standards "Tu consulta aquí"
```

---

**Cumplimiento obligatorio desde 2025-10-01**
**Revisión periódica cada commit**
