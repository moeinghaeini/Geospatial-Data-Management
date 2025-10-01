const express = require('express');
const router = express.Router();

// Mock data for demonstration - Italy
const mockStats = {
  total_features: 8,
  bounds: {
    minx: 9.2000,
    miny: 40.6340,
    maxx: 14.9000,
    maxy: 46.1000
  },
  area: 301340, // Italy's area in sq km
  table_name: 'geospatial_data'
};

// Get database statistics
router.get('/stats', async (req, res) => {
  try {
    res.json(mockStats);
  } catch (error) {
    console.error('Error fetching data stats:', error);
    res.status(500).json({ error: 'Failed to fetch data statistics' });
  }
});

// Get data by type
router.get('/by-type', async (req, res) => {
  try {
    const { type } = req.query;
    
    if (!type) {
      return res.status(400).json({ error: 'Type parameter is required' });
    }
    
    // Mock response based on type
    const mockData = {
      type: "FeatureCollection",
      features: [
        {
          type: "Feature",
          id: 1,
          properties: {
            name: `Sample ${type}`,
            description: `A sample ${type} feature`
          },
          geometry: {
            type: type,
            coordinates: type === 'Point' ? [-73.9857, 40.7580] : 
                        type === 'LineString' ? [[-73.9969, 40.7061], [-73.9974, 40.7032]] :
                        [[[-73.9730, 40.7648], [-73.9580, 40.7648], [-73.9580, 40.7829], [-73.9730, 40.7829], [-73.9730, 40.7648]]]
          }
        }
      ]
    };
    
    res.json(mockData);
  } catch (error) {
    console.error('Error fetching data by type:', error);
    res.status(500).json({ error: 'Failed to fetch data by type' });
  }
});

// Get spatial analysis results
router.get('/analysis/intersection', async (req, res) => {
  try {
    const { geom1, geom2 } = req.query;
    
    if (!geom1 || !geom2) {
      return res.status(400).json({ error: 'Both geometry parameters are required' });
    }
    
    // Mock intersection result
    res.json({
      intersection: {
        type: "Polygon",
        coordinates: [[[-73.9730, 40.7648], [-73.9580, 40.7648], [-73.9580, 40.7829], [-73.9730, 40.7829], [-73.9730, 40.7648]]]
      },
      area: 0.1
    });
  } catch (error) {
    console.error('Error calculating intersection:', error);
    res.status(500).json({ error: 'Failed to calculate intersection' });
  }
});

// Get buffer analysis
router.get('/analysis/buffer', async (req, res) => {
  try {
    const { geometry, distance } = req.query;
    
    if (!geometry || !distance) {
      return res.status(400).json({ error: 'Geometry and distance parameters are required' });
    }
    
    // Mock buffer result
    res.json({
      buffer: {
        type: "Polygon",
        coordinates: [[[-73.9730, 40.7648], [-73.9580, 40.7648], [-73.9580, 40.7829], [-73.9730, 40.7829], [-73.9730, 40.7648]]]
      },
      area: 0.2
    });
  } catch (error) {
    console.error('Error calculating buffer:', error);
    res.status(500).json({ error: 'Failed to calculate buffer' });
  }
});

// Get nearest neighbors
router.get('/analysis/nearest', async (req, res) => {
  try {
    const { lat, lng, limit = 10 } = req.query;
    
    if (!lat || !lng) {
      return res.status(400).json({ error: 'Latitude and longitude are required' });
    }
    
    // Mock nearest neighbors result - Italy
    const mockNearest = {
      type: "FeatureCollection",
      features: [
        {
          type: "Feature",
          id: 1,
          properties: {
            name: "Colosseum",
            description: "Ancient Roman amphitheater in Rome",
            distance: 100
          },
          geometry: {
            type: "Point",
            coordinates: [12.4922, 41.8902]
          }
        },
        {
          type: "Feature",
          id: 4,
          properties: {
            name: "Vatican City",
            description: "Independent city-state within Rome",
            distance: 500
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
        }
      ]
    };
    
    res.json(mockNearest);
  } catch (error) {
    console.error('Error finding nearest neighbors:', error);
    res.status(500).json({ error: 'Failed to find nearest neighbors' });
  }
});

module.exports = router;