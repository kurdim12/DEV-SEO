-- Create devseo user
CREATE USER devseo WITH PASSWORD 'devseo_dev_pass';

-- Create devseo database
CREATE DATABASE devseo OWNER devseo;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE devseo TO devseo;
