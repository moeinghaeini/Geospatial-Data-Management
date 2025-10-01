"""
Advanced Visualization Module for Italy Geospatial Explorer
Provides sophisticated data visualization capabilities using Python libraries
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from folium import plugins
import json
import os
from typing import Dict, List, Any, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class AdvancedVisualizer:
    """
    Advanced visualization class for geospatial data
    """
    
    def __init__(self):
        """Initialize the visualizer"""
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Set style for matplotlib
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
    def create_interactive_map(self, gdf: gpd.GeoDataFrame, style: str = "default") -> str:
        """
        Create interactive Folium map with advanced features
        
        Args:
            gdf: GeoDataFrame with spatial data
            style: Map style ('default', 'dark', 'satellite', 'terrain')
            
        Returns:
            Path to the created map file
        """
        try:
            # Map style configurations
            style_configs = {
                'default': {
                    'tiles': 'OpenStreetMap',
                    'zoom_start': 6,
                    'location': [41.8719, 12.5674]  # Center of Italy
                },
                'dark': {
                    'tiles': 'CartoDB dark_matter',
                    'zoom_start': 6,
                    'location': [41.8719, 12.5674]
                },
                'satellite': {
                    'tiles': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                    'attr': 'Esri',
                    'zoom_start': 6,
                    'location': [41.8719, 12.5674]
                },
                'terrain': {
                    'tiles': 'Stamen Terrain',
                    'zoom_start': 6,
                    'location': [41.8719, 12.5674]
                }
            }
            
            config = style_configs.get(style, style_configs['default'])
            
            # Create base map
            m = folium.Map(
                location=config['location'],
                zoom_start=config['zoom_start'],
                tiles=config['tiles'],
                attr=config.get('attr', '')
            )
            
            # Add landmark markers with clustering
            marker_cluster = plugins.MarkerCluster().add_to(m)
            
            # Color mapping for different landmark types
            color_map = {
                'monument': 'red',
                'cathedral': 'blue',
                'waterway': 'lightblue',
                'city-state': 'green',
                'coastline': 'orange',
                'lake': 'darkblue',
                'archaeological_site': 'purple',
                'default': 'gray'
            }
            
            # Add markers for each landmark
            for idx, row in gdf.iterrows():
                # Get coordinates
                if hasattr(row.geometry, 'centroid'):
                    lat, lon = row.geometry.centroid.y, row.geometry.centroid.x
                else:
                    continue
                
                # Determine marker color
                landmark_type = row.get('type', 'default')
                color = color_map.get(landmark_type, color_map['default'])
                
                # Create popup content
                popup_content = self._create_popup_content(row)
                
                # Add marker
                folium.Marker(
                    [lat, lon],
                    popup=folium.Popup(popup_content, max_width=300),
                    icon=folium.Icon(color=color, icon='info-sign'),
                    tooltip=row.get('name', 'Unnamed Landmark')
                ).add_to(marker_cluster)
            
            # Add heatmap layer
            if len(gdf) > 1:
                heat_data = [[row.geometry.centroid.y, row.geometry.centroid.x] for _, row in gdf.iterrows()]
                plugins.HeatMap(heat_data, name='Landmark Density').add_to(m)
            
            # Add layer control
            folium.LayerControl().add_to(m)
            
            # Add fullscreen button
            plugins.Fullscreen().add_to(m)
            
            # Add measure control
            plugins.MeasureControl().add_to(m)
            
            # Save map
            map_filename = f"italy_landmarks_map_{style}.html"
            map_path = os.path.join(self.output_dir, map_filename)
            m.save(map_path)
            
            return map_path
            
        except Exception as e:
            raise Exception(f"Interactive map creation failed: {str(e)}")
    
    def _create_popup_content(self, row: pd.Series) -> str:
        """Create HTML popup content for landmarks"""
        name = row.get('name', 'Unnamed Landmark')
        description = row.get('description', 'No description available')
        landmark_type = row.get('type', 'Unknown type')
        
        # Create HTML content
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 300px;">
            <h3 style="color: #2c3e50; margin-bottom: 10px;">{name}</h3>
            <p style="color: #7f8c8d; font-style: italic; margin-bottom: 8px;">{landmark_type}</p>
            <p style="color: #34495e; margin-bottom: 10px;">{description}</p>
        """
        
        # Add additional properties
        for key, value in row.items():
            if key not in ['name', 'description', 'type', 'geometry'] and pd.notna(value):
                html_content += f"<p style='margin: 2px 0;'><strong>{key}:</strong> {value}</p>"
        
        html_content += "</div>"
        return html_content
    
    def create_charts(self, gdf: gpd.GeoDataFrame, chart_types: List[str] = ["bar", "pie"]) -> List[str]:
        """
        Create various data visualization charts
        
        Args:
            gdf: GeoDataFrame with spatial data
            chart_types: List of chart types to create
            
        Returns:
            List of paths to created chart files
        """
        try:
            chart_paths = []
            
            for chart_type in chart_types:
                if chart_type == "bar":
                    path = self._create_bar_chart(gdf)
                    chart_paths.append(path)
                elif chart_type == "pie":
                    path = self._create_pie_chart(gdf)
                    chart_paths.append(path)
                elif chart_type == "scatter":
                    path = self._create_scatter_plot(gdf)
                    chart_paths.append(path)
                elif chart_type == "histogram":
                    path = self._create_histogram(gdf)
                    chart_paths.append(path)
                elif chart_type == "heatmap":
                    path = self._create_heatmap(gdf)
                    chart_paths.append(path)
            
            return chart_paths
            
        except Exception as e:
            raise Exception(f"Chart creation failed: {str(e)}")
    
    def _create_bar_chart(self, gdf: gpd.GeoDataFrame) -> str:
        """Create bar chart for landmark types"""
        try:
            # Count landmark types
            if 'type' in gdf.columns:
                type_counts = gdf['type'].value_counts()
            else:
                type_counts = pd.Series({'Unknown': len(gdf)})
            
            # Create bar chart
            plt.figure(figsize=(12, 8))
            bars = plt.bar(range(len(type_counts)), type_counts.values, 
                          color=plt.cm.Set3(np.linspace(0, 1, len(type_counts))))
            
            plt.title('Distribution of Italian Landmarks by Type', fontsize=16, fontweight='bold')
            plt.xlabel('Landmark Type', fontsize=12)
            plt.ylabel('Number of Landmarks', fontsize=12)
            plt.xticks(range(len(type_counts)), type_counts.index, rotation=45, ha='right')
            
            # Add value labels on bars
            for i, bar in enumerate(bars):
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{int(height)}', ha='center', va='bottom')
            
            plt.tight_layout()
            
            # Save chart
            chart_path = os.path.join(self.output_dir, "landmark_types_bar_chart.png")
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            raise Exception(f"Bar chart creation failed: {str(e)}")
    
    def _create_pie_chart(self, gdf: gpd.GeoDataFrame) -> str:
        """Create pie chart for landmark types"""
        try:
            # Count landmark types
            if 'type' in gdf.columns:
                type_counts = gdf['type'].value_counts()
            else:
                type_counts = pd.Series({'Unknown': len(gdf)})
            
            # Create pie chart
            plt.figure(figsize=(10, 8))
            colors = plt.cm.Set3(np.linspace(0, 1, len(type_counts)))
            wedges, texts, autotexts = plt.pie(type_counts.values, labels=type_counts.index, 
                                             autopct='%1.1f%%', colors=colors, startangle=90)
            
            plt.title('Distribution of Italian Landmarks by Type', fontsize=16, fontweight='bold')
            
            # Customize text
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            plt.axis('equal')
            plt.tight_layout()
            
            # Save chart
            chart_path = os.path.join(self.output_dir, "landmark_types_pie_chart.png")
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            raise Exception(f"Pie chart creation failed: {str(e)}")
    
    def _create_scatter_plot(self, gdf: gpd.GeoDataFrame) -> str:
        """Create scatter plot for landmark locations"""
        try:
            # Extract coordinates
            lats = [row.geometry.centroid.y for _, row in gdf.iterrows()]
            lons = [row.geometry.centroid.x for _, row in gdf.iterrows()]
            
            # Create scatter plot
            plt.figure(figsize=(12, 8))
            scatter = plt.scatter(lons, lats, c=range(len(lats)), cmap='viridis', 
                                s=100, alpha=0.7, edgecolors='black')
            
            plt.title('Geographic Distribution of Italian Landmarks', fontsize=16, fontweight='bold')
            plt.xlabel('Longitude', fontsize=12)
            plt.ylabel('Latitude', fontsize=12)
            plt.colorbar(scatter, label='Landmark Index')
            
            # Add grid
            plt.grid(True, alpha=0.3)
            
            # Set aspect ratio
            plt.axis('equal')
            plt.tight_layout()
            
            # Save chart
            chart_path = os.path.join(self.output_dir, "landmark_locations_scatter.png")
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            raise Exception(f"Scatter plot creation failed: {str(e)}")
    
    def _create_histogram(self, gdf: gpd.GeoDataFrame) -> str:
        """Create histogram for landmark areas"""
        try:
            # Calculate areas
            areas = [row.geometry.area for _, row in gdf.iterrows()]
            
            # Create histogram
            plt.figure(figsize=(12, 8))
            plt.hist(areas, bins=10, color='skyblue', alpha=0.7, edgecolor='black')
            
            plt.title('Distribution of Landmark Areas', fontsize=16, fontweight='bold')
            plt.xlabel('Area (square degrees)', fontsize=12)
            plt.ylabel('Frequency', fontsize=12)
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Save chart
            chart_path = os.path.join(self.output_dir, "landmark_areas_histogram.png")
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            raise Exception(f"Histogram creation failed: {str(e)}")
    
    def _create_heatmap(self, gdf: gpd.GeoDataFrame) -> str:
        """Create heatmap for landmark density"""
        try:
            # Create grid for heatmap
            lats = [row.geometry.centroid.y for _, row in gdf.iterrows()]
            lons = [row.geometry.centroid.x for _, row in gdf.iterrows()]
            
            # Create 2D histogram
            plt.figure(figsize=(12, 8))
            plt.hist2d(lons, lats, bins=20, cmap='YlOrRd')
            
            plt.title('Landmark Density Heatmap', fontsize=16, fontweight='bold')
            plt.xlabel('Longitude', fontsize=12)
            plt.ylabel('Latitude', fontsize=12)
            plt.colorbar(label='Density')
            
            plt.tight_layout()
            
            # Save chart
            chart_path = os.path.join(self.output_dir, "landmark_density_heatmap.png")
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            raise Exception(f"Heatmap creation failed: {str(e)}")
    
    def create_interactive_dashboard(self, gdf: gpd.GeoDataFrame) -> str:
        """
        Create interactive Plotly dashboard
        
        Args:
            gdf: GeoDataFrame with spatial data
            
        Returns:
            Path to the dashboard HTML file
        """
        try:
            # Create subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Landmark Types', 'Geographic Distribution', 
                               'Area Distribution', 'Density Heatmap'),
                specs=[[{"type": "bar"}, {"type": "scatter"}],
                       [{"type": "histogram"}, {"type": "scatter"}]]
            )
            
            # 1. Bar chart for landmark types
            if 'type' in gdf.columns:
                type_counts = gdf['type'].value_counts()
                fig.add_trace(
                    go.Bar(x=type_counts.index, y=type_counts.values, name="Landmark Types"),
                    row=1, col=1
                )
            
            # 2. Scatter plot for geographic distribution
            lats = [row.geometry.centroid.y for _, row in gdf.iterrows()]
            lons = [row.geometry.centroid.x for _, row in gdf.iterrows()]
            names = [row.get('name', f'Landmark {i}') for i, (_, row) in enumerate(gdf.iterrows())]
            
            fig.add_trace(
                go.Scatter(x=lons, y=lats, mode='markers', name='Landmarks',
                          text=names, hovertemplate='<b>%{text}</b><br>Lat: %{y}<br>Lon: %{x}'),
                row=1, col=2
            )
            
            # 3. Histogram for areas
            areas = [row.geometry.area for _, row in gdf.iterrows()]
            fig.add_trace(
                go.Histogram(x=areas, name="Area Distribution"),
                row=2, col=1
            )
            
            # 4. Density heatmap
            fig.add_trace(
                go.Histogram2d(x=lons, y=lats, name="Density"),
                row=2, col=2
            )
            
            # Update layout
            fig.update_layout(
                title_text="Italy Geospatial Explorer Dashboard",
                showlegend=True,
                height=800
            )
            
            # Save dashboard
            dashboard_path = os.path.join(self.output_dir, "italy_dashboard.html")
            fig.write_html(dashboard_path)
            
            return dashboard_path
            
        except Exception as e:
            raise Exception(f"Interactive dashboard creation failed: {str(e)}")
    
    def create_3d_visualization(self, gdf: gpd.GeoDataFrame) -> str:
        """
        Create 3D visualization of landmarks
        
        Args:
            gdf: GeoDataFrame with spatial data
            
        Returns:
            Path to the 3D visualization HTML file
        """
        try:
            # Extract coordinates and properties
            lats = [row.geometry.centroid.y for _, row in gdf.iterrows()]
            lons = [row.geometry.centroid.x for _, row in gdf.iterrows()]
            names = [row.get('name', f'Landmark {i}') for i, (_, row) in enumerate(gdf.iterrows())]
            types = [row.get('type', 'Unknown') for _, row in gdf.iterrows()]
            areas = [row.geometry.area for _, row in gdf.iterrows()]
            
            # Create 3D scatter plot
            fig = go.Figure(data=[go.Scatter3d(
                x=lons,
                y=lats,
                z=areas,
                mode='markers',
                marker=dict(
                    size=8,
                    color=areas,
                    colorscale='Viridis',
                    opacity=0.8
                ),
                text=names,
                hovertemplate='<b>%{text}</b><br>Lat: %{y}<br>Lon: %{x}<br>Area: %{z}'
            )])
            
            # Update layout
            fig.update_layout(
                title='3D Visualization of Italian Landmarks',
                scene=dict(
                    xaxis_title='Longitude',
                    yaxis_title='Latitude',
                    zaxis_title='Area'
                ),
                width=800,
                height=600
            )
            
            # Save 3D visualization
            viz_path = os.path.join(self.output_dir, "italy_3d_visualization.html")
            fig.write_html(viz_path)
            
            return viz_path
            
        except Exception as e:
            raise Exception(f"3D visualization creation failed: {str(e)}")
    
    def export_visualization_report(self, gdf: gpd.GeoDataFrame) -> str:
        """
        Create comprehensive visualization report
        
        Args:
            gdf: GeoDataFrame with spatial data
            
        Returns:
            Path to the report HTML file
        """
        try:
            # Create report HTML
            report_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Italy Geospatial Explorer - Visualization Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; }}
                    .section {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; }}
                    .chart {{ text-align: center; margin: 20px 0; }}
                    .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                    .stat-box {{ background-color: #ecf0f1; padding: 15px; text-align: center; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🏛️ Italy Geospatial Explorer</h1>
                    <h2>Visualization Report</h2>
                    <p>Generated on {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div class="section">
                    <h3>📊 Dataset Statistics</h3>
                    <div class="stats">
                        <div class="stat-box">
                            <h4>{len(gdf)}</h4>
                            <p>Total Landmarks</p>
                        </div>
                        <div class="stat-box">
                            <h4>{len(gdf.geometry.geom_type.unique())}</h4>
                            <p>Geometry Types</p>
                        </div>
                        <div class="stat-box">
                            <h4>{gdf.geometry.bounds[0]:.2f}</h4>
                            <p>Min Longitude</p>
                        </div>
                        <div class="stat-box">
                            <h4>{gdf.geometry.bounds[1]:.2f}</h4>
                            <p>Min Latitude</p>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h3>🗺️ Interactive Map</h3>
                    <p>Explore the interactive map to see landmark locations and details.</p>
                </div>
                
                <div class="section">
                    <h3>📈 Data Visualizations</h3>
                    <p>Various charts and graphs showing landmark distributions and patterns.</p>
                </div>
                
                <div class="section">
                    <h3>🔍 Analysis Results</h3>
                    <p>Detailed analysis of spatial patterns, clustering, and accessibility.</p>
                </div>
            </body>
            </html>
            """
            
            # Save report
            report_path = os.path.join(self.output_dir, "visualization_report.html")
            with open(report_path, 'w') as f:
                f.write(report_html)
            
            return report_path
            
        except Exception as e:
            raise Exception(f"Visualization report creation failed: {str(e)}")

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
    
    # Initialize visualizer
    visualizer = AdvancedVisualizer()
    
    # Convert to GeoDataFrame
    gdf = gpd.GeoDataFrame.from_features(sample_data['features'])
    
    # Test interactive map creation
    print("🗺️ Testing interactive map creation...")
    map_path = visualizer.create_interactive_map(gdf, style="default")
    print(f"✅ Interactive map saved to: {map_path}")
    
    # Test chart creation
    print("📊 Testing chart creation...")
    chart_paths = visualizer.create_charts(gdf, ["bar", "pie", "scatter"])
    print(f"✅ Created {len(chart_paths)} charts")
    
    # Test dashboard creation
    print("📈 Testing dashboard creation...")
    dashboard_path = visualizer.create_interactive_dashboard(gdf)
    print(f"✅ Dashboard saved to: {dashboard_path}")
    
    print("🎉 Visualization tests completed successfully!")
