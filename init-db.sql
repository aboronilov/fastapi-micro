-- Database initialization script
-- This script runs when the PostgreSQL container starts for the first time

-- Create database if it doesn't exist (PostgreSQL creates it automatically from environment)
-- SELECT 'CREATE DATABASE fastapi_micro_db' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'fastapi_micro_db')\gexec

-- Grant privileges (if needed)
-- GRANT ALL PRIVILEGES ON DATABASE fastapi_micro_db TO postgres;

-- You can add any additional initialization SQL here
-- For example, creating extensions:
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Note: Tables will be created by Alembic migrations when the FastAPI app starts
