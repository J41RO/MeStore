# GUÍA DE MIGRACIÓN: Portal Admin a Subdomain

## RESUMEN EJECUTIVO
Este documento describe los pasos completos para migrar el portal admin oculto (`/admin-secure-portal`) a un subdomain dedicado (`admin.mestocker.com`) cuando se implemente hosting comercial.

## ESTADO ACTUAL
- **Ruta actual**: `http://192.168.1.137:5173/admin-secure-portal`
- **Implementación**: Portal oculto con funcionalidad completa
- **Seguridad**: AuthGuard protegido, credenciales específicas
- **Objetivo**: Migrar a `https://admin.mestocker.com`

## FASE 1: PREPARACIÓN DE DOMINIO

### 1.1 Registro de Dominio Principal
```bash
# Si no tienes dominio principal, registrar mestocker.com
# Proveedores recomendados: Namecheap, GoDaddy, Cloudflare
```

### 1.2 Configuración DNS
```dns
# Agregar registro A para subdomain admin
admin.mestocker.com    A    [IP_DEL_SERVIDOR]

# Registro CNAME alternativo (si usas CDN)
admin.mestocker.com    CNAME    mestocker.com
```

## FASE 2: CONFIGURACIÓN DE SERVIDOR

### 2.1 Nginx Virtual Host
```nginx
# /etc/nginx/sites-available/admin.mestocker.com
server {
    listen 80;
    listen [::]:80;
    server_name admin.mestocker.com;
    
    # Redirección HTTPS obligatoria
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name admin.mestocker.com;

    # Certificados SSL
    ssl_certificate /etc/letsencrypt/live/admin.mestocker.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/admin.mestocker.com/privkey.pem;
    
    # Configuración SSL moderna
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # Headers de seguridad
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    
    # Restricción de acceso por IP (opcional)
    # allow 192.168.1.0/24;
    # deny all;
    
    location / {
        proxy_pass http://127.0.0.1:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 2.2 Certificados SSL
```bash
# Instalar Certbot si no está instalado
sudo apt install certbot python3-certbot-nginx

# Generar certificado SSL
sudo certbot --nginx -d admin.mestocker.com

# Verificar auto-renovación
sudo certbot renew --dry-run
```

## FASE 3: MODIFICACIONES DE CÓDIGO

### 3.1 Configuración de Environment
```env
# .env.production
VITE_ADMIN_DOMAIN=https://admin.mestocker.com
VITE_MAIN_DOMAIN=https://mestocker.com
VITE_API_URL=https://api.mestocker.com
```

### 3.2 Modificaciones en App.tsx
```typescript
// Eliminar ruta admin-secure-portal del dominio principal
// En admin.mestocker.com usar estructura simplificada:

function AdminApp() {
  return (
    <ErrorBoundary>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route
          path="/*"
          element={
            <AuthGuard>
              <Suspense fallback={<PageLoader />}>
                <AdminLayout>
                  <Routes>
                    <Route path="dashboard" element={<AdminDashboard />} />
                    <Route path="users" element={<UserManagement />} />
                    <Route path="system-config" element={<SystemConfig />} />
                    <Route path="*" element={<Navigate to="/dashboard" replace />} />
                  </Routes>
                </AdminLayout>
              </Suspense>
            </AuthGuard>
          }
        />
      </Routes>
    </ErrorBoundary>
  );
}
```

### 3.3 Build Separado para Admin
```json
// package.json - Agregar script de build admin
{
  "scripts": {
    "build:admin": "vite build --mode admin",
    "build:main": "vite build --mode production"
  }
}
```

## FASE 4: CONFIGURACIÓN DE PRODUCCIÓN

### 4.1 Process Manager (PM2)
```bash
# pm2.config.js
module.exports = {
  apps: [
    {
      name: 'mestocker-main',
      script: 'npm',
      args: 'run preview',
      cwd: '/var/www/mestocker.com',
      env: {
        NODE_ENV: 'production',
        PORT: 5173
      }
    },
    {
      name: 'mestocker-admin',
      script: 'npm',
      args: 'run preview',
      cwd: '/var/www/admin.mestocker.com',
      env: {
        NODE_ENV: 'production',
        PORT: 5174
      }
    }
  ]
};
```

### 4.2 Separación de Builds
```bash
# Estructura de directorios en producción
/var/www/
├── mestocker.com/          # App principal
└── admin.mestocker.com/    # Portal admin exclusivo
```

## FASE 5: SEGURIDAD AVANZADA

### 5.1 Firewall UFW
```bash
# Configurar firewall
sudo ufw allow 22/tcp          # SSH
sudo ufw allow 80/tcp          # HTTP
sudo ufw allow 443/tcp         # HTTPS
sudo ufw enable

# Opcional: Restringir admin a IPs específicas
sudo ufw allow from 192.168.1.0/24 to any port 443
```

### 5.2 Fail2ban para Admin
```bash
# /etc/fail2ban/jail.local
[nginx-admin]
enabled = true
filter = nginx-admin
action = iptables[name=nginx-admin, port=https, protocol=tcp]
logpath = /var/log/nginx/admin.mestocker.com.access.log
maxretry = 3
bantime = 3600
```

## FASE 6: CHECKLIST DE MIGRACIÓN

### Pre-migración
- [ ] Dominio registrado y DNS configurado
- [ ] Certificados SSL generados
- [ ] Nginx configurado y testeado
- [ ] Build de admin separado creado
- [ ] Variables de entorno configuradas

### Durante migración
- [ ] Backup completo del sistema actual
- [ ] Deploy del build admin al subdomain
- [ ] Verificación de funcionamiento
- [ ] Actualización de links internos
- [ ] Notificación a usuarios admin

### Post-migración
- [ ] Monitoring activo del subdomain
- [ ] Verificación de certificados SSL
- [ ] Test de seguridad completo
- [ ] Documentación actualizada
- [ ] Eliminación de ruta oculta del main domain

## COMANDOS DE VERIFICACIÓN

### Verificar DNS
```bash
nslookup admin.mestocker.com
dig admin.mestocker.com
```

### Verificar SSL
```bash
openssl s_client -connect admin.mestocker.com:443
curl -I https://admin.mestocker.com
```

### Verificar Nginx
```bash
sudo nginx -t
sudo systemctl reload nginx
```

## CONSIDERACIONES IMPORTANTES

1. **Tiempo de DNS**: Los cambios DNS pueden tomar 24-48 horas en propagarse
2. **Certificados**: Renovar automáticamente cada 90 días
3. **Backups**: Mantener backups antes de cualquier cambio
4. **Testing**: Probar en ambiente staging antes de producción
5. **Monitoreo**: Implementar alertas para el subdomain admin

## ROLLBACK PLAN

En caso de problemas:
```bash
# 1. Restaurar configuración anterior de Nginx
sudo cp /etc/nginx/sites-available/mestocker.com.backup /etc/nginx/sites-available/mestocker.com

# 2. Reactivar ruta admin-secure-portal en main domain
# 3. Actualizar DNS si es necesario
# 4. Notificar a usuarios del cambio temporal
```

---

**AUTOR**: IA Desarrolladora Universal Expert  
**FECHA**: 2025-09-07  
**VERSIÓN**: 1.0  
**ESTADO**: Portal oculto implementado, listo para migración