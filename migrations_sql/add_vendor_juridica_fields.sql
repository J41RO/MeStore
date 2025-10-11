-- ============================================================================
-- Migration: Add Persona Jurídica Fields to Users Table
-- Database: PostgreSQL (Railway)
-- Date: 2025-10-11
-- Purpose: Agregar campos específicos para registro de Persona Jurídica
-- ============================================================================

-- IMPORTANTE: Ejecutar este script directamente en Railway PostgreSQL
-- después de verificar qué campos ya existen

BEGIN;

-- === CAMPOS PARA PERSONA JURÍDICA ===

-- Razón Social (nombre legal de la empresa)
ALTER TABLE users ADD COLUMN IF NOT EXISTS razon_social VARCHAR(200);
COMMENT ON COLUMN users.razon_social IS 'Razón social de la empresa (Persona Jurídica)';

-- Nombre Comercial (puede ser diferente a razón social)
ALTER TABLE users ADD COLUMN IF NOT EXISTS nombre_comercial VARCHAR(200);
COMMENT ON COLUMN users.nombre_comercial IS 'Nombre comercial del negocio';

-- NIT (identificación tributaria de la empresa)
ALTER TABLE users ADD COLUMN IF NOT EXISTS nit VARCHAR(20) UNIQUE;
COMMENT ON COLUMN users.nit IS 'NIT de la empresa (formato: 123456789-0)';

-- Representante Legal
ALTER TABLE users ADD COLUMN IF NOT EXISTS representante_legal VARCHAR(100);
COMMENT ON COLUMN users.representante_legal IS 'Nombre completo del representante legal';

-- Cédula del Representante
ALTER TABLE users ADD COLUMN IF NOT EXISTS cedula_representante VARCHAR(20);
COMMENT ON COLUMN users.cedula_representante IS 'Cédula del representante legal';

-- Email del Representante
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_representante VARCHAR(255);
COMMENT ON COLUMN users.email_representante IS 'Email del representante legal';

-- Teléfono de la Empresa
ALTER TABLE users ADD COLUMN IF NOT EXISTS telefono_empresa VARCHAR(20);
COMMENT ON COLUMN users.telefono_empresa IS 'Teléfono corporativo de la empresa';

-- === CAMPOS PARA AMBOS TIPOS DE VENDOR (Natural y Jurídica) ===

-- Dirección Fiscal
ALTER TABLE users ADD COLUMN IF NOT EXISTS direccion_fiscal VARCHAR(300);
COMMENT ON COLUMN users.direccion_fiscal IS 'Dirección fiscal del vendedor';

-- Ciudad Fiscal
ALTER TABLE users ADD COLUMN IF NOT EXISTS ciudad_fiscal VARCHAR(100);
COMMENT ON COLUMN users.ciudad_fiscal IS 'Ciudad fiscal';

-- Departamento Fiscal
ALTER TABLE users ADD COLUMN IF NOT EXISTS departamento_fiscal VARCHAR(100);
COMMENT ON COLUMN users.departamento_fiscal IS 'Departamento fiscal';

-- Departamento de Residencia
ALTER TABLE users ADD COLUMN IF NOT EXISTS departamento VARCHAR(100);
COMMENT ON COLUMN users.departamento IS 'Departamento de residencia';

-- Código Postal
ALTER TABLE users ADD COLUMN IF NOT EXISTS codigo_postal VARCHAR(10);
COMMENT ON COLUMN users.codigo_postal IS 'Código postal colombiano';

-- Tipo de Vendedor
ALTER TABLE users ADD COLUMN IF NOT EXISTS tipo_vendedor VARCHAR(20);
COMMENT ON COLUMN users.tipo_vendedor IS 'Tipo de vendedor: persona_natural o persona_juridica';

-- === ÍNDICES PARA OPTIMIZACIÓN ===

-- Índice para búsqueda por NIT
CREATE INDEX IF NOT EXISTS idx_users_nit ON users(nit) WHERE nit IS NOT NULL;

-- Índice para búsqueda por tipo de vendedor
CREATE INDEX IF NOT EXISTS idx_users_tipo_vendedor ON users(tipo_vendedor) WHERE tipo_vendedor IS NOT NULL;

-- Índice compuesto para vendors por tipo y estado
CREATE INDEX IF NOT EXISTS idx_users_vendor_type_status
ON users(user_type, vendor_status, tipo_vendedor)
WHERE user_type = 'VENDOR';

COMMIT;

-- ============================================================================
-- VERIFICACIÓN POST-MIGRACIÓN
-- ============================================================================

-- Ejecutar esta query para verificar que los campos se crearon:
-- SELECT column_name, data_type, is_nullable
-- FROM information_schema.columns
-- WHERE table_name = 'users'
-- AND column_name IN (
--   'razon_social', 'nombre_comercial', 'nit', 'representante_legal',
--   'cedula_representante', 'email_representante', 'telefono_empresa',
--   'direccion_fiscal', 'ciudad_fiscal', 'departamento_fiscal',
--   'departamento', 'tipo_vendedor'
-- )
-- ORDER BY column_name;
