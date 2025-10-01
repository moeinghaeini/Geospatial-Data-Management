"""
FastAPI Backend for Advanced Geospatial Operations
Provides REST API endpoints for spatial analysis, machine learning, and data processing
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import uvicorn
import json
import os
from datetime import datetime

# Import our custom modules
from spatial_analysis import SpatialAnalyzer
from data_processor import DataProcessor
from ml_models import SpatialMLPredictor
from visualization import AdvancedVisualizer

# Initialize FastAPI app
app = FastAPI(
    title="Italy Geospatial Explorer API",
    description="Advanced geospatial analysis API for Italian landmarks and spatial data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
spatial_analyzer = SpatialAnalyzer()
data_processor = DataProcessor()
ml_predictor = SpatialMLPredictor()
visualizer = AdvancedVisualizer()

# Pydantic models for request/response
class GeoJSONData(BaseModel):
    type: str
    features: List[Dict[str, Any]]

class SpatialQuery(BaseModel):
    lat: float
    lon: float
    radius: Optional[float] = None
    limit: Optional[int] = 10

class ClusteringRequest(BaseModel):
    method: str = "kmeans"
    n_clusters: int = 3
    data: GeoJSONData

class MLPredictionRequest(BaseModel):
    features: List[float]
    model_type: str = "accessibility"

class DataImportRequest(BaseModel):
    source: str
    format: str = "geojson"
    options: Optional[Dict[str, Any]] = {}

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Italy Geospatial Explorer API",
        "version": "1.0.0"
    }

# Spatial Analysis Endpoints
@app.post("/api/spatial/analyze")
async def analyze_spatial_data(data: GeoJSONData):
    """Perform comprehensive spatial analysis on geospatial data"""
    try:
        # Load data into spatial analyzer
        gdf = spatial_analyzer.load_data(data.dict())
        
        if gdf is None:
            raise HTTPException(status_code=400, detail="Failed to load geospatial data")
        
        # Perform various analyses
        analysis_results = {
            "total_features": len(gdf),
            "bounds": {
                "min_lat": float(gdf['centroid_lat'].min()),
                "max_lat": float(gdf['centroid_lat'].max()),
                "min_lon": float(gdf['centroid_lon'].min()),
                "max_lon": float(gdf['centroid_lon'].max())
            },
            "feature_types": gdf.get('type', {}).value_counts().to_dict() if 'type' in gdf.columns else {},
            "total_area_sqkm": float(gdf['area_sqkm'].sum()) if 'area_sqkm' in gdf.columns else 0
        }
        
        return {
            "success": True,
            "analysis": analysis_results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/spatial/nearest")
async def find_nearest_landmarks(query: SpatialQuery, data: GeoJSONData):
    """Find nearest landmarks to a given point"""
    try:
        # Load data
        gdf = spatial_analyzer.load_data(data.dict())
        if gdf is None:
            raise HTTPException(status_code=400, detail="Failed to load geospatial data")
        
        # Find nearest landmarks
        nearest = spatial_analyzer.find_nearest_landmarks(
            query.lat, query.lon, query.limit
        )
        
        return {
            "success": True,
            "query_point": {"lat": query.lat, "lon": query.lon},
            "nearest_landmarks": nearest,
            "count": len(nearest)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Nearest neighbor search failed: {str(e)}")

@app.post("/api/spatial/cluster")
async def perform_clustering(request: ClusteringRequest):
    """Perform spatial clustering analysis"""
    try:
        # Load data
        gdf = spatial_analyzer.load_data(request.data.dict())
        if gdf is None:
            raise HTTPException(status_code=400, detail="Failed to load geospatial data")
        
        # Perform clustering
        cluster_results = spatial_analyzer.spatial_clustering(
            method=request.method,
            n_clusters=request.n_clusters
        )
        
        return {
            "success": True,
            "clustering_results": cluster_results,
            "method": request.method,
            "n_clusters": request.n_clusters
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clustering failed: {str(e)}")

@app.post("/api/spatial/density")
async def analyze_density(data: GeoJSONData, grid_size: float = 0.1):
    """Perform density analysis on landmark distribution"""
    try:
        # Load data
        gdf = spatial_analyzer.load_data(data.dict())
        if gdf is None:
            raise HTTPException(status_code=400, detail="Failed to load geospatial data")
        
        # Perform density analysis
        density_results = spatial_analyzer.density_analysis(grid_size)
        
        return {
            "success": True,
            "density_analysis": density_results,
            "grid_size": grid_size
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Density analysis failed: {str(e)}")

@app.post("/api/spatial/accessibility")
async def analyze_accessibility(data: GeoJSONData, transport_speed: float = 50.0):
    """Analyze accessibility of landmarks"""
    try:
        # Load data
        gdf = spatial_analyzer.load_data(data.dict())
        if gdf is None:
            raise HTTPException(status_code=400, detail="Failed to load geospatial data")
        
        # Perform accessibility analysis
        accessibility_results = spatial_analyzer.accessibility_analysis(transport_speed)
        
        return {
            "success": True,
            "accessibility_analysis": accessibility_results,
            "transport_speed_kmh": transport_speed
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Accessibility analysis failed: {str(e)}")

# Machine Learning Endpoints
@app.post("/api/ml/predict")
async def predict_spatial_property(request: MLPredictionRequest):
    """Make predictions using trained ML models"""
    try:
        prediction = ml_predictor.predict(
            features=request.features,
            model_type=request.model_type
        )
        
        return {
            "success": True,
            "prediction": prediction,
            "model_type": request.model_type,
            "confidence": prediction.get('confidence', 0.0)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/api/ml/train")
async def train_ml_model(
    data: GeoJSONData,
    model_type: str = "accessibility",
    background_tasks: BackgroundTasks = None
):
    """Train machine learning models on spatial data"""
    try:
        # Load data
        gdf = spatial_analyzer.load_data(data.dict())
        if gdf is None:
            raise HTTPException(status_code=400, detail="Failed to load geospatial data")
        
        # Train model in background
        if background_tasks:
            background_tasks.add_task(
                ml_predictor.train_model,
                gdf=gdf,
                model_type=model_type
            )
            return {
                "success": True,
                "message": f"Training started for {model_type} model",
                "status": "training_in_progress"
            }
        else:
            # Train synchronously
            training_results = ml_predictor.train_model(gdf, model_type)
            return {
                "success": True,
                "training_results": training_results,
                "model_type": model_type
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model training failed: {str(e)}")

# Data Processing Endpoints
@app.post("/api/data/import")
async def import_geospatial_data(request: DataImportRequest):
    """Import geospatial data from various sources"""
    try:
        imported_data = data_processor.import_data(
            source=request.source,
            format=request.format,
            options=request.options
        )
        
        return {
            "success": True,
            "imported_data": imported_data,
            "source": request.source,
            "format": request.format
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data import failed: {str(e)}")

@app.post("/api/data/clean")
async def clean_geospatial_data(data: GeoJSONData):
    """Clean and validate geospatial data"""
    try:
        cleaned_data = data_processor.clean_data(data.dict())
        
        return {
            "success": True,
            "cleaned_data": cleaned_data,
            "cleaning_report": data_processor.get_cleaning_report()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data cleaning failed: {str(e)}")

@app.post("/api/data/transform")
async def transform_geospatial_data(
    data: GeoJSONData,
    target_crs: str = "EPSG:4326",
    operations: List[str] = []
):
    """Transform geospatial data (projection, simplification, etc.)"""
    try:
        transformed_data = data_processor.transform_data(
            data.dict(),
            target_crs=target_crs,
            operations=operations
        )
        
        return {
            "success": True,
            "transformed_data": transformed_data,
            "target_crs": target_crs,
            "operations": operations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data transformation failed: {str(e)}")

# Visualization Endpoints
@app.post("/api/visualize/map")
async def create_visualization_map(data: GeoJSONData, style: str = "default"):
    """Create interactive visualization maps"""
    try:
        # Load data
        gdf = spatial_analyzer.load_data(data.dict())
        if gdf is None:
            raise HTTPException(status_code=400, detail="Failed to load geospatial data")
        
        # Create visualization
        map_path = visualizer.create_interactive_map(gdf, style=style)
        
        return {
            "success": True,
            "map_path": map_path,
            "download_url": f"/api/files/{os.path.basename(map_path)}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Map creation failed: {str(e)}")

@app.post("/api/visualize/charts")
async def create_data_charts(data: GeoJSONData, chart_types: List[str] = ["bar", "pie"]):
    """Create data visualization charts"""
    try:
        # Load data
        gdf = spatial_analyzer.load_data(data.dict())
        if gdf is None:
            raise HTTPException(status_code=400, detail="Failed to load geospatial data")
        
        # Create charts
        chart_paths = visualizer.create_charts(gdf, chart_types)
        
        return {
            "success": True,
            "chart_paths": chart_paths,
            "chart_types": chart_types
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chart creation failed: {str(e)}")

# File serving endpoint
@app.get("/api/files/{filename}")
async def serve_file(filename: str):
    """Serve generated files (maps, charts, etc.)"""
    file_path = f"output/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="File not found")

# Export endpoints
@app.post("/api/export/analysis")
async def export_analysis_results(data: GeoJSONData, format: str = "json"):
    """Export comprehensive analysis results"""
    try:
        # Load data
        gdf = spatial_analyzer.load_data(data.dict())
        if gdf is None:
            raise HTTPException(status_code=400, detail="Failed to load geospatial data")
        
        # Export results
        export_path = spatial_analyzer.export_analysis_results()
        
        return {
            "success": True,
            "export_path": export_path,
            "format": format,
            "download_url": f"/api/files/{os.path.basename(export_path)}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

# Statistics endpoint
@app.get("/api/stats")
async def get_api_statistics():
    """Get API usage statistics and system information"""
    return {
        "api_version": "1.0.0",
        "uptime": "N/A",  # Would need to track start time
        "endpoints_available": [
            "/api/spatial/analyze",
            "/api/spatial/nearest",
            "/api/spatial/cluster",
            "/api/spatial/density",
            "/api/spatial/accessibility",
            "/api/ml/predict",
            "/api/ml/train",
            "/api/data/import",
            "/api/data/clean",
            "/api/data/transform",
            "/api/visualize/map",
            "/api/visualize/charts",
            "/api/export/analysis"
        ],
        "supported_formats": ["geojson", "shapefile", "kml", "csv"],
        "supported_operations": [
            "spatial_analysis",
            "clustering",
            "density_analysis",
            "accessibility_analysis",
            "ml_prediction",
            "data_import",
            "data_cleaning",
            "data_transformation",
            "visualization"
        ]
    }

if __name__ == "__main__":
    # Create output directory
    os.makedirs("output", exist_ok=True)
    
    # Run the FastAPI server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
