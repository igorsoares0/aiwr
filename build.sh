#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python run_migrations.py

# Initialize database if needed (only on first deploy)
python init_database.py || echo "Database already initialized"