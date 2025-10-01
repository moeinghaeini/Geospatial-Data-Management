const express = require('express');
const cors = require('cors');
const path = require('path');
const { PythonIntegration, pythonIntegrationMiddleware, setupPythonRoutes } = require('../integrate_python');

const app = express();
const PORT = process.env.PORT || 5001;

// Middleware
app.use(cors());
app.use(express.json());

// Only serve static files in production
if (process.env.NODE_ENV === 'production') {
  app.use(express.static(path.join(__dirname, '../client/build')));
}

// Import routes
const geospatialRoutes = require('./routes/geospatial');
const dataRoutes = require('./routes/data');

// Routes
app.use('/api/geospatial', geospatialRoutes);
app.use('/api/data', dataRoutes);

// Python integration middleware
app.use(pythonIntegrationMiddleware);

// Setup Python integration routes
setupPythonRoutes(app);

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    message: 'Geospatial Data Management API is running',
    timestamp: new Date().toISOString()
  });
});

// Serve React app for all other routes (only in production)
if (process.env.NODE_ENV === 'production') {
  app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, '../client/build', 'index.html'));
  });
}

app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
  console.log(`📍 Geospatial Data Management API ready`);
});
