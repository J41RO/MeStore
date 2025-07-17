# ~/frontend/Dockerfile
# ---------------------------------------------------------------------------------------------
# MESTOCKER - Frontend Docker Configuration
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: Dockerfile
# Ruta: ~/frontend/Dockerfile
# Autor: Jairo
# Fecha de Creación: 2025-07-17
# Última Actualización: 2025-07-17
# Versión: 1.0.0
# Propósito: Containerizar frontend React/TypeScript con Nginx
#            Multi-stage build para optimización de producción
#
# Modificaciones:
# 2025-07-17 - Configuración inicial Docker multi-stage
#
# ---------------------------------------------------------------------------------------------

# ===== STAGE 1: BUILD =====
FROM node:20-alpine AS builder

# Metadatos
LABEL stage="builder"
LABEL description="MeStore Frontend Builder Stage"

# Directorio de trabajo
WORKDIR /usr/src/app

# Copiar archivos de dependencias primero (cache de Docker)
COPY package*.json ./

# Instalar dependencias (usando ci para builds reproducibles)
RUN npm ci --only=production

# Copiar código fuente
COPY . .

# Build de producción optimizado
RUN npm run build

# ===== STAGE 2: PRODUCTION =====
FROM nginx:stable-alpine AS production

# Metadatos
LABEL maintainer="jairo.colina.co@gmail.com"
LABEL description="MeStore Frontend - Production Ready"
LABEL version="1.0.0"

# Copiar build desde stage anterior
COPY --from=builder /usr/src/app/dist /usr/share/nginx/html

# Copiar configuración nginx personalizada (la crearemos después)
COPY nginx.conf /etc/nginx/nginx.conf

# Crear usuario nginx no-root
RUN addgroup -g 1001 -S nginx && \
    adduser -S -D -H -u 1001 -h /var/cache/nginx -s /sbin/nologin -G nginx -g nginx nginx

# Cambiar ownership de directorios necesarios
RUN chown -R nginx:nginx /usr/share/nginx/html \
    && chown -R nginx:nginx /var/cache/nginx \
    && chown -R nginx:nginx /etc/nginx

# Exponer puerto
EXPOSE 80

# Usuario no-root
USER nginx

# Comando de inicio
CMD ["nginx", "-g", "daemon off;"]
