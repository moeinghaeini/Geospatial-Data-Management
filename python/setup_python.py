#!/usr/bin/env python3
"""
Python Setup Script for Italy Geospatial Explorer
Installs dependencies and sets up the Python environment
"""

import subprocess
import sys
import os
import json
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. Current version: {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    # Install from requirements.txt
    if os.path.exists("requirements.txt"):
        success = run_command("pip install -r requirements.txt", "Installing requirements")
        if not success:
            return False
    else:
        print("⚠️ requirements.txt not found, installing core packages...")
        core_packages = [
            "geopandas", "shapely", "folium", "geopy", "pandas", "numpy",
            "matplotlib", "seaborn", "plotly", "scikit-learn", "fastapi", "uvicorn"
        ]
        for package in core_packages:
            run_command(f"pip install {package}", f"Installing {package}")
    
    return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    directories = [
        "output",
        "models",
        "data",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def create_config_file():
    """Create configuration file"""
    print("⚙️ Creating configuration file...")
    
    config = {
        "api": {
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
        "output": {
            "directory": "output",
            "formats": ["html", "png", "json"]
        },
        "models": {
            "directory": "models",
            "types": ["accessibility", "clustering", "classification"]
        }
    }
    
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Configuration file created: config.json")
    return True

def test_installation():
    """Test the installation"""
    print("🧪 Testing installation...")
    
    test_script = """
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import folium
from sklearn.ensemble import RandomForestRegressor
from fastapi import FastAPI
import uvicorn

print("✅ All imports successful!")
print("🎉 Python environment setup completed successfully!")
"""
    
    try:
        exec(test_script)
        return True
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False

def create_startup_script():
    """Create startup script for the Python API"""
    print("🚀 Creating startup script...")
    
    startup_script = """#!/usr/bin/env python3
\"\"\"
Startup script for Italy Geospatial Explorer Python API
\"\"\"

import uvicorn
import os
from pathlib import Path

if __name__ == "__main__":
    # Change to the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Start the FastAPI server
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
"""
    
    with open("start_python_api.py", "w") as f:
        f.write(startup_script)
    
    # Make it executable
    os.chmod("start_python_api.py", 0o755)
    
    print("✅ Startup script created: start_python_api.py")
    return True

def create_integration_guide():
    """Create integration guide for using Python with the existing Node.js app"""
    print("📚 Creating integration guide...")
    
    guide_content = """# Python Integration Guide for Italy Geospatial Explorer

## Overview
This guide explains how to integrate the Python-based geospatial analysis capabilities with the existing Node.js application.

## Architecture
```
Node.js Frontend (React) ←→ Node.js Backend (Express) ←→ Python API (FastAPI)
                                                              ↓
                                                      PostgreSQL + PostGIS
```

## Setup Instructions

### 1. Install Python Dependencies
```bash
cd python
python setup_python.py
```

### 2. Start Python API Server
```bash
cd python
python start_python_api.py
```

### 3. Integrate with Node.js Backend
Add the following to your Node.js routes:

```javascript
const axios = require('axios');

// Example: Call Python API for advanced analysis
app.post('/api/advanced/analyze', async (req, res) => {
  try {
    const response = await axios.post('http://localhost:8000/api/spatial/analyze', req.body);
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: 'Advanced analysis failed' });
  }
});
```

## Available Python Endpoints

### Spatial Analysis
- `POST /api/spatial/analyze` - Comprehensive spatial analysis
- `POST /api/spatial/nearest` - Find nearest landmarks
- `POST /api/spatial/cluster` - Spatial clustering
- `POST /api/spatial/density` - Density analysis
- `POST /api/spatial/accessibility` - Accessibility analysis

### Machine Learning
- `POST /api/ml/predict` - Make predictions
- `POST /api/ml/train` - Train ML models

### Data Processing
- `POST /api/data/import` - Import geospatial data
- `POST /api/data/clean` - Clean and validate data
- `POST /api/data/transform` - Transform data

### Visualization
- `POST /api/visualize/map` - Create interactive maps
- `POST /api/visualize/charts` - Create data charts

## Usage Examples

### 1. Advanced Spatial Analysis
```javascript
// Call Python API for clustering analysis
const clusteringResult = await axios.post('http://localhost:8000/api/spatial/cluster', {
  method: 'kmeans',
  n_clusters: 3,
  data: geojsonData
});
```

### 2. Machine Learning Predictions
```javascript
// Make accessibility predictions
const prediction = await axios.post('http://localhost:8000/api/ml/predict', {
  features: [12.4922, 41.8902, 0.001, 0.001, 12.49, 41.89, 12.50, 41.90, 0.1],
  model_type: 'accessibility'
});
```

### 3. Data Visualization
```javascript
// Create interactive visualizations
const visualization = await axios.post('http://localhost:8000/api/visualize/map', {
  data: geojsonData,
  style: 'default'
});
```

## Benefits of Python Integration

### 1. Advanced Spatial Analysis
- Sophisticated clustering algorithms
- Density analysis and heatmaps
- Accessibility modeling
- Spatial statistics

### 2. Machine Learning Capabilities
- Predictive modeling for accessibility
- Landmark type classification
- Spatial pattern recognition
- Anomaly detection

### 3. Enhanced Data Processing
- Data cleaning and validation
- Format conversion (Shapefile, KML, CSV)
- Coordinate system transformations
- Data quality assessment

### 4. Advanced Visualizations
- Interactive Folium maps
- 3D visualizations
- Statistical charts and graphs
- Dashboard creation

## Performance Considerations

### 1. Async Processing
- Use background tasks for heavy computations
- Implement job queues for long-running analyses
- Cache results for repeated queries

### 2. Data Optimization
- Use spatial indexing for large datasets
- Implement data pagination
- Optimize GeoJSON serialization

### 3. Error Handling
- Implement comprehensive error handling
- Add retry mechanisms for failed requests
- Log errors for debugging

## Monitoring and Logging

### 1. API Monitoring
- Track request/response times
- Monitor error rates
- Log usage statistics

### 2. Performance Metrics
- Database query performance
- Spatial analysis execution time
- Memory usage monitoring

## Security Considerations

### 1. API Security
- Implement rate limiting
- Add authentication/authorization
- Validate input data

### 2. Data Security
- Secure database connections
- Encrypt sensitive data
- Implement access controls

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure all dependencies are installed
2. **Port Conflicts**: Check if port 8000 is available
3. **Memory Issues**: Monitor memory usage for large datasets
4. **CORS Issues**: Configure CORS properly for cross-origin requests

### Debug Mode
```bash
# Run Python API in debug mode
python -m uvicorn api.main:app --reload --log-level debug
```

## Future Enhancements

### 1. Real-time Processing
- WebSocket integration
- Real-time data streaming
- Live analysis updates

### 2. Cloud Integration
- AWS/GCP/Azure deployment
- Container orchestration
- Auto-scaling capabilities

### 3. Advanced Analytics
- Deep learning models
- Time series analysis
- Predictive analytics

## Support

For issues and questions:
- Check the Python API documentation at http://localhost:8000/docs
- Review error logs in the logs/ directory
- Test individual components using the example scripts
"""
    
    with open("PYTHON_INTEGRATION_GUIDE.md", "w") as f:
        f.write(guide_content)
    
    print("✅ Integration guide created: PYTHON_INTEGRATION_GUIDE.md")
    return True

def main():
    """Main setup function"""
    print("🌍 Setting up Python environment for Italy Geospatial Explorer...")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Dependency installation failed")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("❌ Directory creation failed")
        sys.exit(1)
    
    # Create config file
    if not create_config_file():
        print("❌ Configuration creation failed")
        sys.exit(1)
    
    # Create startup script
    if not create_startup_script():
        print("❌ Startup script creation failed")
        sys.exit(1)
    
    # Create integration guide
    if not create_integration_guide():
        print("❌ Integration guide creation failed")
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("❌ Installation test failed")
        sys.exit(1)
    
    print("=" * 60)
    print("🎉 Python environment setup completed successfully!")
    print("")
    print("📋 Next steps:")
    print("1. Start the Python API server: python start_python_api.py")
    print("2. Access the API documentation: http://localhost:8000/docs")
    print("3. Read the integration guide: PYTHON_INTEGRATION_GUIDE.md")
    print("4. Test the Python modules: python spatial_analysis.py")
    print("")
    print("🚀 Ready to enhance your geospatial application with Python!")

if __name__ == "__main__":
    main()
