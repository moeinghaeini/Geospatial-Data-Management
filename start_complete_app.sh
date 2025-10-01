#!/bin/bash

# Complete Italy Geospatial Explorer Startup Script
# Starts both Node.js and Python applications with full integration

echo "🏛️ Starting Italy Geospatial Explorer - Complete Application"
echo "=============================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "package.json" ] || [ ! -d "python" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Check prerequisites
print_info "Checking prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js v16 or higher."
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    print_error "Node.js version 16 or higher is required. Current version: $(node -v)"
    exit 1
fi
print_status "Node.js $(node -v) is available"

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [ "$(echo "$PYTHON_VERSION < 3.8" | bc -l)" -eq 1 ]; then
    print_error "Python 3.8 or higher is required. Current version: $PYTHON_VERSION"
    exit 1
fi
print_status "Python $PYTHON_VERSION is available"

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    print_error "PostgreSQL is not installed. Please install PostgreSQL v12 or higher."
    exit 1
fi
print_status "PostgreSQL is available"

# Check if PostgreSQL is running
if ! pg_isready -q; then
    print_error "PostgreSQL is not running. Please start PostgreSQL service."
    exit 1
fi
print_status "PostgreSQL is running"

# Install Node.js dependencies
print_info "Installing Node.js dependencies..."
if npm install; then
    print_status "Node.js dependencies installed"
else
    print_error "Failed to install Node.js dependencies"
    exit 1
fi

# Install client dependencies
print_info "Installing client dependencies..."
cd client
if npm install; then
    print_status "Client dependencies installed"
else
    print_error "Failed to install client dependencies"
    exit 1
fi
cd ..

# Install Python dependencies
print_info "Installing Python dependencies..."
cd python
if pip3 install -r requirements.txt; then
    print_status "Python dependencies installed"
else
    print_error "Failed to install Python dependencies"
    exit 1
fi
cd ..

# Set up environment variables
print_info "Setting up environment variables..."
if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        cp env.example .env
        print_status "Environment file created from example"
        print_warning "Please edit .env file with your database credentials"
    else
        print_warning "No .env file found. Using default values."
    fi
fi

# Create necessary directories
print_info "Creating necessary directories..."
mkdir -p logs
mkdir -p output
mkdir -p python/output
mkdir -p python/models
mkdir -p python/logs
print_status "Directories created"

# Database setup
print_info "Setting up database..."

# Check if database exists
DB_NAME="geospatial_db"
if psql -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
    print_status "Database '$DB_NAME' already exists"
else
    print_info "Creating database '$DB_NAME'..."
    if createdb $DB_NAME; then
        print_status "Database created successfully"
    else
        print_error "Failed to create database"
        exit 1
    fi
fi

# Enable PostGIS extension
print_info "Enabling PostGIS extension..."
if psql -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS postgis;" 2>/dev/null; then
    print_status "PostGIS extension enabled"
else
    print_warning "PostGIS extension setup may require additional configuration"
fi

# Run database initialization
print_info "Running database initialization..."
if [ -f "server/scripts/init-db.sql" ]; then
    if psql -d $DB_NAME -f server/scripts/init-db.sql; then
        print_status "Database initialized with sample data"
    else
        print_warning "Database initialization script had issues"
    fi
else
    print_warning "Database initialization script not found"
fi

# Start Python application in background
print_info "Starting Python application..."
cd python
python3 start_app.py &
PYTHON_PID=$!
cd ..

# Wait for Python application to start
print_info "Waiting for Python application to start..."
sleep 10

# Check if Python application is running
if curl -s http://localhost:8000/api/health > /dev/null; then
    print_status "Python application is running on port 8000"
else
    print_warning "Python application may not be fully started yet"
fi

# Start Node.js application
print_info "Starting Node.js application..."
npm run dev &
NODE_PID=$!

# Wait for Node.js application to start
print_info "Waiting for Node.js application to start..."
sleep 5

# Check if Node.js application is running
if curl -s http://localhost:5001/api/health > /dev/null; then
    print_status "Node.js application is running on port 5001"
else
    print_warning "Node.js application may not be fully started yet"
fi

# Start React client
print_info "Starting React client..."
cd client
npm start &
CLIENT_PID=$!
cd ..

# Wait for React client to start
print_info "Waiting for React client to start..."
sleep 10

# Display application information
echo ""
echo "=============================================================="
echo "🎉 Italy Geospatial Explorer - Complete Application Started!"
echo "=============================================================="
echo ""
echo "📱 Frontend (React):     http://localhost:3000"
echo "🔧 Backend (Node.js):   http://localhost:5001"
echo "🐍 Python API:          http://localhost:8000"
echo "📚 Python API Docs:     http://localhost:8000/docs"
echo "🔧 Python ReDoc:        http://localhost:8000/redoc"
echo ""
echo "🔌 WebSocket (Python):  ws://localhost:8000/ws"
echo ""
echo "📋 Available Features:"
echo "  ✅ Interactive Mapping with Leaflet"
echo "  ✅ Advanced Spatial Analysis (Python)"
echo "  ✅ Machine Learning Models (Python)"
echo "  ✅ Real-time WebSocket Updates"
echo "  ✅ Data Import/Export"
echo "  ✅ Comprehensive API"
echo "  ✅ Database Integration"
echo "  ✅ Advanced Visualizations"
echo ""
echo "🛑 To stop the application, press Ctrl+C"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    print_info "Stopping applications..."
    
    if [ ! -z "$PYTHON_PID" ]; then
        kill $PYTHON_PID 2>/dev/null
        print_status "Python application stopped"
    fi
    
    if [ ! -z "$NODE_PID" ]; then
        kill $NODE_PID 2>/dev/null
        print_status "Node.js application stopped"
    fi
    
    if [ ! -z "$CLIENT_PID" ]; then
        kill $CLIENT_PID 2>/dev/null
        print_status "React client stopped"
    fi
    
    print_status "All applications stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Keep the script running
print_info "Applications are running. Press Ctrl+C to stop."
wait
