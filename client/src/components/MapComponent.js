import React, { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, GeoJSON, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { useGeospatial } from '../context/GeospatialContext';

// Fix for default markers in react-leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom component to handle map events
const MapEventHandler = ({ onMapReady }) => {
  const map = useMap();
  
  useEffect(() => {
    if (onMapReady) {
      onMapReady(map);
    }
  }, [map, onMapReady]);

  return null;
};

const MapComponent = () => {
  const { 
    mapData, 
    selectedFeature, 
    mapCenter, 
    mapZoom, 
    setSelectedFeature,
    loading,
    error 
  } = useGeospatial();
  
  const mapRef = useRef(null);

  const handleMapReady = (map) => {
    mapRef.current = map;
    
    // Add click handler to clear selection
    map.on('click', () => {
      setSelectedFeature(null);
    });
  };

  const onEachFeature = (feature, layer) => {
    // Add click handler to each feature
    layer.on('click', (e) => {
      e.originalEvent.stopPropagation();
      setSelectedFeature(feature);
    });

    // Add hover effects
    layer.on('mouseover', (e) => {
      layer.setStyle({
        weight: 3,
        opacity: 0.8,
        color: '#ff6b6b'
      });
    });

    layer.on('mouseout', (e) => {
      layer.setStyle({
        weight: 2,
        opacity: 0.6,
        color: '#3388ff'
      });
    });
  };

  const getFeatureStyle = (feature) => {
    const isSelected = selectedFeature && selectedFeature.id === feature.id;
    
    return {
      weight: isSelected ? 4 : 2,
      opacity: isSelected ? 1 : 0.6,
      color: isSelected ? '#ff6b6b' : '#3388ff',
      fillOpacity: isSelected ? 0.8 : 0.3,
      fillColor: isSelected ? '#ff6b6b' : '#3388ff'
    };
  };

  const renderPopup = (feature) => {
    const properties = feature.properties || {};
    
    return (
      <Popup>
        <div className="feature-popup">
          <h6>{properties.name || 'Unnamed Feature'}</h6>
          {properties.description && (
            <p className="mb-2">{properties.description}</p>
          )}
          {Object.entries(properties).map(([key, value]) => {
            if (key === 'name' || key === 'description') return null;
            return (
              <div key={key} className="mb-1">
                <strong>{key}:</strong> {String(value)}
              </div>
            );
          })}
        </div>
      </Popup>
    );
  };

  if (loading) {
    return (
      <div className="map-container d-flex justify-content-center align-items-center">
        <div className="text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="mt-2">Loading map data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="map-container d-flex justify-content-center align-items-center">
        <div className="text-center text-danger">
          <i className="fas fa-exclamation-triangle fa-3x mb-3"></i>
          <h5>Error Loading Map</h5>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="map-container">
      <MapContainer
        center={mapCenter}
        zoom={mapZoom}
        style={{ height: '100%', width: '100%' }}
        zoomControl={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        <MapEventHandler onMapReady={handleMapReady} />
        
        {mapData && mapData.features && (
          <GeoJSON
            data={mapData}
            onEachFeature={onEachFeature}
            style={getFeatureStyle}
          >
            {mapData.features.map((feature, index) => (
              <React.Fragment key={feature.id || index}>
                {renderPopup(feature)}
              </React.Fragment>
            ))}
          </GeoJSON>
        )}
      </MapContainer>
    </div>
  );
};

export default MapComponent;
