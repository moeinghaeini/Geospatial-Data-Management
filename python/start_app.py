#!/usr/bin/env python3
"""
Startup Script for Italy Geospatial Explorer - Complete Python Application
Handles environment setup, dependency checking, and application startup
"""

import os
import sys
import subprocess
import json
import time
import logging
from pathlib import Path
from datetime import datetime
import uvicorn
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AppStarter:
    """
    Application startup and configuration manager
    """
    
    def __init__(self):
        """Initialize the app starter"""
        self.app_dir = Path(__file__).parent
        self.config = self.load_config()
        self.setup_environment()
    
    def load_config(self):
        """Load application configuration"""
        config_file = self.app_dir / "config.json"
        
        default_config = {
            "app": {
                "name": "Italy Geospatial Explorer",
                "version": "2.0.0",
                "host": "0.0.0.0",
                "port": 8000,
                "debug": True
            },
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "geospatial_db",
                "user": "postgres",
                "password": "password"
            },
            "features": {
                "websocket": True,
                "ml_models": True,
                "real_time_analysis": True,
                "data_import": True,
                "advanced_visualization": True
            },
            "output": {
                "directory": "output",
                "formats": ["html", "png", "json", "geojson"]
            }
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                logger.info("✅ Configuration loaded from config.json")
                return config
            except Exception as e:
                logger.warning(f"⚠️ Failed to load config.json: {e}")
        
        # Create default config file
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        logger.info("✅ Default configuration created")
        
        return default_config
    
    def setup_environment(self):
        """Setup application environment"""
        try:
            # Load environment variables
            load_dotenv()
            
            # Create necessary directories
            directories = [
                "output",
                "models", 
                "logs",
                "data",
                "temp"
            ]
            
            for directory in directories:
                dir_path = self.app_dir / directory
                dir_path.mkdir(exist_ok=True)
                logger.info(f"✅ Directory created/verified: {directory}")
            
            # Set environment variables
            os.environ['PYTHONPATH'] = str(self.app_dir)
            os.environ['GEOSPATIAL_APP_DIR'] = str(self.app_dir)
            
            logger.info("✅ Environment setup completed")
            
        except Exception as e:
            logger.error(f"❌ Environment setup failed: {e}")
            raise
    
    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        logger.info("🔍 Checking dependencies...")
        
        required_packages = [
            'fastapi', 'uvicorn', 'psycopg2-binary', 'geopandas', 
            'shapely', 'folium', 'plotly', 'matplotlib', 'seaborn',
            'scikit-learn', 'pandas', 'numpy'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                logger.info(f"✅ {package} is available")
            except ImportError:
                missing_packages.append(package)
                logger.warning(f"⚠️ {package} is missing")
        
        if missing_packages:
            logger.error(f"❌ Missing packages: {', '.join(missing_packages)}")
            logger.info("💡 Install missing packages with: pip install -r requirements.txt")
            return False
        
        logger.info("✅ All dependencies are available")
        return True
    
    def check_database_connection(self):
        """Check database connection"""
        logger.info("🗄️ Checking database connection...")
        
        try:
            import psycopg2
            
            conn_params = {
                'host': self.config['database']['host'],
                'port': self.config['database']['port'],
                'database': self.config['database']['name'],
                'user': self.config['database']['user'],
                'password': self.config['database']['password']
            }
            
            conn = psycopg2.connect(**conn_params)
            conn.close()
            
            logger.info("✅ Database connection successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            logger.info("💡 Make sure PostgreSQL is running and credentials are correct")
            return False
    
    def initialize_database(self):
        """Initialize database schema"""
        logger.info("🗄️ Initializing database schema...")
        
        try:
            from database_integration import DatabaseIntegration
            
            db = DatabaseIntegration({
                'host': self.config['database']['host'],
                'port': self.config['database']['port'],
                'database': self.config['database']['name'],
                'user': self.config['database']['user'],
                'password': self.config['database']['password']
            })
            
            db.initialize_database()
            db.close()
            
            logger.info("✅ Database schema initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            return False
    
    def start_application(self):
        """Start the FastAPI application"""
        logger.info("🚀 Starting Italy Geospatial Explorer...")
        
        try:
            # Application configuration
            app_config = {
                'app': 'app:app',
                'host': self.config['app']['host'],
                'port': self.config['app']['port'],
                'reload': self.config['app']['debug'],
                'log_level': 'info',
                'access_log': True
            }
            
            logger.info(f"🌐 Application will be available at: http://{app_config['host']}:{app_config['port']}")
            logger.info(f"📚 API Documentation: http://{app_config['host']}:{app_config['port']}/docs")
            logger.info(f"🔧 ReDoc Documentation: http://{app_config['host']}:{app_config['port']}/redoc")
            
            # Start the application
            uvicorn.run(**app_config)
            
        except Exception as e:
            logger.error(f"❌ Failed to start application: {e}")
            raise
    
    def run_health_check(self):
        """Run application health check"""
        logger.info("🏥 Running health check...")
        
        try:
            import requests
            import time
            
            # Wait for application to start
            time.sleep(5)
            
            # Check health endpoint
            response = requests.get(f"http://{self.config['app']['host']}:{self.config['app']['port']}/api/health")
            
            if response.status_code == 200:
                health_data = response.json()
                logger.info(f"✅ Health check passed: {health_data['status']}")
                logger.info(f"📊 Database status: {health_data.get('database', 'unknown')}")
                logger.info(f"🔗 Active connections: {health_data.get('active_connections', 0)}")
                return True
            else:
                logger.error(f"❌ Health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return False
    
    def print_startup_info(self):
        """Print startup information"""
        print("\n" + "="*60)
        print("🏛️ Italy Geospatial Explorer - Complete Application")
        print("="*60)
        print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Application URL: http://{self.config['app']['host']}:{self.config['app']['port']}")
        print(f"📚 API Documentation: http://{self.config['app']['host']}:{self.config['app']['port']}/docs")
        print(f"🔧 ReDoc Documentation: http://{self.config['app']['host']}:{self.config['app']['port']}/redoc")
        print(f"🔌 WebSocket: ws://{self.config['app']['host']}:{self.config['app']['port']}/ws")
        print("\n📋 Available Features:")
        print("  ✅ Interactive Mapping with Folium")
        print("  ✅ Advanced Spatial Analysis")
        print("  ✅ Machine Learning Models")
        print("  ✅ Real-time WebSocket Updates")
        print("  ✅ Data Import/Export")
        print("  ✅ Comprehensive API")
        print("  ✅ Database Integration")
        print("  ✅ Advanced Visualizations")
        print("\n🎯 Ready to explore Italy's geospatial data!")
        print("="*60 + "\n")
    
    def run(self):
        """Run the complete application startup process"""
        try:
            logger.info("🚀 Starting Italy Geospatial Explorer...")
            
            # Check dependencies
            if not self.check_dependencies():
                logger.error("❌ Dependency check failed. Please install missing packages.")
                sys.exit(1)
            
            # Check database connection
            if not self.check_database_connection():
                logger.error("❌ Database connection failed. Please check your database configuration.")
                sys.exit(1)
            
            # Initialize database
            if not self.initialize_database():
                logger.error("❌ Database initialization failed.")
                sys.exit(1)
            
            # Print startup information
            self.print_startup_info()
            
            # Start the application
            self.start_application()
            
        except KeyboardInterrupt:
            logger.info("👋 Application stopped by user")
        except Exception as e:
            logger.error(f"❌ Application startup failed: {e}")
            sys.exit(1)

def main():
    """Main entry point"""
    # Change to the application directory
    app_dir = Path(__file__).parent
    os.chdir(app_dir)
    
    # Create app starter and run
    starter = AppStarter()
    starter.run()

if __name__ == "__main__":
    main()
