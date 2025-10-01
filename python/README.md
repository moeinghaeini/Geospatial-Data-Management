# 🏛️ Italy Geospatial Explorer - Complete Python Application

A comprehensive geospatial data management and analysis platform built with Python, FastAPI, and PostgreSQL with PostGIS extension.

## 🎯 Overview

This is a complete, production-ready Python application that extends the existing Node.js geospatial application with advanced capabilities including:

- **Advanced Spatial Analysis**: Clustering, density analysis, accessibility modeling
- **Machine Learning**: Predictive models for spatial data
- **Real-time Processing**: WebSocket support for live updates
- **Data Management**: Import/export, cleaning, validation
- **Advanced Visualizations**: Interactive maps, 3D visualizations, dashboards
- **Database Integration**: Full PostgreSQL/PostGIS integration

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher with PostGIS extension
- Node.js (for the frontend integration)

### Installation

1. **Clone and navigate to the Python directory**
   ```bash
   cd python
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp ../env.example .env
   # Edit .env with your database credentials
   ```

4. **Start the application**
   ```bash
   python start_app.py
   ```

The application will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🏗️ Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                      │
├─────────────────────────────────────────────────────────────┤
│  • REST API Endpoints                                       │
│  • WebSocket Real-time Updates                             │
│  • Background Task Processing                              │
│  • Request/Response Validation                             │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                Spatial Analysis Engine                      │
├─────────────────────────────────────────────────────────────┤
│  • SpatialAnalyzer - Advanced spatial operations           │
│  • DataProcessor - Data import/export/cleaning              │
│  • MLPredictor - Machine learning models                  │
│  • AdvancedVisualizer - Interactive visualizations        │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                Database Integration                         │
├─────────────────────────────────────────────────────────────┤
│  • PostgreSQL with PostGIS                                 │
│  • Spatial indexing and optimization                       │
│  • CRUD operations for landmarks                           │
│  • Analysis results storage                                │
└─────────────────────────────────────────────────────────────┘
```

### Key Features

#### 🗺️ **Spatial Analysis**
- **Clustering**: K-means, DBSCAN, hierarchical clustering
- **Density Analysis**: Grid-based density mapping
- **Accessibility Analysis**: Travel time and proximity modeling
- **Nearest Neighbors**: KNN spatial queries
- **Spatial Statistics**: Comprehensive spatial metrics

#### 🤖 **Machine Learning**
- **Accessibility Prediction**: Predict landmark accessibility scores
- **Landmark Classification**: Classify landmarks by type
- **Spatial Clustering**: Unsupervised learning for spatial patterns
- **Model Training**: Background training with real-time updates

#### 📊 **Data Processing**
- **Import/Export**: Multiple formats (GeoJSON, Shapefile, KML, CSV)
- **Data Cleaning**: Validation, error correction, quality assessment
- **Transformation**: Coordinate system conversion, geometry simplification
- **Quality Metrics**: Comprehensive data quality scoring

#### 🎨 **Advanced Visualizations**
- **Interactive Maps**: Folium-based maps with clustering
- **3D Visualizations**: Plotly 3D scatter plots
- **Statistical Charts**: Matplotlib/Seaborn visualizations
- **Dashboards**: Comprehensive analysis dashboards

#### 🔄 **Real-time Features**
- **WebSocket Support**: Live updates and notifications
- **Background Processing**: Asynchronous analysis tasks
- **Real-time Analytics**: Live spatial analysis
- **Event Broadcasting**: Real-time data updates

## 📚 API Documentation

### Core Endpoints

#### Landmarks Management
- `GET /api/landmarks` - Get all landmarks
- `POST /api/landmarks` - Create new landmark
- `PUT /api/landmarks/{id}` - Update landmark
- `DELETE /api/landmarks/{id}` - Delete landmark

#### Spatial Analysis
- `POST /api/analysis/spatial` - Perform spatial analysis
- `POST /api/spatial/nearest` - Find nearest landmarks
- `POST /api/spatial/cluster` - Spatial clustering
- `POST /api/spatial/density` - Density analysis
- `POST /api/spatial/accessibility` - Accessibility analysis

#### Machine Learning
- `POST /api/ml/train` - Train ML models
- `POST /api/ml/predict` - Make predictions
- `GET /api/ml/models` - Get model information

#### Data Processing
- `POST /api/data/import` - Import geospatial data
- `GET /api/data/export` - Export data
- `POST /api/data/clean` - Clean and validate data
- `POST /api/data/transform` - Transform data

#### Visualizations
- `POST /api/visualize/map` - Create interactive maps
- `GET /api/visualize/dashboard` - Create dashboards
- `POST /api/visualize/charts` - Create data charts

#### Real-time
- `WebSocket /ws` - Real-time updates
- `POST /api/realtime/process` - Process real-time data

### Example API Usage

#### Create a Landmark
```python
import requests

landmark_data = {
    "name": "Trevi Fountain",
    "description": "Famous fountain in Rome",
    "landmark_type": "monument",
    "geometry": {
        "type": "Point",
        "coordinates": [12.4833, 41.9009]
    },
    "properties": {
        "built": "1762",
        "architect": "Nicola Salvi"
    }
}

response = requests.post("http://localhost:8000/api/landmarks", json=landmark_data)
print(response.json())
```

#### Perform Spatial Analysis
```python
analysis_request = {
    "analysis_type": "clustering",
    "parameters": {
        "method": "kmeans",
        "n_clusters": 3
    }
}

