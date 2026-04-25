-- Connect to your database and run these commands as the master/admin user

-- Grant all privileges on the database
GRANT ALL PRIVILEGES ON DATABASE vidharthi_store TO vidharthi_user;

-- Grant schema permissions
GRANT USAGE, CREATE ON SCHEMA public TO vidharthi_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO vidharthi_user;

-- Grant default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO vidharthi_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO vidharthi_user;

-- Grant permissions on all existing tables (if any)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO vidharthi_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO vidharthi_user;
