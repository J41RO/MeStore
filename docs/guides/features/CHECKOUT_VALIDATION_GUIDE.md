# 🛒 GUÍA PASO A PASO: VALIDACIÓN DE CHECKOUT

**Fecha**: 2025-10-02
**Objetivo**: Validar que el sistema de pagos funciona correctamente después de los fixes
**Duración Estimada**: 10-15 minutos

---

## 🌐 INFORMACIÓN DE SERVICIOS

### ✅ Servicios Activos

**Backend API**:
- URL: http://192.168.1.137:8000
- Docs: http://192.168.1.137:8000/docs
- Status: ✅ OPERACIONAL
- Productos: 20 disponibles

**Frontend**:
- URL Principal: http://192.168.1.137:5173
- Status: ✅ OPERACIONAL
- Framework: React + Vite

---

## 📋 PASO 1: ACCEDER AL FRONTEND

### Acción:
Abre tu navegador y ve a:
```
http://192.168.1.137:5173
```

### Qué esperar ver:
- ✅ Landing page de MeStore
- ✅ Menú de navegación (Inicio, Productos, Carrito)
- ✅ Footer con información

### ⚠️ Si no funciona:
El puerto 5173 está ocupado. Hay múltiples instancias de Vite corriendo.

**Opciones**:
1. Intenta: http://192.168.1.137:5176 (puerto alternativo detectado)
2. O mata los procesos duplicados:
   ```bash
   pkill -f "vite.*5173"
   cd frontend
   npm run dev -- --host 192.168.1.137 --port 5173
   ```

---

## 📋 PASO 2: NAVEGAR A PRODUCTOS

### Acción:
1. En el menú principal, click en **"Productos"** o **"Catálogo"**
2. O navega directamente a: http://192.168.1.137:5173/products

### Qué esperar ver:
- ✅ Grid/lista de productos
- ✅ **20 productos** mostrados
- ✅ Cada producto debe mostrar:
  - Nombre
  - Precio (formato colombiano: $XXX,XXX)
  - Stock disponible
  - Imagen (si existe)
  - Botón "Agregar al Carrito" o "Ver Detalles"

### ✅ Validaciones:
- [ ] Se muestran los 20 productos
- [ ] Precios son visibles y tienen formato correcto
- [ ] Stock > 0 en todos los productos
- [ ] No hay errores en consola del navegador

### 🔍 Productos que deberías ver:
```
✅ SECADOR-PHILIPS-2300W: Secador de Pelo Philips 2300W - $185,000
✅ PERFUME-DIOR-100ML: Perfume Dior Sauvage 100ml - $450,000
✅ AUDIF-SONY-WH1000: Audífonos Sony WH-1000XM5 - Stock: 50
✅ LIBRO-SAPIENS: Libro: Sapiens de Yuval Noah Harari - Stock: 50
✅ YOGA-MAT-PRO: Tapete Yoga Profesional - Stock: 50
... (15 más)
```

### ⚠️ Si hay problemas:
- **No se muestran productos**: Verifica consola del navegador (F12)
- **Error de API**: Verifica que backend esté corriendo en puerto 8000
- **Stock = 0**: Ejecuta el fix de nuevo: `python scripts/fix_pending_products_auto.py`

---

## 📋 PASO 3: AGREGAR PRODUCTOS AL CARRITO

### Acción:
1. Selecciona **2-3 productos diferentes**
2. Click en **"Agregar al Carrito"** en cada uno
3. Observa el ícono del carrito en el menú superior

### Qué esperar ver:
- ✅ Badge/contador en ícono de carrito incrementa (1, 2, 3...)
- ✅ Mensaje de confirmación: "Producto agregado al carrito"
- ✅ Sin errores en consola

### ✅ Validaciones:
- [ ] Contador de carrito incrementa correctamente
- [ ] Notificación/toast de "Producto agregado"
- [ ] Puedes agregar el mismo producto múltiples veces
- [ ] No hay errores 400/500 en consola

### 💡 Recomendación:
Agrega productos de diferentes precios para probar cálculos:
- 1x Secador ($185,000)
- 2x Libro ($89,900 c/u)
- 1x Perfume ($450,000)

**Total esperado**: $814,800

---

## 📋 PASO 4: VER CARRITO

### Acción:
1. Click en el **ícono de carrito** en el menú
2. O navega a: http://192.168.1.137:5173/cart

### Qué esperar ver:
- ✅ Lista de productos agregados
- ✅ Cantidad de cada producto
- ✅ Precio unitario
- ✅ Subtotal por producto (cantidad × precio)
- ✅ **TOTAL del carrito** (suma exacta)
- ✅ Botones: +/- para cambiar cantidad
- ✅ Botón "Eliminar" por producto
- ✅ Botón "Proceder al Checkout" o "Finalizar Compra"

