-- Script SQL para limpiar y crear usuarios específicos del proyecto
-- LIMPIAR USUARIOS EXISTENTES
DELETE FROM users;

-- CREAR USUARIOS ESPECÍFICOS CON TODOS LOS CAMPOS REQUERIDOS
-- Password hash para '123456': $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewdBNbnh9mu5Cc3C

-- Admin User
INSERT INTO users (
    id, email, password_hash, user_type, nombre, apellido, is_active, is_verified, 
    email_verified, phone_verified, reset_attempts, otp_attempts, cedula, telefono, 
    ciudad, empresa, direccion, created_at, updated_at
) VALUES (
    gen_random_uuid(), 'admin@mestore.com', 
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewdBNbnh9mu5Cc3C',
    'ADMIN', 'Admin', 'MeStore', true, true, true, false, 0, 0,
    '10000001', '123-456-7890', 'Bogotá', 'MeStore Demo', 'Dirección Demo Admin',
    NOW(), NOW()
);

-- Vendor User  
INSERT INTO users (
    id, email, password_hash, user_type, nombre, apellido, is_active, is_verified,
    email_verified, phone_verified, reset_attempts, otp_attempts, cedula, telefono,
    ciudad, empresa, direccion, created_at, updated_at
) VALUES (
    gen_random_uuid(), 'vendor@mestore.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewdBNbnh9mu5Cc3C',
    'VENDEDOR', 'Vendor', 'Demo', true, true, true, false, 0, 0,
    '10000002', '123-456-7891', 'Bogotá', 'MeStore Demo', 'Dirección Demo Vendor',
    NOW(), NOW()
);

-- Buyer User
INSERT INTO users (
    id, email, password_hash, user_type, nombre, apellido, is_active, is_verified,
    email_verified, phone_verified, reset_attempts, otp_attempts, cedula, telefono,
    ciudad, empresa, direccion, created_at, updated_at
) VALUES (
    gen_random_uuid(), 'buyer@mestore.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewdBNbnh9mu5Cc3C',
    'COMPRADOR', 'Buyer', 'Demo', true, true, true, false, 0, 0,
    '10000003', '123-456-7892', 'Bogotá', 'MeStore Demo', 'Dirección Demo Buyer',
    NOW(), NOW()
);

-- Super User
INSERT INTO users (
    id, email, password_hash, user_type, nombre, apellido, is_active, is_verified,
    email_verified, phone_verified, reset_attempts, otp_attempts, cedula, telefono,
    ciudad, empresa, direccion, created_at, updated_at
) VALUES (
    gen_random_uuid(), 'super@mestore.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewdBNbnh9mu5Cc3C', 
    'SUPERUSER', 'Super', 'Admin', true, true, true, false, 0, 0,
    '10000004', '123-456-7893', 'Bogotá', 'MeStore Demo', 'Dirección Demo Super',
    NOW(), NOW()
);

-- Verificar usuarios creados
SELECT 
    email, 
    user_type, 
    CONCAT(nombre, ' ', apellido) as full_name,
    is_active,
    is_verified,
    created_at::date as created
FROM users 
ORDER BY 
    CASE user_type 
        WHEN 'SUPERUSER' THEN 1 
        WHEN 'ADMIN' THEN 2 
        WHEN 'VENDEDOR' THEN 3 
        WHEN 'COMPRADOR' THEN 4 
    END;

\echo '✅ =========================================='
\echo '✅ USUARIOS CREADOS EXITOSAMENTE'
\echo '✅ =========================================='
\echo ''
\echo '🔐 CREDENCIALES DE ACCESO:'
\echo '   • super@mestore.com / 123456 (SuperUser)'
\echo '   • admin@mestore.com / 123456 (Admin)'
\echo '   • vendor@mestore.com / 123456 (Vendedor)'
\echo '   • buyer@mestore.com / 123456 (Comprador)'
\echo ''
\echo '🌐 URL: http://localhost:5174'
\echo '🗄️  Total usuarios en DB:'

SELECT COUNT(*) as total_usuarios FROM users;