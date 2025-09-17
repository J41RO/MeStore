-- Create database and user setup for MeStore
-- Run this with: psql -U postgres -f setup_db.sql

-- Create user if not exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'test_user') THEN
        CREATE USER test_user WITH PASSWORD 'secure_test_pass_123';
    END IF;
END
$$;

-- Create database if not exists
SELECT 'CREATE DATABASE test_mestocker OWNER test_user'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'test_mestocker')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE test_mestocker TO test_user;

-- Connect to the database and grant schema privileges
\c test_mestocker

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO test_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO test_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO test_user;

-- Make test_user owner of public schema
ALTER SCHEMA public OWNER TO test_user;