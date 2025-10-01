import React, { createContext, useContext, useReducer, useEffect } from 'react';
import axios from 'axios';

const GeospatialContext = createContext();

const initialState = {
  mapData: null,
  selectedFeature: null,
  loading: false,
  error: null,
  stats: null,
  analysisResults: null,
  mapCenter: [41.9028, 12.4964], // Rome, Italy
  mapZoom: 6
};

const geospatialReducer = (state, action) => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    
    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false };
    
    case 'SET_MAP_DATA':
      return { ...state, mapData: action.payload, loading: false, error: null };
    
    case 'SET_SELECTED_FEATURE':
      return { ...state, selectedFeature: action.payload };
    
    case 'SET_STATS':
      return { ...state, stats: action.payload };
    
    case 'SET_ANALYSIS_RESULTS':
      return { ...state, analysisResults: action.payload };
    
    case 'SET_MAP_CENTER':
      return { ...state, mapCenter: action.payload };
    
    case 'SET_MAP_ZOOM':
      return { ...state, mapZoom: action.payload };
    
    default:
      return state;
  }
};

export const GeospatialProvider = ({ children }) => {
  const [state, dispatch] = useReducer(geospatialReducer, initialState);

  // API functions
  const fetchMapData = async (params = {}) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const response = await axios.get('/api/geospatial/data', { params });
      dispatch({ type: 'SET_MAP_DATA', payload: response.data });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
    }
  };

  const fetchDataByBbox = async (bbox) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const response = await axios.get('/api/geospatial/data/bbox', {
        params: {
          minx: bbox[0],
          miny: bbox[1],
          maxx: bbox[2],
          maxy: bbox[3]
        }
      });
      dispatch({ type: 'SET_MAP_DATA', payload: response.data });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
    }
  };

  const fetchDataByRadius = async (lat, lng, radius) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const response = await axios.get('/api/geospatial/data/radius', {
        params: { lat, lng, radius }
      });
      dispatch({ type: 'SET_MAP_DATA', payload: response.data });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get('/api/data/stats');
      dispatch({ type: 'SET_STATS', payload: response.data });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
    }
  };

  const fetchNearestNeighbors = async (lat, lng, limit = 10) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const response = await axios.get('/api/data/analysis/nearest', {
        params: { lat, lng, limit }
      });
      dispatch({ type: 'SET_ANALYSIS_RESULTS', payload: response.data });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
    }
  };

  const addGeospatialData = async (data) => {
    try {
      const response = await axios.post('/api/geospatial/data', data);
      await fetchMapData(); // Refresh data
      return response.data;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const updateGeospatialData = async (id, data) => {
    try {
      const response = await axios.put(`/api/geospatial/data/${id}`, data);
      await fetchMapData(); // Refresh data
      return response.data;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const deleteGeospatialData = async (id) => {
    try {
      const response = await axios.delete(`/api/geospatial/data/${id}`);
      await fetchMapData(); // Refresh data
      return response.data;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  // Load initial data
  useEffect(() => {
    fetchMapData();
    fetchStats();
  }, []);

  const value = {
    ...state,
    fetchMapData,
    fetchDataByBbox,
    fetchDataByRadius,
    fetchStats,
    fetchNearestNeighbors,
    addGeospatialData,
    updateGeospatialData,
    deleteGeospatialData,
    setSelectedFeature: (feature) => dispatch({ type: 'SET_SELECTED_FEATURE', payload: feature }),
    setMapCenter: (center) => dispatch({ type: 'SET_MAP_CENTER', payload: center }),
    setMapZoom: (zoom) => dispatch({ type: 'SET_MAP_ZOOM', payload: zoom })
  };

  return (
    <GeospatialContext.Provider value={value}>
      {children}
    </GeospatialContext.Provider>
  );
};

export const useGeospatial = () => {
  const context = useContext(GeospatialContext);
  if (!context) {
    throw new Error('useGeospatial must be used within a GeospatialProvider');
  }
  return context;
};
