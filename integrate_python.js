/**
 * Python Integration for Italy Geospatial Explorer
 * Connects the Node.js application with the Python backend
 */

const axios = require('axios');
const WebSocket = require('ws');

class PythonIntegration {
    constructor() {
        this.pythonApiUrl = process.env.PYTHON_API_URL || 'http://localhost:8000';
        this.pythonWsUrl = process.env.PYTHON_WS_URL || 'ws://localhost:8000/ws';
        this.wsConnection = null;
        this.isConnected = false;
    }

    /**
     * Initialize Python integration
     */
    async initialize() {
        try {
            console.log('🐍 Initializing Python integration...');
            
            // Test Python API connection
            await this.testConnection();
            
            // Connect to WebSocket
            await this.connectWebSocket();
            
            console.log('✅ Python integration initialized successfully');
            return true;
        } catch (error) {
            console.error('❌ Python integration failed:', error.message);
            return false;
        }
    }

    /**
     * Test Python API connection
     */
    async testConnection() {
        try {
            const response = await axios.get(`${this.pythonApiUrl}/api/health`, {
                timeout: 5000
            });
            
            if (response.data.status === 'healthy') {
                console.log('✅ Python API is healthy');
                return true;
            } else {
                throw new Error('Python API is not healthy');
            }
        } catch (error) {
            throw new Error(`Python API connection failed: ${error.message}`);
        }
    }

    /**
     * Connect to Python WebSocket
     */
    async connectWebSocket() {
        return new Promise((resolve, reject) => {
            try {
                this.wsConnection = new WebSocket(this.pythonWsUrl);
                
                this.wsConnection.on('open', () => {
                    console.log('✅ Python WebSocket connected');
                    this.isConnected = true;
                    resolve();
                });
                
                this.wsConnection.on('message', (data) => {
                    try {
                        const message = JSON.parse(data);
                        this.handleWebSocketMessage(message);
                    } catch (error) {
                        console.error('WebSocket message parsing error:', error);
                    }
                });
                
                this.wsConnection.on('close', () => {
                    console.log('⚠️ Python WebSocket disconnected');
                    this.isConnected = false;
                });
                
                this.wsConnection.on('error', (error) => {
                    console.error('❌ Python WebSocket error:', error);
                    reject(error);
                });
                
            } catch (error) {
                reject(error);
            }
        });
    }

    /**
     * Handle WebSocket messages from Python
     */
    handleWebSocketMessage(message) {
        console.log('📨 Received from Python:', message.type);
        
        switch (message.type) {
            case 'analysis_completed':
                this.handleAnalysisCompleted(message.data);
                break;
            case 'model_training_completed':
                this.handleModelTrainingCompleted(message.data);
                break;
            case 'landmark_created':
                this.handleLandmarkCreated(message.data);
                break;
            case 'landmark_updated':
                this.handleLandmarkUpdated(message.data);
                break;
            case 'landmark_deleted':
                this.handleLandmarkDeleted(message.data);
                break;
            case 'realtime_analysis':
                this.handleRealtimeAnalysis(message.data);
                break;
            default:
                console.log('Unknown message type:', message.type);
        }
    }

    /**
     * Perform advanced spatial analysis
     */
    async performSpatialAnalysis(analysisType, parameters = {}) {
        try {
            const response = await axios.post(`${this.pythonApiUrl}/api/analysis/spatial`, {
                analysis_type: analysisType,
                parameters: parameters
            });
            
            return response.data;
        } catch (error) {
            console.error('Spatial analysis failed:', error.message);
            throw error;
        }
    }

    /**
     * Train machine learning model
     */
    async trainMLModel(modelType, trainingData, parameters = {}) {
        try {
            const response = await axios.post(`${this.pythonApiUrl}/api/ml/train`, {
                model_type: modelType,
                training_data: trainingData,
                parameters: parameters
            });
            
            return response.data;
        } catch (error) {
            console.error('ML model training failed:', error.message);
            throw error;
        }
    }

    /**
     * Make ML prediction
     */
    async makePrediction(features, modelType = 'accessibility') {
        try {
            const response = await axios.post(`${this.pythonApiUrl}/api/ml/predict`, {
                features: features,
                model_type: modelType
            });
            
            return response.data;
        } catch (error) {
            console.error('ML prediction failed:', error.message);
            throw error;
        }
    }

    /**
     * Import geospatial data
     */
    async importData(filePath, format = 'geojson') {
        try {
            const response = await axios.post(`${this.pythonApiUrl}/api/data/import`, {
                file_path: filePath,
                format: format
            });
            
            return response.data;
        } catch (error) {
            console.error('Data import failed:', error.message);
            throw error;
        }
    }

    /**
     * Export geospatial data
     */
    async exportData(format = 'geojson') {
        try {
            const response = await axios.get(`${this.pythonApiUrl}/api/data/export`, {
                params: { format: format }
            });
            
            return response.data;
        } catch (error) {
            console.error('Data export failed:', error.message);
            throw error;
        }
    }

