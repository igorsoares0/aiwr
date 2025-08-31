#!/bin/bash

echo "🚀 Starting Writify deployment..."

# Create database tables
echo "📊 Creating database tables..."
python create_tables.py

# Run database migrations (fallback)
echo "📋 Running database migrations..."
python run_migrations.py || echo "⚠️ Migrations failed or not needed"

# Initialize database with admin user
echo "👤 Initializing database..."
python init_database.py || echo "⚠️ Database already initialized"

echo "✅ Database setup complete!"

# Start the application
echo "🌐 Starting web application..."
exec gunicorn -w 4 -b 0.0.0.0:$PORT run:app