### ✅ Validaciones CRÍTICAS:
- [ ] Los precios se muestran correctamente
- [ ] El subtotal de cada item es correcto (cantidad × precio)
- [ ] El **TOTAL** es la suma exacta de todos los subtotales
- [ ] Puedes incrementar/decrementar cantidades
- [ ] Al cambiar cantidad, el subtotal y total se actualizan
- [ ] Puedes eliminar productos

### 🧮 Ejemplo de cálculo correcto:
```
Producto 1: Secador
  Cantidad: 1
  Precio unitario: $185,000
  Subtotal: $185,000

Producto 2: Libro
  Cantidad: 2
  Precio unitario: $89,900
  Subtotal: $179,800

Producto 3: Perfume
  Cantidad: 1
  Precio unitario: $450,000
  Subtotal: $450,000

─────────────────────────────
TOTAL: $814,800
```

### ⚠️ Si hay problemas:
- **Totales incorrectos**: El BUG #1 no se aplicó correctamente
- **Decimales extraños**: Verifica que backend use DECIMAL(10,2)
- **Carrito vacío**: LocalStorage o state management issue

---

## 📋 PASO 5: PROCEDER AL CHECKOUT

### Acción:
1. En la página del carrito, click **"Proceder al Checkout"**
2. O navega a: http://192.168.1.137:5173/checkout

### Qué esperar ver:
- ✅ Formulario de checkout con múltiples pasos:
  1. **Datos del comprador** (nombre, email, teléfono)
  2. **Dirección de envío** (dirección, ciudad, código postal)
  3. **Método de pago** (PayU, Wompi, Efecty, PSE)
  4. **Resumen de orden** (productos, total)

### ✅ Validaciones:
- [ ] Formulario se carga sin errores
- [ ] Campos requeridos están marcados
- [ ] Resumen de orden muestra productos correctos
- [ ] Total del resumen coincide con total del carrito
- [ ] Métodos de pago están disponibles

---

## 📋 PASO 6: LLENAR DATOS DEL COMPRADOR

### Acción:
Completa el formulario con datos de prueba:

```
Nombre: Juan Pérez Test
Email: juan.test@mestore.com
Teléfono: +57 300 123 4567
```

### ✅ Validaciones:
- [ ] Los campos aceptan el input
- [ ] Validación de formato de email funciona
- [ ] Validación de teléfono funciona
- [ ] Puedes avanzar al siguiente paso

---

## 📋 PASO 7: LLENAR DIRECCIÓN DE ENVÍO

### Acción:
Completa la dirección:

```
Dirección: Calle 123 #45-67
Ciudad: Bogotá
Departamento: Cundinamarca
Código Postal: 110111
País: Colombia
```

### ✅ Validaciones:
- [ ] Todos los campos se pueden llenar
- [ ] Validaciones de formato funcionan
- [ ] Puedes avanzar al siguiente paso

---

## 📋 PASO 8: SELECCIONAR MÉTODO DE PAGO

### Acción:
1. Selecciona un método de pago (ej: **PSE** o **PayU**)
2. Si es PSE, selecciona un banco de prueba
3. Click en **"Finalizar Compra"** o **"Pagar"**

### Qué esperar ver:
- ✅ Loading/spinner mientras se crea la orden
- ✅ **Redirección a página de confirmación** O
- ✅ **Redirección a pasarela de pago** (PayU/Wompi)

### ✅ Validaciones CRÍTICAS:
- [ ] **NO hay error 400** (Bad Request)
- [ ] **NO hay error 500** (Server Error)
- [ ] La orden se crea exitosamente
- [ ] Se muestra ID de orden generado
- [ ] Redirección funciona correctamente

### 🔍 Verificación en Backend:
Mientras haces esto, puedes verificar en backend que la orden se creó:

```bash
# Abrir una nueva terminal y ejecutar:
curl -s http://192.168.1.137:8000/api/v1/orders/ | python3 -m json.tool | tail -50
```

Deberías ver tu orden recién creada con:
- ✅ Status: "PENDING" o "CONFIRMED"
- ✅ Total correcto
- ✅ Items con cantidades correctas
- ✅ Buyer info correcta

---

## 📋 PASO 9: CONFIRMAR ORDEN CREADA

### Acción:
Después de "Finalizar Compra", verifica que llegaste a:
- Página de confirmación de orden, O
- Página de pago de PayU/Wompi

### Qué esperar ver (Página de Confirmación):
- ✅ Mensaje: "¡Orden creada exitosamente!"
- ✅ **Número de orden** (UUID)
- ✅ **Total pagado**
- ✅ **Estado de la orden**
- ✅ Detalles de productos comprados