    /**
     * Create interactive visualization
     */
    async createVisualization(style = 'default') {
        try {
            const response = await axios.post(`${this.pythonApiUrl}/api/visualize/map`, {
                style: style
            });
            
            return response.data;
        } catch (error) {
            console.error('Visualization creation failed:', error.message);
            throw error;
        }
    }

    /**
     * Get comprehensive statistics
     */
    async getStatistics() {
        try {
            const response = await axios.get(`${this.pythonApiUrl}/api/statistics`);
            return response.data;
        } catch (error) {
            console.error('Statistics retrieval failed:', error.message);
            throw error;
        }
    }

    /**
     * Process real-time data
     */
    async processRealtimeData(geojsonData) {
        try {
            const response = await axios.post(`${this.pythonApiUrl}/api/realtime/process`, {
                type: 'FeatureCollection',
                features: geojsonData
            });
            
            return response.data;
        } catch (error) {
            console.error('Real-time processing failed:', error.message);
            throw error;
        }
    }

    /**
     * Handle analysis completed event
     */
    handleAnalysisCompleted(data) {
        console.log(`📊 Analysis completed: ${data.analysis_type}`);
        // Emit event to frontend or update database
        // This could trigger a frontend update via WebSocket
    }

    /**
     * Handle model training completed event
     */
    handleModelTrainingCompleted(data) {
        console.log(`🤖 Model training completed: ${data.model_type}`);
        // Update model status in database
        // Notify frontend of training completion
    }

    /**
     * Handle landmark created event
     */
    handleLandmarkCreated(data) {
        console.log(`🏛️ Landmark created: ${data.name}`);
        // Update local database
        // Notify frontend of new landmark
    }

    /**
     * Handle landmark updated event
     */
    handleLandmarkUpdated(data) {
        console.log(`🔄 Landmark updated: ${data.name}`);
        // Update local database
        // Notify frontend of landmark update
    }

    /**
     * Handle landmark deleted event
     */
    handleLandmarkDeleted(data) {
        console.log(`🗑️ Landmark deleted: ID ${data.id}`);
        // Update local database
        // Notify frontend of landmark deletion
    }

    /**
     * Handle real-time analysis event
     */
    handleRealtimeAnalysis(data) {
        console.log(`⚡ Real-time analysis: ${data.feature_count} features`);
        // Update frontend with real-time results
        // Could trigger map updates or notifications
    }

    /**
     * Send message to Python WebSocket
     */
    sendMessage(message) {
        if (this.wsConnection && this.isConnected) {
            this.wsConnection.send(JSON.stringify(message));
        } else {
            console.warn('⚠️ WebSocket not connected, cannot send message');
        }
    }

    /**
     * Close Python integration
     */
    close() {
        if (this.wsConnection) {
            this.wsConnection.close();
        }
        console.log('👋 Python integration closed');
    }
}

// Express.js integration middleware
function pythonIntegrationMiddleware(req, res, next) {
    req.pythonIntegration = new PythonIntegration();
    next();
}

// Example Express routes that use Python integration
function setupPythonRoutes(app) {
    // Advanced spatial analysis endpoint
    app.post('/api/advanced/spatial-analysis', async (req, res) => {
        try {
            const { analysisType, parameters } = req.body;
            const result = await req.pythonIntegration.performSpatialAnalysis(analysisType, parameters);
            res.json(result);
        } catch (error) {
            res.status(500).json({ error: 'Advanced spatial analysis failed' });
        }
    });

    // Machine learning prediction endpoint
    app.post('/api/advanced/ml-prediction', async (req, res) => {
        try {
            const { features, modelType } = req.body;
            const result = await req.pythonIntegration.makePrediction(features, modelType);
            res.json(result);
        } catch (error) {
            res.status(500).json({ error: 'ML prediction failed' });
        }
    });

    // Data import endpoint
    app.post('/api/advanced/import-data', async (req, res) => {
        try {
            const { filePath, format } = req.body;
            const result = await req.pythonIntegration.importData(filePath, format);
            res.json(result);
        } catch (error) {
            res.status(500).json({ error: 'Data import failed' });
        }
    });

    // Visualization creation endpoint
    app.post('/api/advanced/create-visualization', async (req, res) => {
        try {
            const { style } = req.body;
            const result = await req.pythonIntegration.createVisualization(style);
            res.json(result);
        } catch (error) {
            res.status(500).json({ error: 'Visualization creation failed' });
        }
    });

    // Statistics endpoint
    app.get('/api/advanced/statistics', async (req, res) => {
        try {
            const result = await req.pythonIntegration.getStatistics();
            res.json(result);
        } catch (error) {
            res.status(500).json({ error: 'Statistics retrieval failed' });
        }
    });
}

module.exports = {
    PythonIntegration,
    pythonIntegrationMiddleware,
    setupPythonRoutes
};
