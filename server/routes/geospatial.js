const express = require('express');
const router = express.Router();

// Mock data for demonstration - Italy landmarks
const mockGeospatialData = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      id: 1,
      properties: {
        name: "Colosseum",
        description: "Ancient Roman amphitheater in Rome",
        type: "monument",
        built: "70-80 AD",
        capacity: "50,000 spectators"
      },
      geometry: {
        type: "Point",
        coordinates: [12.4922, 41.8902]
      }
    },
    {
      type: "Feature",
      id: 2,
      properties: {
        name: "Leaning Tower of Pisa",
        description: "Famous bell tower in Pisa",
        type: "monument",
        height: "56.67m",
        tilt: "3.97 degrees"
      },
      geometry: {
        type: "Point",
        coordinates: [10.3966, 43.7230]
      }
    },
    {
      type: "Feature",
      id: 3,
      properties: {
        name: "Venice Grand Canal",
        description: "Main waterway in Venice",
        type: "waterway",
        length: "3.8 km",
        width: "30-70m"
      },
      geometry: {
        type: "LineString",
        coordinates: [
          [12.3267, 45.4408],
          [12.3350, 45.4300],
          [12.3450, 45.4200]
        ]
      }
    },
    {
      type: "Feature",
      id: 4,
      properties: {
        name: "Vatican City",
        description: "Independent city-state within Rome",
        type: "city-state",
        area: "0.17 sq mi",
        population: "825"
      },
      geometry: {
        type: "Polygon",
        coordinates: [[
          [12.4459, 41.9022],
          [12.4580, 41.9022],
          [12.4580, 41.9094],
          [12.4459, 41.9094],
          [12.4459, 41.9022]
        ]]
      }
    },
    {
      type: "Feature",
      id: 5,
      properties: {
        name: "Florence Cathedral",
        description: "Cathedral of Santa Maria del Fiore",
        type: "cathedral",
        height: "114m",
        dome: "Brunelleschi's Dome"
      },
      geometry: {
        type: "Point",
        coordinates: [11.2558, 43.7731]
      }
    },
    {
      type: "Feature",
      id: 6,
      properties: {
        name: "Amalfi Coast",
        description: "Stunning coastline in southern Italy",
        type: "coastline",
        length: "50 km",
        region: "Campania"
      },
      geometry: {
        type: "LineString",
        coordinates: [
          [14.6270, 40.6340],
          [14.7200, 40.6500],
          [14.8000, 40.6800],
          [14.9000, 40.7200]
        ]
      }
    },
    {
      type: "Feature",
      id: 7,
      properties: {
        name: "Lake Como",
        description: "Beautiful lake in northern Italy",
        type: "lake",
        area: "146 sq km",
        depth: "425m"
      },
      geometry: {
        type: "Polygon",
        coordinates: [[
          [9.2000, 46.0000],
          [9.3000, 46.0000],
          [9.3000, 46.1000],
          [9.2000, 46.1000],
          [9.2000, 46.0000]
        ]]
      }
    },
    {
      type: "Feature",
      id: 8,
      properties: {
        name: "Pompeii",
        description: "Ancient Roman city destroyed by Vesuvius",
        type: "archaeological_site",
        destroyed: "79 AD",
        area: "66 hectares"
      },
      geometry: {
        type: "Point",
        coordinates: [14.4848, 40.7489]
      }
    }
  ]
};

// Get all geospatial data
router.get('/data', async (req, res) => {
  try {
    const { limit = 1000 } = req.query;
    const limitedData = {
      ...mockGeospatialData,
      features: mockGeospatialData.features.slice(0, parseInt(limit))
    };
    res.json(limitedData);
  } catch (error) {
    console.error('Error fetching geospatial data:', error);
    res.status(500).json({ error: 'Failed to fetch geospatial data' });
  }
});

