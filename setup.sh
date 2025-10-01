#!/bin/bash

# Modern Geospatial Data Management Application Setup Script
echo "🌍 Setting up Modern Geospatial Data Management Application..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js v16 or higher."
    exit 1
fi

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed. Please install PostgreSQL v12 or higher."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    echo "❌ Node.js version 16 or higher is required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Install root dependencies
echo "📦 Installing root dependencies..."
npm install

# Install client dependencies
echo "📦 Installing client dependencies..."
cd client
npm install
cd ..

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your database credentials"
fi

# Database setup
echo "🗄️  Setting up database..."

# Check if database exists
DB_NAME="geospatial_db"
if psql -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
    echo "✅ Database '$DB_NAME' already exists"
else
    echo "📊 Creating database '$DB_NAME'..."
    createdb $DB_NAME
fi

# Enable PostGIS extension
echo "🗺️  Enabling PostGIS extension..."
psql -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS postgis;" 2>/dev/null || echo "⚠️  PostGIS extension setup may require additional configuration"

# Run database initialization
echo "📋 Running database initialization..."
if [ -f server/scripts/init-db.sql ]; then
    psql -d $DB_NAME -f server/scripts/init-db.sql
    echo "✅ Database initialized with sample data"
else
    echo "⚠️  Database initialization script not found"
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your database credentials"
echo "2. Run 'npm run dev' to start the application"
echo "3. Open http://localhost:3000 in your browser"
echo ""
echo "🔧 Available commands:"
echo "  npm run dev      - Start development server"
echo "  npm run build    - Build for production"
echo "  npm run server   - Start backend only"
echo "  npm run client   - Start frontend only"
echo ""
echo "📚 For more information, see README.md"
