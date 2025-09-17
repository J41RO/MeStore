# 🔐 CREDENCIALES DEL SISTEMA - MESTORE

## 📋 **USUARIOS DISPONIBLES**

### 🛒 **COMPRADOR**
- **Email**: `buyer@mestore.com`
- **Password**: `123456` (por defecto)
- **Tipo**: COMPRADOR
- **Redirección**: `/app/dashboard` (BuyerDashboard)
- **Layout**: BuyerLayout
- **Permisos**: Compras, carrito, órdenes de compra

---

### 🏪 **VENDEDOR**  
- **Email**: `vendor@mestore.com`
- **Password**: `123456` (por defecto)
- **Tipo**: VENDEDOR
- **Redirección**: `/app/vendor-dashboard` (VendorDashboard)  
- **Layout**: DashboardLayout
- **Permisos**: Productos, órdenes de venta, comisiones, reportes

---

### ⚙️ **ADMINISTRADOR**
- **Email**: `admin@mestore.com`
- **Password**: `123456` (por defecto)
- **Tipo**: ADMIN
- **Redirección**: `/admin-secure-portal/dashboard` (AdminDashboard)
- **Layout**: AdminLayout
- **Permisos**: Gestión usuarios, órdenes, inventario, reportes admin

---

### 🔧 **SUPERUSUARIO**
- **Email**: `super@mestore.com`
- **Password**: `123456` (por defecto)
- **Tipo**: SUPERUSER
- **Redirección**: `/admin-secure-portal/dashboard` (AdminDashboard)
- **Layout**: AdminLayout  
- **Permisos**: Acceso completo, configuración sistema

---

## 🎯 **SISTEMA DE REDIRECCIÓN AUTOMÁTICA**

El componente `RoleBasedRedirect` en `/app` redirige automáticamente según el rol:

```typescript
switch (user.user_type) {
  case UserType.COMPRADOR:
    return <Navigate to="/app/dashboard" replace />;
    
  case UserType.VENDEDOR:
    return <Navigate to="/app/vendor-dashboard" replace />;
    
  case UserType.ADMIN:
  case UserType.SUPERUSER:
    return <Navigate to="/admin-secure-portal/dashboard" replace />;
    
  default:
    return <Navigate to="/marketplace/home" replace />;
}
```

## 🚀 **RUTAS DE ACCESO**

### **Entrada Principal**
- **Login**: `http://localhost:5173/login`
- **Después del login**: Redirección automática según rol

### **Compradores**
- Dashboard: `http://localhost:5173/app/dashboard`
- Marketplace: `http://localhost:5173/marketplace`
- Carrito: `http://localhost:5173/app/checkout`

### **Vendedores**
- Dashboard: `http://localhost:5173/app/vendor-dashboard`
- Productos: `http://localhost:5173/app/productos`
- Órdenes: `http://localhost:5173/app/ordenes`
- Comisiones: `http://localhost:5173/app/comisiones`

### **Administradores**
- Portal Admin: `http://localhost:5173/admin-secure-portal/dashboard`
- Usuarios: `http://localhost:5173/admin-secure-portal/users`
- Órdenes: `http://localhost:5173/admin-secure-portal/orders`
- Sistema: `http://localhost:5173/admin-secure-portal/system-config`

## ⚡ **VERIFICACIÓN RÁPIDA**

```bash
# Verificar usuarios en BD
python check_user_credentials.py

# Crear usuario de prueba
python scripts/create_test_user.py

# Verificar acceso específico
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "vendor@mestore.com", "password": "123456"}'
```

## 🛡️ **PROTECCIÓN DE RUTAS**

- **AuthGuard**: Protege todas las rutas `/app/*`
- **RoleGuard**: Controla acceso por rol específico
- **AdminGuard**: Solo ADMIN/SUPERUSER acceden a `/admin-secure-portal/*`

## 📝 **NOTAS IMPORTANTES**

1. **Contraseña por defecto**: `123456` para todos los usuarios de prueba
2. **Admin vs SuperUser**: Ambos acceden al mismo portal, pero SUPERUSER tiene más permisos
3. **Portal Admin**: Ruta separada `/admin-secure-portal/*` (futuro subdominio)
4. **Redirección automática**: Los usuarios van a su área correcta al hacer login

---

**💡 Mantenido automáticamente - Credenciales siempre disponibles para testing**