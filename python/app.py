"""
Complete Italy Geospatial Explorer - Python Application
A comprehensive geospatial data management and analysis application
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, Polygon, LineString
from shapely.wkt import loads
import folium
from folium import plugins
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score
import joblib
import schedule
import time
from threading import Thread
import websockets
import aiofiles

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our custom modules
from spatial_analysis import SpatialAnalyzer
from data_processor import DataProcessor
from ml_models import SpatialMLPredictor
from visualization import AdvancedVisualizer

# Initialize FastAPI app
app = FastAPI(
    title="Italy Geospatial Explorer - Complete Application",
    description="Comprehensive geospatial data management and analysis platform",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5000", "http://localhost:5001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="output"), name="static")

# Global instances
spatial_analyzer = SpatialAnalyzer()
data_processor = DataProcessor()
ml_predictor = SpatialMLPredictor()
visualizer = AdvancedVisualizer()

# Database connection
class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432'),
                database=os.getenv('DB_NAME', 'geospatial_db'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'password')
            )
            logger.info("✅ Database connected successfully")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            self.connection = None
    
    def get_connection(self):
        """Get database connection"""
        if self.connection is None or self.connection.closed:
            self.connect()
        return self.connection
    
    def execute_query(self, query: str, params: tuple = None):
        """Execute database query"""
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                else:
                    conn.commit()
                    return cursor.rowcount
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Initialize database manager
db_manager = DatabaseManager()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Pydantic models
class GeoJSONData(BaseModel):
    type: str
    features: List[Dict[str, Any]]

class SpatialQuery(BaseModel):
    lat: float
    lon: float
    radius: Optional[float] = None
    limit: Optional[int] = 10

class LandmarkData(BaseModel):
    name: str
    description: str
    landmark_type: str
    geometry: Dict[str, Any]
    properties: Optional[Dict[str, Any]] = {}

class AnalysisRequest(BaseModel):
    analysis_type: str
    parameters: Dict[str, Any]
    data: Optional[GeoJSONData] = None

class MLTrainingRequest(BaseModel):
    model_type: str
    training_data: GeoJSONData
    parameters: Optional[Dict[str, Any]] = {}

# Database initialization
@app.on_event("startup")
async def startup_event():
    """Initialize database and create tables"""
    try:
        # Create geospatial_data table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS geospatial_data (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            landmark_type VARCHAR(100),
            geometry GEOMETRY(GEOMETRY, 4326),
            properties JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Create spatial index
        create_index_query = """
        CREATE INDEX IF NOT EXISTS idx_geospatial_geometry 
        ON geospatial_data USING GIST (geometry);
        """
        
        # Create properties index
        create_properties_index_query = """
        CREATE INDEX IF NOT EXISTS idx_geospatial_properties 
        ON geospatial_data USING GIN (properties);
        """
        
        db_manager.execute_query(create_table_query)
        db_manager.execute_query(create_index_query)
        db_manager.execute_query(create_properties_index_query)
        
        # Insert sample Italian landmarks if table is empty
        sample_landmarks = [
            {
                'name': 'Colosseum',
                'description': 'Ancient Roman amphitheater in Rome',
                'landmark_type': 'monument',
                'geometry': 'POINT(12.4922 41.8902)',
                'properties': {'built': '70-80 AD', 'capacity': '50,000 spectators'}
            },
            {
                'name': 'Leaning Tower of Pisa',
                'description': 'Famous bell tower in Pisa',
                'landmark_type': 'monument',
                'geometry': 'POINT(10.3966 43.7230)',
                'properties': {'height': '56.67m', 'tilt': '3.97 degrees'}
            },
            {
                'name': 'Venice Grand Canal',
                'description': 'Main waterway in Venice',
                'landmark_type': 'waterway',
                'geometry': 'LINESTRING(12.3267 45.4408, 12.3350 45.4300, 12.3450 45.4200)',
                'properties': {'length': '3.8 km', 'width': '30-70m'}
            },
            {
                'name': 'Vatican City',
                'description': 'Independent city-state within Rome',
                'landmark_type': 'city-state',
                'geometry': 'POLYGON((12.4459 41.9022, 12.4580 41.9022, 12.4580 41.9094, 12.4459 41.9094, 12.4459 41.9022))',
                'properties': {'area': '0.17 sq mi', 'population': '825'}
            },
            {
                'name': 'Florence Cathedral',
                'description': 'Cathedral of Santa Maria del Fiore',
                'landmark_type': 'cathedral',
                'geometry': 'POINT(11.2558 43.7731)',
                'properties': {'height': '114m', 'dome': 'Brunelleschi\'s Dome'}
            },
            {
                'name': 'Amalfi Coast',
                'description': 'Stunning coastline in southern Italy',
                'landmark_type': 'coastline',
                'geometry': 'LINESTRING(14.6270 40.6340, 14.7200 40.6500, 14.8000 40.6800, 14.9000 40.7200)',
                'properties': {'length': '50 km', 'region': 'Campania'}
            },
            {
                'name': 'Lake Como',
                'description': 'Beautiful lake in northern Italy',
                'landmark_type': 'lake',
                'geometry': 'POLYGON((9.2000 46.0000, 9.3000 46.0000, 9.3000 46.1000, 9.2000 46.1000, 9.2000 46.0000))',
                'properties': {'area': '146 sq km', 'depth': '425m'}
            },
            {
                'name': 'Pompeii',
                'description': 'Ancient Roman city destroyed by Vesuvius',
                'landmark_type': 'archaeological_site',
                'geometry': 'POINT(14.4848 40.7489)',
                'properties': {'destroyed': '79 AD', 'area': '66 hectares'}
            }
        ]
        
        # Check if data already exists
        count_query = "SELECT COUNT(*) FROM geospatial_data"
        result = db_manager.execute_query(count_query)
        
        if result[0]['count'] == 0:
            # Insert sample data
            for landmark in sample_landmarks:
                insert_query = """
                INSERT INTO geospatial_data (name, description, landmark_type, geometry, properties)
                VALUES (%s, %s, %s, ST_GeomFromText(%s, 4326), %s)
                """
                db_manager.execute_query(insert_query, (
                    landmark['name'],
                    landmark['description'],
                    landmark['landmark_type'],
                    landmark['geometry'],
                    json.dumps(landmark['properties'])
                ))
            
            logger.info("✅ Sample Italian landmarks inserted into database")
        
        logger.info("✅ Database initialization completed")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db_status = "connected" if db_manager.get_connection() else "disconnected"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "Italy Geospatial Explorer - Complete Application",
            "version": "2.0.0",
            "database": db_status,
            "active_connections": len(manager.active_connections)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong", "timestamp": datetime.now().isoformat()})
            elif message.get("type") == "subscribe":
                # Handle subscription to specific data updates
                await websocket.send_json({"type": "subscribed", "channel": message.get("channel")})
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# CRUD Operations for Landmarks
@app.get("/api/landmarks")
async def get_landmarks(limit: int = 100, offset: int = 0, landmark_type: str = None):
    """Get all landmarks with optional filtering"""
    try:
        query = """
        SELECT id, name, description, landmark_type, 
               ST_AsGeoJSON(geometry) as geometry, properties, created_at, updated_at
        FROM geospatial_data
        """
        params = []
        
        if landmark_type:
            query += " WHERE landmark_type = %s"
            params.append(landmark_type)
        
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        results = db_manager.execute_query(query, tuple(params))
        
        # Convert to GeoJSON format
        features = []
        for row in results:
            feature = {
                "type": "Feature",
                "id": row['id'],
                "properties": {
                    "name": row['name'],
                    "description": row['description'],
                    "type": row['landmark_type'],
                    "created_at": row['created_at'].isoformat() if row['created_at'] else None,
                    "updated_at": row['updated_at'].isoformat() if row['updated_at'] else None,
                    **json.loads(row['properties']) if row['properties'] else {}
                },
                "geometry": json.loads(row['geometry'])
            }
            features.append(feature)
        
        return {
            "type": "FeatureCollection",
            "features": features,
            "total": len(features)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch landmarks: {str(e)}")

@app.post("/api/landmarks")
async def create_landmark(landmark: LandmarkData):
    """Create a new landmark"""
    try:
        # Convert geometry to WKT
        geometry_wkt = f"POINT({landmark.geometry['coordinates'][0]} {landmark.geometry['coordinates'][1]})"
        
        insert_query = """
        INSERT INTO geospatial_data (name, description, landmark_type, geometry, properties)
        VALUES (%s, %s, %s, ST_GeomFromText(%s, 4326), %s)
        RETURNING id
        """
        
        result = db_manager.execute_query(insert_query, (
            landmark.name,
            landmark.description,
            landmark.landmark_type,
            geometry_wkt,
            json.dumps(landmark.properties)
        ))
        
        # Broadcast update to WebSocket clients
        await manager.broadcast({
            "type": "landmark_created",
            "data": {
                "id": result,
                "name": landmark.name,
                "type": landmark.landmark_type
            }
        })
        
        return {"id": result, "message": "Landmark created successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create landmark: {str(e)}")

@app.put("/api/landmarks/{landmark_id}")
async def update_landmark(landmark_id: int, landmark: LandmarkData):
    """Update an existing landmark"""
    try:
        geometry_wkt = f"POINT({landmark.geometry['coordinates'][0]} {landmark.geometry['coordinates'][1]})"
        
        update_query = """
        UPDATE geospatial_data 
        SET name = %s, description = %s, landmark_type = %s, 
            geometry = ST_GeomFromText(%s, 4326), properties = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """
        
        result = db_manager.execute_query(update_query, (
            landmark.name,
            landmark.description,
            landmark.landmark_type,
            geometry_wkt,
            json.dumps(landmark.properties),
            landmark_id
        ))
        
        if result == 0:
            raise HTTPException(status_code=404, detail="Landmark not found")
        
        # Broadcast update
        await manager.broadcast({
            "type": "landmark_updated",
            "data": {"id": landmark_id, "name": landmark.name}
        })
        
        return {"message": "Landmark updated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update landmark: {str(e)}")

@app.delete("/api/landmarks/{landmark_id}")
async def delete_landmark(landmark_id: int):
    """Delete a landmark"""
    try:
        delete_query = "DELETE FROM geospatial_data WHERE id = %s"
        result = db_manager.execute_query(delete_query, (landmark_id,))
        
        if result == 0:
            raise HTTPException(status_code=404, detail="Landmark not found")
        
        # Broadcast update
        await manager.broadcast({
            "type": "landmark_deleted",
            "data": {"id": landmark_id}
        })
        
        return {"message": "Landmark deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete landmark: {str(e)}")

# Advanced Spatial Analysis
@app.post("/api/analysis/spatial")
async def perform_spatial_analysis(request: AnalysisRequest):
    """Perform comprehensive spatial analysis"""
    try:
        # Get landmarks from database
        landmarks_query = """
        SELECT id, name, description, landmark_type, 
               ST_AsGeoJSON(geometry) as geometry, properties
        FROM geospatial_data
        """
        landmarks_data = db_manager.execute_query(landmarks_query)
        
        # Convert to GeoJSON format
        features = []
        for row in landmarks_data:
            feature = {
                "type": "Feature",
                "id": row['id'],
                "properties": {
                    "name": row['name'],
                    "description": row['description'],
                    "type": row['landmark_type'],
                    **json.loads(row['properties']) if row['properties'] else {}
                },
                "geometry": json.loads(row['geometry'])
            }
            features.append(feature)
        
        geojson_data = {"type": "FeatureCollection", "features": features}
        
        # Load data into spatial analyzer
        gdf = spatial_analyzer.load_data(geojson_data)
        
        if gdf is None:
            raise HTTPException(status_code=400, detail="Failed to load spatial data")
        
        # Perform analysis based on type
        analysis_type = request.analysis_type
        parameters = request.parameters
        
        if analysis_type == "clustering":
            results = spatial_analyzer.spatial_clustering(
                method=parameters.get("method", "kmeans"),
                n_clusters=parameters.get("n_clusters", 3)
            )
        elif analysis_type == "density":
            results = spatial_analyzer.density_analysis(
                grid_size=parameters.get("grid_size", 0.1)
            )
        elif analysis_type == "accessibility":
            results = spatial_analyzer.accessibility_analysis(
                transport_speed=parameters.get("transport_speed", 50.0)
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown analysis type: {analysis_type}")
        
        # Broadcast analysis results
        await manager.broadcast({
            "type": "analysis_completed",
            "data": {
                "analysis_type": analysis_type,
                "results": results
            }
        })
        
        return {
            "success": True,
            "analysis_type": analysis_type,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Spatial analysis failed: {str(e)}")

# Machine Learning Endpoints
@app.post("/api/ml/train")
async def train_ml_model(request: MLTrainingRequest, background_tasks: BackgroundTasks):
    """Train machine learning models"""
    try:
        # Convert training data to GeoDataFrame
        gdf = spatial_analyzer.load_data(request.training_data.dict())
        
        if gdf is None:
            raise HTTPException(status_code=400, detail="Failed to load training data")
        
        # Train model in background
        background_tasks.add_task(
            _train_model_background,
            gdf=gdf,
            model_type=request.model_type,
            parameters=request.parameters
        )
        
        return {
            "success": True,
            "message": f"Training started for {request.model_type} model",
            "status": "training_in_progress"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model training failed: {str(e)}")

async def _train_model_background(gdf, model_type: str, parameters: Dict):
    """Background task for model training"""
    try:
        # Train the model
        results = ml_predictor.train_model(gdf, model_type)
        
        # Broadcast training completion
        await manager.broadcast({
            "type": "model_training_completed",
            "data": {
                "model_type": model_type,
                "results": results
            }
        })
        
    except Exception as e:
        logger.error(f"Background training failed: {e}")
        await manager.broadcast({
            "type": "model_training_failed",
            "data": {"error": str(e)}
        })

@app.post("/api/ml/predict")
async def make_prediction(features: List[float], model_type: str = "accessibility"):
    """Make predictions using trained models"""
    try:
        prediction = ml_predictor.predict(features, model_type)
        
        return {
            "success": True,
            "prediction": prediction,
            "model_type": model_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

# Data Import/Export
@app.post("/api/data/import")
async def import_data(file_path: str, format: str = "geojson"):
    """Import geospatial data from file"""
    try:
        imported_data = data_processor.import_data(file_path, format)
        
        # Save to database
        if imported_data and 'data' in imported_data:
            gdf = imported_data['data']
            
            for idx, row in gdf.iterrows():
                # Convert geometry to WKT
                geometry_wkt = row.geometry.wkt
                
                insert_query = """
                INSERT INTO geospatial_data (name, description, landmark_type, geometry, properties)
                VALUES (%s, %s, %s, ST_GeomFromText(%s, 4326), %s)
                """
                
                db_manager.execute_query(insert_query, (
                    row.get('name', f'Imported Feature {idx}'),
                    row.get('description', ''),
                    row.get('type', 'unknown'),
                    geometry_wkt,
                    json.dumps(row.drop(['geometry']).to_dict())
                ))
        
        return {
            "success": True,
            "imported_features": len(imported_data['data']) if imported_data else 0,
            "format": format
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data import failed: {str(e)}")

@app.get("/api/data/export")
async def export_data(format: str = "geojson"):
    """Export all landmarks data"""
    try:
        # Get all landmarks
        landmarks_query = """
        SELECT id, name, description, landmark_type, 
               ST_AsGeoJSON(geometry) as geometry, properties
        FROM geospatial_data
        """
        landmarks_data = db_manager.execute_query(landmarks_query)
        
        # Convert to GeoJSON
        features = []
        for row in landmarks_data:
            feature = {
                "type": "Feature",
                "id": row['id'],
                "properties": {
                    "name": row['name'],
                    "description": row['description'],
                    "type": row['landmark_type'],
                    **json.loads(row['properties']) if row['properties'] else {}
                },
                "geometry": json.loads(row['geometry'])
            }
            features.append(feature)
        
        geojson_data = {"type": "FeatureCollection", "features": features}
        
        # Export to file
        if format == "geojson":
            output_path = f"output/landmarks_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.geojson"
            with open(output_path, 'w') as f:
                json.dump(geojson_data, f, indent=2)
            
            return FileResponse(output_path, filename=f"italy_landmarks_{datetime.now().strftime('%Y%m%d')}.geojson")
        
        return geojson_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data export failed: {str(e)}")

# Visualization Endpoints
@app.post("/api/visualize/map")
async def create_visualization_map(style: str = "default"):
    """Create interactive visualization map"""
    try:
        # Get landmarks data
        landmarks_query = """
        SELECT id, name, description, landmark_type, 
               ST_AsGeoJSON(geometry) as geometry, properties
        FROM geospatial_data
        """
        landmarks_data = db_manager.execute_query(landmarks_query)
        
        # Convert to GeoDataFrame
        features = []
        for row in landmarks_data:
            feature = {
                "type": "Feature",
                "id": row['id'],
                "properties": {
                    "name": row['name'],
                    "description": row['description'],
                    "type": row['landmark_type'],
                    **json.loads(row['properties']) if row['properties'] else {}
                },
                "geometry": json.loads(row['geometry'])
            }
            features.append(feature)
        
        geojson_data = {"type": "FeatureCollection", "features": features}
        gdf = spatial_analyzer.load_data(geojson_data)
        
        # Create visualization
        map_path = visualizer.create_interactive_map(gdf, style=style)
        
        return {
            "success": True,
            "map_path": map_path,
            "download_url": f"/static/{os.path.basename(map_path)}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Map creation failed: {str(e)}")

@app.get("/api/visualize/dashboard")
async def create_dashboard():
    """Create comprehensive dashboard"""
    try:
        # Get landmarks data
        landmarks_query = """
        SELECT id, name, description, landmark_type, 
               ST_AsGeoJSON(geometry) as geometry, properties
        FROM geospatial_data
        """
        landmarks_data = db_manager.execute_query(landmarks_query)
        
        # Convert to GeoDataFrame
        features = []
        for row in landmarks_data:
            feature = {
                "type": "Feature",
                "id": row['id'],
                "properties": {
                    "name": row['name'],
                    "description": row['description'],
                    "type": row['landmark_type'],
                    **json.loads(row['properties']) if row['properties'] else {}
                },
                "geometry": json.loads(row['geometry'])
            }
            features.append(feature)
        
        geojson_data = {"type": "FeatureCollection", "features": features}
        gdf = spatial_analyzer.load_data(geojson_data)
        
        # Create dashboard
        dashboard_path = visualizer.create_interactive_dashboard(gdf)
        
        return FileResponse(dashboard_path, filename="italy_dashboard.html")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard creation failed: {str(e)}")

# Statistics and Analytics
@app.get("/api/statistics")
async def get_statistics():
    """Get comprehensive statistics about the dataset"""
    try:
        # Get basic statistics
        total_landmarks_query = "SELECT COUNT(*) as total FROM geospatial_data"
        type_distribution_query = """
        SELECT landmark_type, COUNT(*) as count 
        FROM geospatial_data 
        GROUP BY landmark_type
        """
        
        total_result = db_manager.execute_query(total_landmarks_query)
        type_results = db_manager.execute_query(type_distribution_query)
        
        # Get spatial bounds
        bounds_query = """
        SELECT 
            ST_XMin(ST_Extent(geometry)) as min_lon,
            ST_YMin(ST_Extent(geometry)) as min_lat,
            ST_XMax(ST_Extent(geometry)) as max_lon,
            ST_YMax(ST_Extent(geometry)) as max_lat
        FROM geospatial_data
        """
        bounds_result = db_manager.execute_query(bounds_query)
        
        statistics = {
            "total_landmarks": total_result[0]['total'],
            "type_distribution": {row['landmark_type']: row['count'] for row in type_results},
            "spatial_bounds": {
                "min_lon": float(bounds_result[0]['min_lon']) if bounds_result[0]['min_lon'] else 0,
                "min_lat": float(bounds_result[0]['min_lat']) if bounds_result[0]['min_lat'] else 0,
                "max_lon": float(bounds_result[0]['max_lon']) if bounds_result[0]['max_lon'] else 0,
                "max_lat": float(bounds_result[0]['max_lat']) if bounds_result[0]['max_lat'] else 0
            },
            "last_updated": datetime.now().isoformat()
        }
        
        return statistics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Statistics generation failed: {str(e)}")

# Real-time data processing
@app.post("/api/realtime/process")
async def process_realtime_data(data: GeoJSONData):
    """Process real-time geospatial data"""
    try:
        # Load and analyze data
        gdf = spatial_analyzer.load_data(data.dict())
        
        if gdf is None:
            raise HTTPException(status_code=400, detail="Failed to load data")
        
        # Perform real-time analysis
        analysis_results = {
            "feature_count": len(gdf),
            "bounds": gdf.total_bounds.tolist(),
            "geometry_types": gdf.geometry.geom_type.value_counts().to_dict(),
            "timestamp": datetime.now().isoformat()
        }
        
        # Broadcast results to WebSocket clients
        await manager.broadcast({
            "type": "realtime_analysis",
            "data": analysis_results
        })
        
        return analysis_results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Real-time processing failed: {str(e)}")

# Background tasks
def background_data_cleanup():
    """Background task for data cleanup and maintenance"""
    try:
        # Clean up old temporary files
        import glob
        temp_files = glob.glob("output/temp_*")
        for file in temp_files:
            if os.path.exists(file):
                os.remove(file)
        
        logger.info("Background cleanup completed")
        
    except Exception as e:
        logger.error(f"Background cleanup failed: {e}")

# Schedule background tasks
schedule.every(1).hours.do(background_data_cleanup)

def run_scheduler():
    """Run the background scheduler"""
    while True:
        schedule.run_pending()
        time.sleep(60)

# Start background scheduler in a separate thread
scheduler_thread = Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

# Main application entry point
if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("output", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run the application
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
