"""
Advanced Spatial Analysis Module for Italy Geospatial Explorer
Provides sophisticated spatial analysis capabilities using Python geospatial libraries
"""

import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import nearest_points
from geopy.distance import geodesic
import folium
from folium import plugins
import json
from typing import List, Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class SpatialAnalyzer:
    """
    Advanced spatial analysis class for geospatial data processing and analysis
    """
    
    def __init__(self, data_source: str = None):
        """
        Initialize the spatial analyzer
        
        Args:
            data_source: Path to geospatial data file or database connection
        """
        self.data_source = data_source
        self.gdf = None
        self.italy_bounds = {
            'min_lat': 35.5, 'max_lat': 47.1,
            'min_lon': 6.6, 'max_lon': 18.5
        }
    
    def load_data(self, data: Dict) -> gpd.GeoDataFrame:
        """
        Load geospatial data from GeoJSON or database
        
        Args:
            data: GeoJSON data dictionary
            
        Returns:
            GeoDataFrame with spatial data
        """
        try:
            # Convert GeoJSON to GeoDataFrame
            self.gdf = gpd.GeoDataFrame.from_features(data['features'])
            
            # Ensure CRS is set to WGS84
            if self.gdf.crs is None:
                self.gdf.crs = 'EPSG:4326'
            
            # Add spatial columns for analysis
            self.gdf['centroid_lat'] = self.gdf.geometry.centroid.y
            self.gdf['centroid_lon'] = self.gdf.geometry.centroid.x
            self.gdf['area_sqkm'] = self.gdf.geometry.area * 111 * 111  # Rough conversion
            self.gdf['perimeter_km'] = self.gdf.geometry.length * 111  # Rough conversion
            
            return self.gdf
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    
    def find_nearest_landmarks(self, lat: float, lon: float, n: int = 5) -> List[Dict]:
        """
        Find the nearest landmarks to a given point
        
        Args:
            lat: Latitude of the query point
            lon: Longitude of the query point
            n: Number of nearest landmarks to return
            
        Returns:
            List of nearest landmarks with distances
        """
        if self.gdf is None:
            return []
        
        query_point = Point(lon, lat)
        distances = []
        
        for idx, row in self.gdf.iterrows():
            # Calculate distance using geodesic for accuracy
            landmark_point = Point(row['centroid_lon'], row['centroid_lat'])
            distance_km = geodesic(
                (lat, lon), 
                (row['centroid_lat'], row['centroid_lon'])
            ).kilometers
            
            distances.append({
                'id': row.get('id', idx),
                'name': row.get('name', f'Landmark {idx}'),
                'description': row.get('description', ''),
                'type': row.get('type', 'unknown'),
                'distance_km': round(distance_km, 2),
                'geometry': row.geometry,
                'properties': row.to_dict()
            })
        
        # Sort by distance and return top n
        distances.sort(key=lambda x: x['distance_km'])
        return distances[:n]
    
    def spatial_clustering(self, method: str = 'kmeans', n_clusters: int = 3) -> Dict:
        """
        Perform spatial clustering analysis on landmarks
        
        Args:
            method: Clustering method ('kmeans', 'dbscan', 'hierarchical')
            n_clusters: Number of clusters for kmeans
            
        Returns:
            Dictionary with clustering results
        """
        if self.gdf is None:
            return {}
        
        from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
        from sklearn.preprocessing import StandardScaler
        
        # Prepare coordinates for clustering
        coords = np.array([[row['centroid_lon'], [row['centroid_lat']]] for _, row in self.gdf.iterrows())
        coords = coords.reshape(-1, 2)
        
        # Standardize coordinates
        scaler = StandardScaler()
        coords_scaled = scaler.fit_transform(coords)
        
        if method == 'kmeans':
            clusterer = KMeans(n_clusters=n_clusters, random_state=42)
            labels = clusterer.fit_predict(coords_scaled)
        elif method == 'dbscan':
            clusterer = DBSCAN(eps=0.5, min_samples=2)
            labels = clusterer.fit_predict(coords_scaled)
        elif method == 'hierarchical':
            clusterer = AgglomerativeClustering(n_clusters=n_clusters)
            labels = clusterer.fit_predict(coords_scaled)
        else:
            raise ValueError("Method must be 'kmeans', 'dbscan', or 'hierarchical'")
        
        # Add cluster labels to dataframe
        self.gdf['cluster'] = labels
        
        # Calculate cluster statistics
        cluster_stats = {}
        for cluster_id in np.unique(labels):
            if cluster_id == -1:  # Skip noise points in DBSCAN
                continue
            cluster_data = self.gdf[self.gdf['cluster'] == cluster_id]
            cluster_stats[cluster_id] = {
                'count': len(cluster_data),
                'centroid_lat': cluster_data['centroid_lat'].mean(),
                'centroid_lon': cluster_data['centroid_lon'].mean(),
                'landmarks': cluster_data['name'].tolist()
            }
        
        return {
            'labels': labels.tolist(),
            'cluster_stats': cluster_stats,
            'method': method,
            'n_clusters': len(np.unique(labels))
        }
    
    def density_analysis(self, grid_size: float = 0.1) -> Dict:
        """
        Perform density analysis on landmark distribution
        
        Args:
            grid_size: Size of grid cells in degrees
            
        Returns:
            Dictionary with density analysis results
        """
        if self.gdf is None:
            return {}
        
        # Create grid for density analysis
        min_lon, max_lon = self.gdf['centroid_lon'].min(), self.gdf['centroid_lon'].max()
        min_lat, max_lat = self.gdf['centroid_lat'].min(), self.gdf['centroid_lat'].max()
        
        # Create grid cells
        grid_cells = []
        for lon in np.arange(min_lon, max_lon, grid_size):
            for lat in np.arange(min_lat, max_lat, grid_size):
                cell = Polygon([
                    (lon, lat),
                    (lon + grid_size, lat),
                    (lon + grid_size, lat + grid_size),
                    (lon, lat + grid_size)
                ])
                grid_cells.append(cell)
        
        # Count landmarks in each grid cell
        density_data = []
        for i, cell in enumerate(grid_cells):
            count = 0
            for _, landmark in self.gdf.iterrows():
                if cell.contains(landmark.geometry.centroid):
                    count += 1
            
            if count > 0:
                density_data.append({
                    'cell_id': i,
                    'geometry': cell,
                    'landmark_count': count,
                    'density': count / (grid_size * grid_size),
                    'center_lat': cell.centroid.y,
                    'center_lon': cell.centroid.x
                })
        
        return {
            'density_data': density_data,
            'max_density': max([d['density'] for d in density_data]) if density_data else 0,
            'total_cells': len(grid_cells),
            'occupied_cells': len(density_data)
        }
    
    def accessibility_analysis(self, transport_speed: float = 50.0) -> Dict:
        """
        Analyze accessibility of landmarks using travel time estimates
        
        Args:
            transport_speed: Average transport speed in km/h
            
        Returns:
            Dictionary with accessibility analysis
        """
        if self.gdf is None:
            return {}
        
        accessibility_data = []
        
        for idx, landmark in self.gdf.iterrows():
            # Calculate distances to all other landmarks
            distances = []
            for other_idx, other_landmark in self.gdf.iterrows():
                if idx != other_idx:
                    distance = geodesic(
                        (landmark['centroid_lat'], landmark['centroid_lon']),
                        (other_landmark['centroid_lat'], other_landmark['centroid_lon'])
                    ).kilometers
                    distances.append(distance)
            
            # Calculate accessibility metrics
            avg_distance = np.mean(distances) if distances else 0
            min_distance = np.min(distances) if distances else 0
            max_distance = np.max(distances) if distances else 0
            
            # Calculate travel times
            avg_travel_time = avg_distance / transport_speed
            min_travel_time = min_distance / transport_speed
            max_travel_time = max_distance / transport_speed
            
            accessibility_data.append({
                'landmark_id': landmark.get('id', idx),
                'name': landmark.get('name', f'Landmark {idx}'),
                'avg_distance_km': round(avg_distance, 2),
                'min_distance_km': round(min_distance, 2),
                'max_distance_km': round(max_distance, 2),
                'avg_travel_time_hours': round(avg_travel_time, 2),
                'min_travel_time_hours': round(min_travel_time, 2),
                'max_travel_time_hours': round(max_travel_time, 2),
                'accessibility_score': round(1 / (avg_distance + 1), 4)  # Higher score = more accessible
            })
        
        return {
            'accessibility_data': accessibility_data,
            'most_accessible': max(accessibility_data, key=lambda x: x['accessibility_score']),
            'least_accessible': min(accessibility_data, key=lambda x: x['accessibility_score'])
        }
    
    def create_interactive_map(self, output_path: str = 'italy_analysis_map.html') -> str:
        """
        Create an interactive Folium map with analysis results
        
        Args:
            output_path: Path to save the HTML map
            
        Returns:
            Path to the created map file
        """
        if self.gdf is None:
            return None
        
        # Create base map centered on Italy
        italy_center = [41.8719, 12.5674]  # Center of Italy
        m = folium.Map(
            location=italy_center,
            zoom_start=6,
            tiles='OpenStreetMap'
        )
        
        # Add landmark markers
        for idx, row in self.gdf.iterrows():
            # Determine marker color based on type
            color_map = {
                'monument': 'red',
                'cathedral': 'blue',
                'waterway': 'lightblue',
                'city-state': 'green',
                'coastline': 'orange',
                'lake': 'darkblue',
                'archaeological_site': 'purple'
            }
            color = color_map.get(row.get('type', 'unknown'), 'gray')
            
            # Create popup content
            popup_content = f"""
            <b>{row.get('name', 'Unnamed')}</b><br>
            <i>{row.get('type', 'Unknown type')}</i><br>
            {row.get('description', 'No description')}<br>
            <small>Area: {row.get('area_sqkm', 0):.2f} km²</small>
            """
            
            # Add marker
            folium.Marker(
                [row['centroid_lat'], row['centroid_lon']],
                popup=folium.Popup(popup_content, max_width=300),
                icon=folium.Icon(color=color, icon='info-sign')
            ).add_to(m)
        
        # Add heatmap if clustering was performed
        if 'cluster' in self.gdf.columns:
            from folium.plugins import HeatMap
            heat_data = [[row['centroid_lat'], row['centroid_lon']] for _, row in self.gdf.iterrows()]
            HeatMap(heat_data).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Save map
        m.save(output_path)
        return output_path
    
    def export_analysis_results(self, output_path: str = 'spatial_analysis_results.json') -> str:
        """
        Export analysis results to JSON file
        
        Args:
            output_path: Path to save the results
            
        Returns:
            Path to the saved file
        """
        if self.gdf is None:
            return None
        
        results = {
            'metadata': {
                'total_landmarks': len(self.gdf),
                'analysis_date': pd.Timestamp.now().isoformat(),
                'crs': str(self.gdf.crs)
            },
            'landmarks': []
        }
        
        for idx, row in self.gdf.iterrows():
            landmark_data = {
                'id': row.get('id', idx),
                'name': row.get('name', f'Landmark {idx}'),
                'type': row.get('type', 'unknown'),
                'description': row.get('description', ''),
                'coordinates': {
                    'lat': row['centroid_lat'],
                    'lon': row['centroid_lon']
                },
                'geometry': row.geometry.wkt if hasattr(row.geometry, 'wkt') else str(row.geometry),
                'area_sqkm': row.get('area_sqkm', 0),
                'perimeter_km': row.get('perimeter_km', 0)
            }
            
            # Add cluster information if available
            if 'cluster' in row:
                landmark_data['cluster'] = row['cluster']
            
            results['landmarks'].append(landmark_data)
        
        # Save results
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        return output_path

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
    
    # Initialize analyzer
    analyzer = SpatialAnalyzer()
    gdf = analyzer.load_data(sample_data)
    
    if gdf is not None:
        print("✅ Spatial analyzer initialized successfully")
        print(f"📊 Loaded {len(gdf)} landmarks")
        
        # Perform nearest neighbor analysis
        nearest = analyzer.find_nearest_landmarks(41.9028, 12.4964, n=3)
        print(f"🔍 Found {len(nearest)} nearest landmarks to Rome")
        
        # Create interactive map
        map_path = analyzer.create_interactive_map()
        print(f"🗺️ Interactive map saved to: {map_path}")
        
        # Export results
        results_path = analyzer.export_analysis_results()
        print(f"📄 Analysis results saved to: {results_path}")
    else:
        print("❌ Failed to initialize spatial analyzer")
