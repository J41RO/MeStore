# 🧪 CREDENCIALES DE TESTING - VENDEDOR DASHBOARD

## 🔐 Cuenta Vendedor Permanente

**Esta cuenta está siempre disponible para testing del Dashboard Vendor**

### Credenciales de Login:
- **URL de Login**: http://192.168.1.137:5173/login
- **Email**: `vendedor.test@mestore.com`
- **Password**: `VendorTest123!`

### Dashboard URL:
- **Dashboard Vendor**: http://192.168.1.137:5173/dashboard

## 👤 Información de la Cuenta

- **Nombre**: Vendedor Testing
- **Empresa**: TechStore Solutions S.A.S
- **Ciudad**: Medellín
- **Tipo**: VENDEDOR
- **Status**: ACTIVA y VERIFICADA
- **Permisos**: Acceso completo al Dashboard Vendor

## 📊 Funcionalidades Disponibles en el Dashboard

✅ **Métricas de Vendedor**:
- Total productos, ventas del mes, ingresos totales
- Órdenes pendientes y completadas
- Trending y cambios mes anterior

✅ **Productos Recientes**:
- TopProductsWidget integrado
- Enlaces a gestión de productos

✅ **Órdenes del Vendedor**:
- Lista de órdenes recientes con estados
- Métricas de órdenes (pendientes, procesando, completadas)
- Datos simulados desde backend API

✅ **Performance Summary**:
- Puntuación del vendedor
- Clientes únicos atendidos
- Tiempo promedio de entrega

✅ **Acciones Rápidas**:
- Nuevo producto
- Ver órdenes
- Mis productos
- Reportes

## 🔧 Scripts de Mantenimiento

Si necesitas verificar o recrear la cuenta:

```bash
# Verificar que la cuenta existe
python verify_vendor_account.py

# Recrear cuenta completa
python create_vendor_testing_account.py
```

## 📝 Notas Técnicas

- Cuenta pre-aprobada (vendor_status = approved)
- Email y teléfono pre-verificados
- Sin necesidad de OTP para login
- Información bancaria incluida para testing de comisiones
- Usuario ID: d076c76c-f13a-498d-9bfa-3c7f25b9ada3

---

**💡 Mantenido para siempre - Esta cuenta es permanente para testing**