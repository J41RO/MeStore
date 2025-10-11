-- ============================================================================
-- Migration: Add Email Verification Token Fields to Users Table
-- Database: PostgreSQL (Railway)
-- Date: 2025-10-11
-- Purpose: Agregar campos para verificación de email por token (link)
-- ============================================================================

-- IMPORTANTE: Ejecutar este script directamente en Railway PostgreSQL

BEGIN;

-- ===  CAMPOS PARA VERIFICACIÓN DE EMAIL POR TOKEN ===

-- Token de verificación de email (link clickeable)
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verification_token VARCHAR(100);
COMMENT ON COLUMN users.email_verification_token IS 'Token único de 32 bytes para verificación de email vía link';

-- Fecha de expiración del token (24 horas desde generación)
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verification_expires TIMESTAMP;
COMMENT ON COLUMN users.email_verification_expires IS 'Timestamp de expiración del token de verificación de email';

-- === ÍNDICE PARA OPTIMIZACIÓN DE BÚSQUEDAS ===

-- Índice para búsqueda rápida de tokens (usado en endpoint /verify-email?token=xxx)
CREATE INDEX IF NOT EXISTS idx_users_email_verification_token
ON users(email_verification_token)
WHERE email_verification_token IS NOT NULL;

COMMIT;

-- ============================================================================
-- VERIFICACIÓN POST-MIGRACIÓN
-- ============================================================================

-- Ejecutar esta query para verificar que los campos se crearon:
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'users'
AND column_name IN ('email_verification_token', 'email_verification_expires')
ORDER BY column_name;

-- Verificar índice:
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'users'
AND indexname = 'idx_users_email_verification_token';
