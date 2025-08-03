-- Database initialization script for MRDPOL Core
-- This script will be executed when the PostgreSQL container starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create custom types
DO $$ BEGIN
    CREATE TYPE user_role_type AS ENUM ('admin', 'manager', 'user', 'viewer');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE task_status_type AS ENUM ('new', 'in_progress', 'pending_review', 'needs_revision', 'completed', 'canceled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE task_priority_type AS ENUM ('low', 'medium', 'high', 'urgent');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create database schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS mrdpol_core;

-- Set default search path
ALTER DATABASE mrdpol_core_db SET search_path TO mrdpol_core, public;

-- Create a function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Grant privileges to the application user
GRANT ALL PRIVILEGES ON DATABASE mrdpol_core_db TO mrdpol_user;
GRANT ALL ON SCHEMA mrdpol_core TO mrdpol_user;
GRANT ALL ON SCHEMA public TO mrdpol_user;

-- Create initial admin user (will be handled by alembic migrations)
-- This is just a placeholder for the initialization process
