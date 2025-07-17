# ~/Dockerfile
# ---------------------------------------------------------------------------------------------
# MESTOCKER - Backend Docker Configuration
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: Dockerfile
# Ruta: ~/Dockerfile
# Autor: Jairo
# Fecha de Creación: 2025-07-17
# Última Actualización: 2025-07-17
# Versión: 1.0.0
# Propósito: Containerizar backend Python/FastAPI para desarrollo
#            Configuración optimizada para hot-reload y debugging
#
# Modificaciones:
# 2025-07-17 - Configuración inicial Docker para desarrollo
#
# ---------------------------------------------------------------------------------------------

# Base image con Python optimizado
FROM python:3.11-slim

# Metadatos del container
LABEL maintainer="jairo.colina.co@gmail.com"
LABEL description="MeStore Backend - FastAPI Development Container"
LABEL version="1.0.0"

# Directorio de trabajo en el container
WORKDIR /app

# Variables de entorno para Python
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ENVIRONMENT=development
ENV PYTHONPATH=/app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivo de dependencias primero (para cache de Docker)
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

# Exponer puerto de desarrollo
EXPOSE 8000

# Comando para desarrollo con hot-reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "info"]
