-- Create additional databases for the application
-- Note: This script should only run during initial container setup

-- Ensure sdlc_user exists (it should be created by Podman environment variables)
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'sdlc_user') THEN
      
      CREATE ROLE sdlc_user LOGIN PASSWORD 'sdlc_password';
   END IF;
END
$do$;

-- Create databases with conditional logic to handle existing databases
-- Using psql conditional execution to avoid errors if databases already exist

-- Check and create sdlc_backlog_module database
SELECT 'CREATE DATABASE sdlc_backlog_module OWNER sdlc_user'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'sdlc_backlog_module')\gexec

-- Check and create sdlc_accelerator database  
SELECT 'CREATE DATABASE sdlc_accelerator OWNER sdlc_user'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'sdlc_accelerator')\gexec

-- Check and create n8n database
SELECT 'CREATE DATABASE n8n OWNER sdlc_user'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'n8n')\gexec

-- Grant all privileges to sdlc_user
GRANT ALL PRIVILEGES ON DATABASE sdlc_accelerator TO sdlc_user;
GRANT ALL PRIVILEGES ON DATABASE sdlc_backlog_module TO sdlc_user;
GRANT ALL PRIVILEGES ON DATABASE n8n TO sdlc_user;

-- Enable pgvector extension on main database
\c sdlc_accelerator;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;

-- Grant schema permissions
GRANT ALL ON SCHEMA public TO sdlc_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sdlc_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sdlc_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO sdlc_user;

-- Enable pgvector on sdlc_backlog_module database
\c sdlc_backlog_module;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;

-- Grant schema permissions
GRANT ALL ON SCHEMA public TO sdlc_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sdlc_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sdlc_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO sdlc_user;

-- Enable extensions on n8n database
\c n8n;
GRANT ALL ON SCHEMA public TO sdlc_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sdlc_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sdlc_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO sdlc_user;