// Get data within bounding box
router.get('/data/bbox', async (req, res) => {
  try {
    const { minx, miny, maxx, maxy } = req.query;
    
    if (!minx || !miny || !maxx || !maxy) {
      return res.status(400).json({ error: 'Bounding box parameters required' });
    }
    
    // Simple bounding box filter for demo
    const filteredFeatures = mockGeospatialData.features.filter(feature => {
      if (feature.geometry.type === 'Point') {
        const [lng, lat] = feature.geometry.coordinates;
        return lng >= parseFloat(minx) && lng <= parseFloat(maxx) && 
               lat >= parseFloat(miny) && lat <= parseFloat(maxy);
      }
      return true; // For polygons and lines, include all for demo
    });
    
    res.json({
      type: "FeatureCollection",
      features: filteredFeatures
    });
  } catch (error) {
    console.error('Error fetching bbox data:', error);
    res.status(500).json({ error: 'Failed to fetch bbox data' });
  }
});

// Get data within radius
router.get('/data/radius', async (req, res) => {
  try {
    const { lat, lng, radius } = req.query;
    
    if (!lat || !lng || !radius) {
      return res.status(400).json({ error: 'Latitude, longitude, and radius required' });
    }
    
    // Simple distance calculation for demo
    const filteredFeatures = mockGeospatialData.features.filter(feature => {
      if (feature.geometry.type === 'Point') {
        const [lng2, lat2] = feature.geometry.coordinates;
        const distance = Math.sqrt(
          Math.pow(lng2 - parseFloat(lng), 2) + Math.pow(lat2 - parseFloat(lat), 2)
        ) * 111000; // Rough conversion to meters
        return distance <= parseFloat(radius);
      }
      return true; // For polygons and lines, include all for demo
    });
    
    res.json({
      type: "FeatureCollection",
      features: filteredFeatures
    });
  } catch (error) {
    console.error('Error fetching radius data:', error);
    res.status(500).json({ error: 'Failed to fetch radius data' });
  }
});

// Add new geospatial data
router.post('/data', async (req, res) => {
  try {
    const { name, description, geometry, properties } = req.body;
    
    if (!geometry) {
      return res.status(400).json({ error: 'Geometry is required' });
    }
    
    const newFeature = {
      type: "Feature",
      id: mockGeospatialData.features.length + 1,
      properties: {
        name: name || 'Unnamed Feature',
        description: description || '',
        ...properties
      },
      geometry
    };
    
    mockGeospatialData.features.push(newFeature);
    
    res.json({
      id: newFeature.id,
      created_at: new Date().toISOString(),
      message: 'Geospatial data added successfully'
    });
  } catch (error) {
    console.error('Error adding geospatial data:', error);
    res.status(500).json({ error: 'Failed to add geospatial data' });
  }
});

// Update geospatial data
router.put('/data/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const { name, description, geometry, properties } = req.body;
    
    const featureIndex = mockGeospatialData.features.findIndex(f => f.id == id);
    
    if (featureIndex === -1) {
      return res.status(404).json({ error: 'Geospatial data not found' });
    }
    
    const feature = mockGeospatialData.features[featureIndex];
    
    if (name) feature.properties.name = name;
    if (description) feature.properties.description = description;
    if (geometry) feature.geometry = geometry;
    if (properties) feature.properties = { ...feature.properties, ...properties };
    
    res.json({
      id: feature.id,
      updated_at: new Date().toISOString(),
      message: 'Geospatial data updated successfully'
    });
  } catch (error) {
    console.error('Error updating geospatial data:', error);
    res.status(500).json({ error: 'Failed to update geospatial data' });
  }
});

// Delete geospatial data
router.delete('/data/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    const featureIndex = mockGeospatialData.features.findIndex(f => f.id == id);
    
    if (featureIndex === -1) {
      return res.status(404).json({ error: 'Geospatial data not found' });
    }
    
    mockGeospatialData.features.splice(featureIndex, 1);
    
    res.json({ message: 'Geospatial data deleted successfully' });
  } catch (error) {
    console.error('Error deleting geospatial data:', error);
    res.status(500).json({ error: 'Failed to delete geospatial data' });
  }
});

module.exports = router;