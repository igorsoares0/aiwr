#!/bin/bash

# Run database migrations
echo "Running database migrations..."
python run_migrations.py

# Initialize database if needed
echo "Initializing database..."
python init_database.py

# Start the application
echo "Starting application..."
exec gunicorn -w 4 -b 0.0.0.0:$PORT run:app