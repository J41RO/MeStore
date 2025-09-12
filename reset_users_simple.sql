-- Script SQL para limpiar y crear usuarios específicos del proyecto
-- 
-- LIMPIAR USUARIOS EXISTENTES
DELETE FROM users;

-- CREAR USUARIOS ESPECÍFICOS
-- Nota: Los passwords están hasheados con bcrypt con salt rounds 12

-- Admin User: admin@mestore.com / 123456
INSERT INTO users (
    id, 
    email, 
    password_hash, 
    user_type, 
    nombre, 
    apellido, 
    is_active, 
    is_verified, 
    email_verified, 
    phone_verified,
    reset_attempts,
    otp_attempts,
    cedula, 
    telefono, 
    ciudad, 
    empresa, 
    direccion, 
    created_at, 
    updated_at
) VALUES (
    gen_random_uuid(),
    'admin@mestore.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewdBNbnh9mu5Cc3C', -- password: 123456
    'ADMIN',
    'Admin',
    'MeStore',
    true,
    true,
    true,
    false,
    0,
    0,
    '10000001',
    '123-456-7890',
    'Bogotá',
    'MeStore Demo',
    'Dirección Demo Admin',
    NOW(),
    NOW()
);

-- Vendor User: vendor@mestore.com / 123456
INSERT INTO users (
    id, 
    email, 
    password_hash, 
    user_type, 
    nombre, 
    apellido, 
    is_active, 
    is_verified, 
    email_verified, 
    cedula, 
    telefono, 
    ciudad, 
    empresa, 
    direccion, 
    created_at, 
    updated_at
) VALUES (
    gen_random_uuid(),
    'vendor@mestore.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewdBNbnh9mu5Cc3C', -- password: 123456
    'VENDEDOR',
    'Vendor',
    'Demo',
    true,
    true,
    true,
    '10000002',
    '123-456-7891',
    'Bogotá',
    'MeStore Demo',
    'Dirección Demo Vendor',
    NOW(),
    NOW()
);

-- Buyer User: buyer@mestore.com / 123456  
INSERT INTO users (
    id, 
    email, 
    password_hash, 
    user_type, 
    nombre, 
    apellido, 
    is_active, 
    is_verified, 
    email_verified, 
    cedula, 
    telefono, 
    ciudad, 
    empresa, 
    direccion, 
    created_at, 
    updated_at
) VALUES (
    gen_random_uuid(),
    'buyer@mestore.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewdBNbnh9mu5Cc3C', -- password: 123456
    'COMPRADOR',
    'Buyer',
    'Demo',
    true,
    true,
    true,
    '10000003',
    '123-456-7892',
    'Bogotá',
    'MeStore Demo',
    'Dirección Demo Buyer',
    NOW(),
    NOW()
);

-- Super User: super@mestore.com / 123456
INSERT INTO users (
    id, 
    email, 
    password_hash, 
    user_type, 
    nombre, 
    apellido, 
    is_active, 
    is_verified, 
    email_verified, 
    cedula, 
    telefono, 
    ciudad, 
    empresa, 
    direccion, 
    created_at, 
    updated_at
) VALUES (
    gen_random_uuid(),
    'super@mestore.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewdBNbnh9mu5Cc3C', -- password: 123456
    'SUPERUSER',
    'Super',
    'Admin',
    true,
    true,
    true,
    '10000004',
    '123-456-7893',
    'Bogotá',
    'MeStore Demo',
    'Dirección Demo Super',
    NOW(),
    NOW()
);

-- Verificar usuarios creados
SELECT 
    email, 
    user_type, 
    CONCAT(nombre, ' ', apellido) as full_name,
    is_active,
    is_verified,
    created_at
FROM users 
ORDER BY user_type;

\echo '✅ USUARIOS CREADOS EXITOSAMENTE'
\echo '🔐 CREDENCIALES:'
\echo '   • admin@mestore.com / 123456 (Admin)'
\echo '   • vendor@mestore.com / 123456 (Vendedor)'
\echo '   • buyer@mestore.com / 123456 (Comprador)'
\echo '   • super@mestore.com / 123456 (SuperUser)'