# Configuración Subdominio Admin MeStocker

## URLs Configuradas:
- admin.mestocker.com -> http://192.168.1.137:5173/admin-secure-portal
- mestocker.com -> Disponible para configuración futura

## Archivos Modificados:
- /etc/hosts: Resolución DNS local
- /etc/nginx/sites-available/admin-mestocker: Configuración nginx
- /etc/nginx/sites-enabled/admin-mestocker: Sitio activo
- ~/MeStore/frontend/vite.config.ts: allowedHosts configurado

## Credenciales Admin:
- Usuario: test@mestore.com
- Password: 123456

## Comandos de Mantenimiento:
```bash
# Verificar estado
sudo systemctl status nginx
curl -s -o /dev/null -w "%{http_code}" http://admin.mestocker.com

# Ver logs
sudo tail -f /var/log/nginx/admin-mestocker.access.log

# Recargar configuración
sudo nginx -t && sudo systemctl reload nginx
```