response = requests.post("http://localhost:8000/api/analysis/spatial", json=analysis_request)
print(response.json())
```

#### Train ML Model
```python
training_request = {
    "model_type": "accessibility",
    "training_data": geojson_data,
    "parameters": {
        "n_estimators": 100,
        "random_state": 42
    }
}

response = requests.post("http://localhost:8000/api/ml/train", json=training_request)
print(response.json())
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=geospatial_db
DB_USER=postgres
DB_PASSWORD=your_password

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=true

# Optional: API Keys for external services
MAPBOX_TOKEN=your_mapbox_token
GOOGLE_MAPS_API_KEY=your_google_maps_key
```

### Configuration File

The `config.json` file contains comprehensive application settings:

```json
{
  "app": {
    "name": "Italy Geospatial Explorer",
    "version": "2.0.0",
    "host": "0.0.0.0",
    "port": 8000,
    "debug": true
  },
  "database": {
    "host": "localhost",
    "port": 5432,
    "name": "geospatial_db",
    "user": "postgres",
    "password": "password"
  },
  "features": {
    "websocket": true,
    "ml_models": true,
    "real_time_analysis": true
  }
}
```

## 🗄️ Database Schema

### Tables

#### `geospatial_data`
```sql
CREATE TABLE geospatial_data (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    landmark_type VARCHAR(100),
    geometry GEOMETRY(GEOMETRY, 4326),
    properties JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `analysis_results`
```sql
CREATE TABLE analysis_results (
    id SERIAL PRIMARY KEY,
    analysis_type VARCHAR(100) NOT NULL,
    parameters JSONB,
    results JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `user_sessions`
```sql
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE,
    user_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes

- **Spatial Index**: `GIST` index on geometry column
- **Properties Index**: `GIN` index on JSONB properties
- **Type Index**: B-tree index on landmark_type
- **Timestamp Index**: B-tree index on created_at

## 🧪 Testing

### Run Tests
```bash
# Test individual modules
python spatial_analysis.py
python data_processor.py
python ml_models.py
python visualization.py
python database_integration.py

# Test the complete application
python -m pytest tests/
```

### Health Check
```bash
curl http://localhost:8000/api/health
```

## 📊 Performance Optimization

### Database Optimization
- **Spatial Indexing**: GIST indexes for optimal spatial queries
- **Query Optimization**: EXPLAIN ANALYZE for performance tuning
- **Connection Pooling**: Efficient database connections
- **Prepared Statements**: SQL injection prevention

### Application Optimization
- **Async Processing**: Background tasks for heavy computations
- **Caching**: Result caching for repeated queries
- **Memory Management**: Efficient data structures
- **Batch Processing**: Bulk operations for large datasets

## 🔒 Security

### Data Protection
- **Input Validation**: Pydantic models for request validation
- **SQL Injection Prevention**: Parameterized queries
- **CORS Configuration**: Cross-origin security
- **Rate Limiting**: Request throttling

### Authentication (Optional)
- **JWT Tokens**: Stateless authentication
- **Role-based Access**: Permission management
- **Session Management**: Secure user sessions

## 🚀 Deployment

### Development
```bash
python start_app.py
```

### Production
```bash
# Using Gunicorn
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Using Docker
docker build -t italy-geospatial-app .
docker run -p 8000:8000 italy-geospatial-app
```

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up database
createdb geospatial_db
psql -d geospatial_db -c "CREATE EXTENSION postgis;"

# Run migrations
python database_integration.py
```

## 📈 Monitoring

### Logging
- **Application Logs**: `logs/app.log`
- **Error Tracking**: Comprehensive error logging
- **Performance Metrics**: Request/response timing
- **Database Monitoring**: Query performance tracking

### Health Monitoring
- **Health Endpoint**: `/api/health`
- **Database Status**: Connection monitoring
- **WebSocket Status**: Active connection tracking
- **System Resources**: Memory and CPU usage

## 🤝 Integration with Node.js App

### Frontend Integration
```javascript
// Call Python API from Node.js
const axios = require('axios');

app.post('/api/advanced/analyze', async (req, res) => {
  try {
    const response = await axios.post('http://localhost:8000/api/analysis/spatial', req.body);
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: 'Advanced analysis failed' });
  }
});
```

### WebSocket Integration
```javascript
// WebSocket client for real-time updates
const WebSocket = require('ws');
const ws = new WebSocket('ws://localhost:8000/ws');

ws.on('message', (data) => {
  const message = JSON.parse(data);
  console.log('Received:', message);
});
```

## 🔮 Future Enhancements

### Planned Features
- **Real-time Streaming**: WebSocket integration for live data
- **Advanced ML**: Deep learning models for spatial analysis
- **Mobile Support**: React Native mobile application
- **Cloud Deployment**: AWS/GCP/Azure integration

### Scalability Improvements
- **Microservices**: Service decomposition
- **Load Balancing**: Traffic distribution
- **Caching Layers**: Redis integration
- **CDN Integration**: Global content delivery

## 📞 Support

### Documentation
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Code Examples**: See individual module files

### Troubleshooting
- **Logs**: Check `logs/app.log` for errors
- **Database**: Verify PostgreSQL connection
- **Dependencies**: Ensure all packages are installed
- **Ports**: Check if port 8000 is available

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**🏛️ Built with ❤️ for exploring Italy's rich cultural heritage and advancing geospatial technology**
