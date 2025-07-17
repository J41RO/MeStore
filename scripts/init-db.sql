-- MeStore Database Initialization Script
-- Ejecutado automáticamente al crear el container de PostgreSQL

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Configuraciones de base de datos
ALTER DATABASE mestocker_dev SET timezone TO 'UTC';

-- Mensaje de confirmación
SELECT 'MeStore Database initialized successfully!' AS status;
