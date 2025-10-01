"""
Database Integration Module for Italy Geospatial Explorer
Handles all database operations with PostgreSQL and PostGIS
"""

import psycopg2
from psycopg2.extras import RealDictCursor, Json
import geopandas as gpd
import pandas as pd
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DatabaseIntegration:
    """
    Comprehensive database integration class for geospatial operations
    """
    
    def __init__(self, connection_params: Dict = None):
        """
        Initialize database connection
        
        Args:
            connection_params: Database connection parameters
        """
        self.connection_params = connection_params or {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'geospatial_db'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password')
        }
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(**self.connection_params)
            self.connection.autocommit = True
            logger.info("✅ Database connected successfully")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            self.connection = None
    
    def get_connection(self):
        """Get database connection, reconnect if necessary"""
        if self.connection is None or self.connection.closed:
            self.connect()
        return self.connection
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = True):
        """
        Execute database query
        
        Args:
            query: SQL query string
            params: Query parameters
            fetch: Whether to fetch results
            
        Returns:
            Query results or row count
        """
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                if fetch and query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                else:
                    conn.commit()
                    return cursor.rowcount
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            raise Exception(f"Database error: {str(e)}")
    
    def initialize_database(self):
        """Initialize database schema and extensions"""
        try:
            # Enable PostGIS extension
            self.execute_query("CREATE EXTENSION IF NOT EXISTS postgis;", fetch=False)
            
            # Create geospatial_data table
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
            self.execute_query(create_table_query, fetch=False)
            
            # Create spatial index
            create_spatial_index_query = """
            CREATE INDEX IF NOT EXISTS idx_geospatial_geometry 
            ON geospatial_data USING GIST (geometry);
            """
            self.execute_query(create_spatial_index_query, fetch=False)
            
            # Create properties index
            create_properties_index_query = """
            CREATE INDEX IF NOT EXISTS idx_geospatial_properties 
            ON geospatial_data USING GIN (properties);
            """
            self.execute_query(create_properties_index_query, fetch=False)
            
            # Create landmark_type index
            create_type_index_query = """
            CREATE INDEX IF NOT EXISTS idx_geospatial_type 
            ON geospatial_data (landmark_type);
            """
            self.execute_query(create_type_index_query, fetch=False)
            
            # Create analysis_results table
            create_analysis_table_query = """
            CREATE TABLE IF NOT EXISTS analysis_results (
                id SERIAL PRIMARY KEY,
                analysis_type VARCHAR(100) NOT NULL,
                parameters JSONB,
                results JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            self.execute_query(create_analysis_table_query, fetch=False)
            
            # Create user_sessions table for tracking
            create_sessions_table_query = """
            CREATE TABLE IF NOT EXISTS user_sessions (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) UNIQUE,
                user_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            self.execute_query(create_sessions_table_query, fetch=False)
            
            logger.info("✅ Database schema initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise Exception(f"Database initialization failed: {str(e)}")
    
    def insert_landmark(self, name: str, description: str, landmark_type: str, 
                       geometry_wkt: str, properties: Dict = None) -> int:
        """
        Insert a new landmark into the database
        
        Args:
            name: Landmark name
            description: Landmark description
            landmark_type: Type of landmark
            geometry_wkt: Geometry in WKT format
            properties: Additional properties
            
        Returns:
            ID of the inserted landmark
        """
        try:
            insert_query = """
            INSERT INTO geospatial_data (name, description, landmark_type, geometry, properties)
            VALUES (%s, %s, %s, ST_GeomFromText(%s, 4326), %s)
            RETURNING id
            """
            
            result = self.execute_query(insert_query, (
                name, description, landmark_type, geometry_wkt, 
                json.dumps(properties) if properties else None
            ))
            
            return result[0]['id'] if result else None
            
        except Exception as e:
            logger.error(f"Failed to insert landmark: {e}")
            raise Exception(f"Landmark insertion failed: {str(e)}")
    
    def get_landmarks(self, limit: int = 100, offset: int = 0, 
                     landmark_type: str = None, bounds: Dict = None) -> List[Dict]:
        """
        Get landmarks with optional filtering
        
        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            landmark_type: Filter by landmark type
            bounds: Spatial bounds filter
            
        Returns:
            List of landmark dictionaries
        """
        try:
            query = """
            SELECT id, name, description, landmark_type, 
                   ST_AsGeoJSON(geometry) as geometry, properties, created_at, updated_at
            FROM geospatial_data
            WHERE 1=1
            """
            params = []
            
            if landmark_type:
                query += " AND landmark_type = %s"
                params.append(landmark_type)
            
            if bounds:
                query += """
                AND ST_Intersects(geometry, ST_MakeEnvelope(%s, %s, %s, %s, 4326))
                """
                params.extend([bounds['min_lon'], bounds['min_lat'], 
                              bounds['max_lon'], bounds['max_lat']])
            
            query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            results = self.execute_query(query, tuple(params))
            
            landmarks = []
            for row in results:
                landmark = {
                    'id': row['id'],
                    'name': row['name'],
                    'description': row['description'],
                    'landmark_type': row['landmark_type'],
                    'geometry': json.loads(row['geometry']),
                    'properties': json.loads(row['properties']) if row['properties'] else {},
                    'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                    'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None
                }
                landmarks.append(landmark)
            
            return landmarks
            
        except Exception as e:
            logger.error(f"Failed to get landmarks: {e}")
            raise Exception(f"Failed to retrieve landmarks: {str(e)}")
    
    def update_landmark(self, landmark_id: int, name: str = None, description: str = None,
                       landmark_type: str = None, geometry_wkt: str = None, 
                       properties: Dict = None) -> bool:
        """
        Update an existing landmark
        
        Args:
            landmark_id: ID of the landmark to update
            name: New name
            description: New description
            landmark_type: New type
            geometry_wkt: New geometry in WKT format
            properties: New properties
            
        Returns:
            True if update was successful
        """
        try:
            update_fields = []
            params = []
            
            if name is not None:
                update_fields.append("name = %s")
                params.append(name)
            
            if description is not None:
                update_fields.append("description = %s")
                params.append(description)
            
            if landmark_type is not None:
                update_fields.append("landmark_type = %s")
                params.append(landmark_type)
            
            if geometry_wkt is not None:
                update_fields.append("geometry = ST_GeomFromText(%s, 4326)")
                params.append(geometry_wkt)
            
            if properties is not None:
                update_fields.append("properties = %s")
                params.append(json.dumps(properties))
            
            if not update_fields:
                return False
            
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            params.append(landmark_id)
            
            query = f"""
            UPDATE geospatial_data 
            SET {', '.join(update_fields)}
            WHERE id = %s
            """
            
            result = self.execute_query(query, tuple(params), fetch=False)
            return result > 0
            
        except Exception as e:
            logger.error(f"Failed to update landmark: {e}")
            raise Exception(f"Landmark update failed: {str(e)}")
    
    def delete_landmark(self, landmark_id: int) -> bool:
        """
        Delete a landmark
        
        Args:
            landmark_id: ID of the landmark to delete
            
        Returns:
            True if deletion was successful
        """
        try:
            delete_query = "DELETE FROM geospatial_data WHERE id = %s"
            result = self.execute_query(delete_query, (landmark_id,), fetch=False)
            return result > 0
            
        except Exception as e:
            logger.error(f"Failed to delete landmark: {e}")
            raise Exception(f"Landmark deletion failed: {str(e)}")
    
    def spatial_query(self, lat: float, lon: float, radius: float = None, 
                     limit: int = 10) -> List[Dict]:
        """
        Perform spatial queries on landmarks
        
        Args:
            lat: Latitude of query point
            lon: Longitude of query point
            radius: Search radius in meters
            limit: Maximum number of results
            
        Returns:
            List of nearby landmarks
        """
        try:
            if radius:
                # Find landmarks within radius
                query = """
                SELECT id, name, description, landmark_type, 
                       ST_AsGeoJSON(geometry) as geometry, properties,
                       ST_Distance(geometry, ST_GeomFromText(%s, 4326)) as distance
                FROM geospatial_data
                WHERE ST_DWithin(geometry, ST_GeomFromText(%s, 4326), %s)
                ORDER BY distance
                LIMIT %s
                """
                point_wkt = f"POINT({lon} {lat})"
                results = self.execute_query(query, (point_wkt, point_wkt, radius, limit))
            else:
                # Find nearest landmarks
                query = """
                SELECT id, name, description, landmark_type, 
                       ST_AsGeoJSON(geometry) as geometry, properties,
                       ST_Distance(geometry, ST_GeomFromText(%s, 4326)) as distance
                FROM geospatial_data
                ORDER BY distance
                LIMIT %s
                """
                point_wkt = f"POINT({lon} {lat})"
                results = self.execute_query(query, (point_wkt, limit))
            
            landmarks = []
            for row in results:
                landmark = {
                    'id': row['id'],
                    'name': row['name'],
                    'description': row['description'],
                    'landmark_type': row['landmark_type'],
                    'geometry': json.loads(row['geometry']),
                    'properties': json.loads(row['properties']) if row['properties'] else {},
                    'distance': float(row['distance']) if row['distance'] else 0
                }
                landmarks.append(landmark)
            
            return landmarks
            
        except Exception as e:
            logger.error(f"Spatial query failed: {e}")
            raise Exception(f"Spatial query failed: {str(e)}")
    
    def get_statistics(self) -> Dict:
        """
        Get comprehensive database statistics
        
        Returns:
            Dictionary with statistics
        """
        try:
            # Total landmarks
            total_query = "SELECT COUNT(*) as total FROM geospatial_data"
            total_result = self.execute_query(total_query)
            
            # Type distribution
            type_query = """
            SELECT landmark_type, COUNT(*) as count 
            FROM geospatial_data 
            GROUP BY landmark_type
            """
            type_results = self.execute_query(type_query)
            
            # Spatial bounds
            bounds_query = """
            SELECT 
                ST_XMin(ST_Extent(geometry)) as min_lon,
                ST_YMin(ST_Extent(geometry)) as min_lat,
                ST_XMax(ST_Extent(geometry)) as max_lon,
                ST_YMax(ST_Extent(geometry)) as max_lat
            FROM geospatial_data
            """
            bounds_result = self.execute_query(bounds_query)
            
            # Recent activity
            recent_query = """
            SELECT COUNT(*) as recent_count
            FROM geospatial_data
            WHERE created_at > NOW() - INTERVAL '7 days'
            """
            recent_result = self.execute_query(recent_query)
            
            statistics = {
                'total_landmarks': total_result[0]['total'] if total_result else 0,
                'type_distribution': {row['landmark_type']: row['count'] for row in type_results},
                'spatial_bounds': {
                    'min_lon': float(bounds_result[0]['min_lon']) if bounds_result and bounds_result[0]['min_lon'] else 0,
                    'min_lat': float(bounds_result[0]['min_lat']) if bounds_result and bounds_result[0]['min_lat'] else 0,
                    'max_lon': float(bounds_result[0]['max_lon']) if bounds_result and bounds_result[0]['max_lon'] else 0,
                    'max_lat': float(bounds_result[0]['max_lat']) if bounds_result and bounds_result[0]['max_lat'] else 0
                },
                'recent_activity': recent_result[0]['recent_count'] if recent_result else 0,
                'last_updated': datetime.now().isoformat()
            }
            
            return statistics
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            raise Exception(f"Statistics retrieval failed: {str(e)}")
    
    def save_analysis_results(self, analysis_type: str, parameters: Dict, 
                            results: Dict) -> int:
        """
        Save analysis results to database
        
        Args:
            analysis_type: Type of analysis performed
            parameters: Analysis parameters
            results: Analysis results
            
        Returns:
            ID of the saved analysis
        """
        try:
            insert_query = """
            INSERT INTO analysis_results (analysis_type, parameters, results)
            VALUES (%s, %s, %s)
            RETURNING id
            """
            
            result = self.execute_query(insert_query, (
                analysis_type,
                json.dumps(parameters),
                json.dumps(results)
            ))
            
            return result[0]['id'] if result else None
            
        except Exception as e:
            logger.error(f"Failed to save analysis results: {e}")
            raise Exception(f"Analysis results save failed: {str(e)}")
    
    def get_analysis_history(self, limit: int = 50) -> List[Dict]:
        """
        Get analysis history
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of analysis records
        """
        try:
            query = """
            SELECT id, analysis_type, parameters, results, created_at
            FROM analysis_results
            ORDER BY created_at DESC
            LIMIT %s
            """
            
            results = self.execute_query(query, (limit,))
            
            analyses = []
            for row in results:
                analysis = {
                    'id': row['id'],
                    'analysis_type': row['analysis_type'],
                    'parameters': json.loads(row['parameters']) if row['parameters'] else {},
                    'results': json.loads(row['results']) if row['results'] else {},
                    'created_at': row['created_at'].isoformat() if row['created_at'] else None
                }
                analyses.append(analysis)
            
            return analyses
            
        except Exception as e:
            logger.error(f"Failed to get analysis history: {e}")
            raise Exception(f"Analysis history retrieval failed: {str(e)}")
    
    def export_to_geojson(self, landmark_type: str = None) -> Dict:
        """
        Export landmarks to GeoJSON format
        
        Args:
            landmark_type: Filter by landmark type
            
        Returns:
            GeoJSON FeatureCollection
        """
        try:
            landmarks = self.get_landmarks(limit=10000, landmark_type=landmark_type)
            
            features = []
            for landmark in landmarks:
                feature = {
                    'type': 'Feature',
                    'id': landmark['id'],
                    'properties': {
                        'name': landmark['name'],
                        'description': landmark['description'],
                        'type': landmark['landmark_type'],
                        **landmark['properties']
                    },
                    'geometry': landmark['geometry']
                }
                features.append(feature)
            
            return {
                'type': 'FeatureCollection',
                'features': features
            }
            
        except Exception as e:
            logger.error(f"Failed to export to GeoJSON: {e}")
            raise Exception(f"GeoJSON export failed: {str(e)}")
    
    def import_from_geojson(self, geojson_data: Dict) -> int:
        """
        Import landmarks from GeoJSON data
        
        Args:
            geojson_data: GeoJSON FeatureCollection
            
        Returns:
            Number of imported features
        """
        try:
            imported_count = 0
            
            for feature in geojson_data.get('features', []):
                properties = feature.get('properties', {})
                geometry = feature.get('geometry', {})
                
                if geometry.get('type') == 'Point':
                    coords = geometry.get('coordinates', [])
                    if len(coords) >= 2:
                        geometry_wkt = f"POINT({coords[0]} {coords[1]})"
                        
                        landmark_id = self.insert_landmark(
                            name=properties.get('name', f'Imported Feature {imported_count}'),
                            description=properties.get('description', ''),
                            landmark_type=properties.get('type', 'unknown'),
                            geometry_wkt=geometry_wkt,
                            properties=properties
                        )
                        
                        if landmark_id:
                            imported_count += 1
            
            return imported_count
            
        except Exception as e:
            logger.error(f"Failed to import from GeoJSON: {e}")
            raise Exception(f"GeoJSON import failed: {str(e)}")
    
    def close(self):
        """Close database connection"""
        if self.connection and not self.connection.closed:
            self.connection.close()
            logger.info("Database connection closed")

# Example usage and testing
if __name__ == "__main__":
    # Initialize database integration
    db = DatabaseIntegration()
    
    try:
        # Initialize database schema
        print("🗄️ Initializing database...")
        db.initialize_database()
        
        # Test statistics
        print("📊 Getting statistics...")
        stats = db.get_statistics()
        print(f"✅ Total landmarks: {stats['total_landmarks']}")
        print(f"✅ Type distribution: {stats['type_distribution']}")
        
        # Test spatial query
        print("🔍 Testing spatial query...")
        nearby = db.spatial_query(41.9028, 12.4964, limit=5)
        print(f"✅ Found {len(nearby)} nearby landmarks")
        
        print("🎉 Database integration tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Database integration test failed: {e}")
    
    finally:
        db.close()