### ✅ Validaciones:
- [ ] Orden tiene un ID válido
- [ ] Total mostrado es correcto
- [ ] Productos listados son correctos
- [ ] Estado inicial es apropiado (PENDING o CONFIRMED)

---

## 📋 PASO 10: VERIFICAR STOCK SE DECREMENTÓ

### Acción:
1. Vuelve a la página de productos
2. Busca los productos que compraste
3. Verifica el stock

### Qué esperar ver:
Si compraste:
- 1x Secador (stock inicial: 50)
  - **Stock nuevo**: 49 ✅

- 2x Libro (stock inicial: 50)
  - **Stock nuevo**: 48 ✅

### ✅ Validaciones:
- [ ] Stock se decrementó correctamente
- [ ] Decremento coincide con cantidad comprada
- [ ] Productos siguen disponibles (stock > 0)

### 🔍 Verificación en Backend:
```bash
# Verificar stock actual de un producto específico
curl -s http://192.168.1.137:8000/api/v1/products/ | \
  python3 -c "import sys,json; products=json.load(sys.stdin)['data']; \
  [print(f'{p[\"sku\"]}: Stock={p[\"stock\"]}') for p in products if 'SECADOR' in p['sku']]"
```

---

## 📋 PASO 11: VERIFICAR ORDEN EN BASE DE DATOS (OPCIONAL)

### Acción (Técnica):
Conectarte a la base de datos y verificar:

```bash
# Si usas SQLite:
sqlite3 app.db "SELECT id, buyer_email, total_amount, status FROM orders ORDER BY created_at DESC LIMIT 1;"

# O consulta la API:
curl -s "http://192.168.1.137:8000/api/v1/orders/" | python3 -m json.tool
```

### Qué esperar ver:
- ✅ Orden con email del comprador
- ✅ Total_amount es DECIMAL (no Float)
- ✅ Status apropiado
- ✅ Items asociados a la orden

---

## ✅ CHECKLIST FINAL DE VALIDACIÓN

### Sistema de Pagos:
- [ ] ✅ Backend responde en puerto 8000
- [ ] ✅ Frontend carga en puerto 5173
- [ ] ✅ 20 productos visibles con stock
- [ ] ✅ Productos se pueden agregar al carrito
- [ ] ✅ Carrito muestra totales correctos
- [ ] ✅ Checkout se puede iniciar
- [ ] ✅ Formularios de comprador y envío funcionan
- [ ] ✅ Métodos de pago están disponibles
- [ ] ✅ Orden se crea SIN errores 400/500
- [ ] ✅ Stock se decrementa correctamente

### Precisión Financiera:
- [ ] ✅ Precios se muestran correctamente
- [ ] ✅ Subtotales son exactos (cantidad × precio)
- [ ] ✅ Total del carrito es correcto
- [ ] ✅ Total de la orden coincide con carrito
- [ ] ✅ No hay decimales extraños (ej: 185000.00000001)

### Flujo Completo:
- [ ] ✅ Landing → Productos → Carrito → Checkout → Confirmación
- [ ] ✅ Sin errores en consola del navegador
- [ ] ✅ Sin errores 400/500 en API
- [ ] ✅ Redirecciones funcionan correctamente

---

## 🎯 RESULTADOS ESPERADOS

Si todo funciona correctamente:

✅ **Sistema de Pagos**: OPERACIONAL
✅ **Checkout Flow**: COMPLETO
✅ **Cálculos Financieros**: EXACTOS
✅ **Stock Management**: FUNCIONAL
✅ **Orden Creation**: EXITOSA

---

## ⚠️ PROBLEMAS COMUNES Y SOLUCIONES

### Error 400: Bad Request al crear orden
**Causa**: Posible validación fallando en backend
**Solución**: Verificar consola del navegador para ver detalles del error

### Totales incorrectos
**Causa**: BUG #1 no aplicado completamente
**Solución**: Re-ejecutar migrations:
```bash
cd /home/admin-jairo/MeStore
alembic upgrade head
```

### Stock no se decrementa
**Causa**: Lógica de inventario no activa
**Solución**: Verificar que el endpoint de crear orden actualice stock

### Productos no visibles
**Causa**: Estado PENDING no actualizado
**Solución**: Re-ejecutar:
```bash
python scripts/fix_pending_products_auto.py
```

---

## 📞 SIGUIENTE PASO DESPUÉS DE VALIDACIÓN

Si la validación es **EXITOSA** ✅:
1. Documentar resultados
2. Proceder con **Fase 2: BUG #3 (Race Condition)**
3. O continuar con **Dashboard Comprador**

Si hay **PROBLEMAS** ❌:
1. Documentar errores encontrados
2. Reportar a agentes responsables
3. Aplicar fixes adicionales

---

**Generado**: 2025-10-02
**By**: Master Orchestrator
**Version**: 1.0
