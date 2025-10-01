"""
Data Processing Module for Italy Geospatial Explorer
Handles data import, cleaning, validation, and transformation
"""

import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import transform
import fiona
import json
import os
from typing import Dict, List, Any, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class DataProcessor:
    """
    Comprehensive data processing class for geospatial data
    """
    
    def __init__(self):
        """Initialize the data processor"""
        self.supported_formats = ['geojson', 'shapefile', 'kml', 'csv', 'excel']
        self.cleaning_report = {}
        self.validation_errors = []
        
    def import_data(self, source: str, format: str = 'geojson', options: Dict = None) -> Dict:
        """
        Import geospatial data from various sources and formats
        
        Args:
            source: Path to data source or URL
            format: Data format (geojson, shapefile, kml, csv, excel)
            options: Additional import options
            
        Returns:
            Dictionary with imported data and metadata
        """
        try:
            if format.lower() == 'geojson':
                return self._import_geojson(source, options)
            elif format.lower() == 'shapefile':
                return self._import_shapefile(source, options)
            elif format.lower() == 'kml':
                return self._import_kml(source, options)
            elif format.lower() == 'csv':
                return self._import_csv(source, options)
            elif format.lower() == 'excel':
                return self._import_excel(source, options)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            raise Exception(f"Data import failed: {str(e)}")
    
    def _import_geojson(self, source: str, options: Dict = None) -> Dict:
        """Import GeoJSON data"""
        try:
            if source.startswith('http'):
                # Handle URL sources
                import requests
                response = requests.get(source)
                data = response.json()
            else:
                # Handle file sources
                with open(source, 'r') as f:
                    data = json.load(f)
            
            # Convert to GeoDataFrame
            gdf = gpd.GeoDataFrame.from_features(data['features'])
            
            # Set CRS if not specified
            if gdf.crs is None:
                gdf.crs = 'EPSG:4326'
            
            return {
                'data': gdf,
                'format': 'geojson',
                'source': source,
                'features_count': len(gdf),
                'crs': str(gdf.crs),
                'bounds': gdf.total_bounds.tolist()
            }
            
        except Exception as e:
            raise Exception(f"GeoJSON import failed: {str(e)}")
    
    def _import_shapefile(self, source: str, options: Dict = None) -> Dict:
        """Import Shapefile data"""
        try:
            gdf = gpd.read_file(source)
            
            return {
                'data': gdf,
                'format': 'shapefile',
                'source': source,
                'features_count': len(gdf),
                'crs': str(gdf.crs),
                'bounds': gdf.total_bounds.tolist()
            }
            
        except Exception as e:
            raise Exception(f"Shapefile import failed: {str(e)}")
    
    def _import_kml(self, source: str, options: Dict = None) -> Dict:
        """Import KML data"""
        try:
            gdf = gpd.read_file(source, driver='KML')
            
            return {
                'data': gdf,
                'format': 'kml',
                'source': source,
                'features_count': len(gdf),
                'crs': str(gdf.crs),
                'bounds': gdf.total_bounds.tolist()
            }
            
        except Exception as e:
            raise Exception(f"KML import failed: {str(e)}")
    
    def _import_csv(self, source: str, options: Dict = None) -> Dict:
        """Import CSV data with coordinates"""
        try:
            df = pd.read_csv(source)
            
            # Check for coordinate columns
            lat_col = options.get('lat_column', 'lat') if options else 'lat'
            lon_col = options.get('lon_column', 'lon') if options else 'lon'
            
            if lat_col not in df.columns or lon_col not in df.columns:
                raise ValueError(f"Coordinate columns '{lat_col}' and '{lon_col}' not found")
            
            # Create geometry column
            geometry = [Point(xy) for xy in zip(df[lon_col], df[lat_col])]
            gdf = gpd.GeoDataFrame(df, geometry=geometry)
            gdf.crs = 'EPSG:4326'
            
            return {
                'data': gdf,
                'format': 'csv',
                'source': source,
                'features_count': len(gdf),
                'crs': str(gdf.crs),
                'bounds': gdf.total_bounds.tolist()
            }
            
        except Exception as e:
            raise Exception(f"CSV import failed: {str(e)}")
    
    def _import_excel(self, source: str, options: Dict = None) -> Dict:
        """Import Excel data with coordinates"""
        try:
            sheet_name = options.get('sheet_name', 0) if options else 0
            df = pd.read_excel(source, sheet_name=sheet_name)
            
            # Check for coordinate columns
            lat_col = options.get('lat_column', 'lat') if options else 'lat'
            lon_col = options.get('lon_column', 'lon') if options else 'lon'
            
            if lat_col not in df.columns or lon_col not in df.columns:
                raise ValueError(f"Coordinate columns '{lat_col}' and '{lon_col}' not found")
            
            # Create geometry column
            geometry = [Point(xy) for xy in zip(df[lon_col], df[lat_col])]
            gdf = gpd.GeoDataFrame(df, geometry=geometry)
            gdf.crs = 'EPSG:4326'
            
            return {
                'data': gdf,
                'format': 'excel',
                'source': source,
                'features_count': len(gdf),
                'crs': str(gdf.crs),
                'bounds': gdf.total_bounds.tolist()
            }
            
        except Exception as e:
            raise Exception(f"Excel import failed: {str(e)}")
    
    def clean_data(self, data: Dict) -> Dict:
        """
        Clean and validate geospatial data
        
        Args:
            data: GeoJSON data dictionary
            
        Returns:
            Cleaned data dictionary
        """
        try:
            # Convert to GeoDataFrame
            gdf = gpd.GeoDataFrame.from_features(data['features'])
            
            # Initialize cleaning report
            self.cleaning_report = {
                'original_count': len(gdf),
                'issues_found': [],
                'fixes_applied': [],
                'final_count': 0
            }
            
            # 1. Remove invalid geometries
            invalid_geoms = gdf.geometry.isna() | gdf.geometry.is_empty
            if invalid_geoms.any():
                self.cleaning_report['issues_found'].append(f"Found {invalid_geoms.sum()} invalid geometries")
                gdf = gdf[~invalid_geoms]
                self.cleaning_report['fixes_applied'].append("Removed invalid geometries")
            
            # 2. Fix invalid geometries
            invalid_geoms = ~gdf.geometry.is_valid
            if invalid_geoms.any():
                self.cleaning_report['issues_found'].append(f"Found {invalid_geoms.sum()} invalid geometries")
                gdf.loc[invalid_geoms, 'geometry'] = gdf.loc[invalid_geoms, 'geometry'].buffer(0)
                self.cleaning_report['fixes_applied'].append("Fixed invalid geometries using buffer(0)")
            
            # 3. Remove duplicate geometries
            duplicates = gdf.geometry.duplicated()
            if duplicates.any():
                self.cleaning_report['issues_found'].append(f"Found {duplicates.sum()} duplicate geometries")
                gdf = gdf[~duplicates]
                self.cleaning_report['fixes_applied'].append("Removed duplicate geometries")
            
            # 4. Clean attribute data
            for col in gdf.columns:
                if col != 'geometry':
                    # Remove null values in important columns
                    if col in ['name', 'type', 'description']:
                        gdf[col] = gdf[col].fillna('Unknown')
                    
                    # Clean string columns
                    if gdf[col].dtype == 'object':
                        gdf[col] = gdf[col].astype(str).str.strip()
            
            # 5. Ensure CRS is set
            if gdf.crs is None:
                gdf.crs = 'EPSG:4326'
                self.cleaning_report['fixes_applied'].append("Set CRS to EPSG:4326")
            
            # Update final count
            self.cleaning_report['final_count'] = len(gdf)
            
            # Convert back to GeoJSON
            cleaned_data = {
                'type': 'FeatureCollection',
                'features': json.loads(gdf.to_json())['features']
            }
            
            return cleaned_data
            
        except Exception as e:
            raise Exception(f"Data cleaning failed: {str(e)}")
    
    def transform_data(self, data: Dict, target_crs: str = 'EPSG:4326', operations: List[str] = None) -> Dict:
        """
        Transform geospatial data (projection, simplification, etc.)
        
        Args:
            data: GeoJSON data dictionary
            target_crs: Target coordinate reference system
            operations: List of transformation operations
            
        Returns:
            Transformed data dictionary
        """
        try:
            # Convert to GeoDataFrame
            gdf = gpd.GeoDataFrame.from_features(data['features'])
            
            # Set source CRS if not set
            if gdf.crs is None:
                gdf.crs = 'EPSG:4326'
            
            # Transform CRS if needed
            if str(gdf.crs) != target_crs:
                gdf = gdf.to_crs(target_crs)
            
            # Apply transformation operations
            if operations:
                for operation in operations:
                    if operation == 'simplify':
                        # Simplify geometries
                        tolerance = 0.001  # Adjust as needed
                        gdf['geometry'] = gdf.geometry.simplify(tolerance)
                    
                    elif operation == 'buffer':
                        # Apply buffer
                        buffer_distance = 0.01  # Adjust as needed
                        gdf['geometry'] = gdf.geometry.buffer(buffer_distance)
                    
                    elif operation == 'convex_hull':
                        # Create convex hulls
                        gdf['geometry'] = gdf.geometry.convex_hull
                    
                    elif operation == 'centroid':
                        # Convert to centroids
                        gdf['geometry'] = gdf.geometry.centroid
            
            # Convert back to GeoJSON
            transformed_data = {
                'type': 'FeatureCollection',
                'features': json.loads(gdf.to_json())['features']
            }
            
            return transformed_data
            
        except Exception as e:
            raise Exception(f"Data transformation failed: {str(e)}")
    
    def validate_data(self, data: Dict) -> Dict:
        """
        Validate geospatial data quality
        
        Args:
            data: GeoJSON data dictionary
            
        Returns:
            Validation results dictionary
        """
        try:
            # Convert to GeoDataFrame
            gdf = gpd.GeoDataFrame.from_features(data['features'])
            
            validation_results = {
                'total_features': len(gdf),
                'valid_geometries': gdf.geometry.is_valid.sum(),
                'invalid_geometries': (~gdf.geometry.is_valid).sum(),
                'empty_geometries': gdf.geometry.is_empty.sum(),
                'null_geometries': gdf.geometry.isna().sum(),
                'duplicate_geometries': gdf.geometry.duplicated().sum(),
                'crs_defined': gdf.crs is not None,
                'bounds': gdf.total_bounds.tolist() if len(gdf) > 0 else None,
                'geometry_types': gdf.geometry.geom_type.value_counts().to_dict(),
                'attribute_columns': list(gdf.columns),
                'missing_values': gdf.isnull().sum().to_dict()
            }
            
            # Calculate quality score
            quality_score = 0
            if validation_results['valid_geometries'] == validation_results['total_features']:
                quality_score += 40
            if validation_results['empty_geometries'] == 0:
                quality_score += 20
            if validation_results['null_geometries'] == 0:
                quality_score += 20
            if validation_results['duplicate_geometries'] == 0:
                quality_score += 20
            
            validation_results['quality_score'] = quality_score
            validation_results['quality_grade'] = self._get_quality_grade(quality_score)
            
            return validation_results
            
        except Exception as e:
            raise Exception(f"Data validation failed: {str(e)}")
    
    def _get_quality_grade(self, score: int) -> str:
        """Get quality grade based on score"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def export_data(self, data: Dict, output_path: str, format: str = 'geojson') -> str:
        """
        Export geospatial data to various formats
        
        Args:
            data: GeoJSON data dictionary
            output_path: Output file path
            format: Output format
            
        Returns:
            Path to exported file
        """
        try:
            # Convert to GeoDataFrame
            gdf = gpd.GeoDataFrame.from_features(data['features'])
            
            if format.lower() == 'geojson':
                gdf.to_file(output_path, driver='GeoJSON')
            elif format.lower() == 'shapefile':
                gdf.to_file(output_path, driver='ESRI Shapefile')
            elif format.lower() == 'kml':
                gdf.to_file(output_path, driver='KML')
            elif format.lower() == 'csv':
                # Export as CSV with coordinates
                df = gdf.drop('geometry', axis=1)
                df['lat'] = gdf.geometry.y
                df['lon'] = gdf.geometry.x
                df.to_csv(output_path, index=False)
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Data export failed: {str(e)}")
    
    def get_cleaning_report(self) -> Dict:
        """Get the latest cleaning report"""
        return self.cleaning_report
    
    def get_validation_errors(self) -> List[str]:
        """Get validation errors"""
        return self.validation_errors

# Example usage and testing
if __name__ == "__main__":
    # Sample Italian landmarks data
    sample_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": 1,
                "properties": {
                    "name": "Colosseum",
                    "description": "Ancient Roman amphitheater in Rome",
                    "type": "monument"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [12.4922, 41.8902]
                }
            },
            {
                "type": "Feature",
                "id": 2,
                "properties": {
                    "name": "Leaning Tower of Pisa",
                    "description": "Famous bell tower in Pisa",
                    "type": "monument"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [10.3966, 43.7230]
                }
            }
        ]
    }
    
    # Initialize processor
    processor = DataProcessor()
    
    # Test data cleaning
    print("🧹 Testing data cleaning...")
    cleaned_data = processor.clean_data(sample_data)
    print(f"✅ Cleaned data: {len(cleaned_data['features'])} features")
    
    # Test data validation
    print("🔍 Testing data validation...")
    validation_results = processor.validate_data(cleaned_data)
    print(f"✅ Quality score: {validation_results['quality_score']}/100")
    print(f"✅ Quality grade: {validation_results['quality_grade']}")
    
    # Test data transformation
    print("🔄 Testing data transformation...")
    transformed_data = processor.transform_data(cleaned_data, operations=['simplify'])
    print(f"✅ Transformed data: {len(transformed_data['features'])} features")
    
    print("🎉 Data processing tests completed successfully!")
