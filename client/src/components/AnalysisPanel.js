import React, { useState } from 'react';
import { Card, Button, Form, Row, Col, Alert, ListGroup } from 'react-bootstrap';
import { toast } from 'react-toastify';
import { useGeospatial } from '../context/GeospatialContext';

const AnalysisPanel = () => {
  const { 
    analysisResults, 
    loading, 
    fetchNearestNeighbors,
    fetchDataByRadius,
    mapCenter 
  } = useGeospatial();
  
  const [analysisType, setAnalysisType] = useState('nearest');
  const [radius, setRadius] = useState(1000);
  const [limit, setLimit] = useState(10);
  const [lat, setLat] = useState(mapCenter[0].toString());
  const [lng, setLng] = useState(mapCenter[1].toString());

  const handleNearestNeighbors = async () => {
    try {
      await fetchNearestNeighbors(parseFloat(lat), parseFloat(lng), limit);
      toast.success('Nearest neighbors analysis completed');
    } catch (error) {
      toast.error('Analysis failed');
    }
  };

  const handleRadiusAnalysis = async () => {
    try {
      await fetchDataByRadius(parseFloat(lat), parseFloat(lng), radius);
      toast.success('Radius analysis completed');
    } catch (error) {
      toast.error('Analysis failed');
    }
  };

  const handleUseCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLat(position.coords.latitude.toString());
          setLng(position.coords.longitude.toString());
          toast.success('Current location set');
        },
        (error) => {
          toast.error('Failed to get current location');
        }
      );
    } else {
      toast.error('Geolocation not supported');
    }
  };

  return (
    <div>
      <Card className="mb-3">
        <Card.Header>
          <h6 className="mb-0">
            <i className="fas fa-chart-line me-2"></i>
            Spatial Analysis
          </h6>
        </Card.Header>
        <Card.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Analysis Type</Form.Label>
              <Form.Select 
                value={analysisType} 
                onChange={(e) => setAnalysisType(e.target.value)}
              >
                <option value="nearest">Nearest Neighbors</option>
                <option value="radius">Radius Analysis</option>
              </Form.Select>
            </Form.Group>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Latitude</Form.Label>
                  <Form.Control
                    type="number"
                    step="any"
                    value={lat}
                    onChange={(e) => setLat(e.target.value)}
                    placeholder="40.7128"
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Longitude</Form.Label>
                  <Form.Control
                    type="number"
                    step="any"
                    value={lng}
                    onChange={(e) => setLng(e.target.value)}
                    placeholder="-74.0060"
                  />
                </Form.Group>
              </Col>
            </Row>

            <Button 
              variant="outline-secondary" 
              size="sm" 
              onClick={handleUseCurrentLocation}
              className="mb-3"
            >
              <i className="fas fa-location-arrow me-2"></i>
              Use Current Location
            </Button>

            {analysisType === 'nearest' && (
              <Form.Group className="mb-3">
                <Form.Label>Number of Results</Form.Label>
                <Form.Control
                  type="number"
                  min="1"
                  max="100"
                  value={limit}
                  onChange={(e) => setLimit(parseInt(e.target.value))}
                />
              </Form.Group>
            )}

            {analysisType === 'radius' && (
              <Form.Group className="mb-3">
                <Form.Label>Radius (meters)</Form.Label>
                <Form.Control
                  type="number"
                  min="1"
                  value={radius}
                  onChange={(e) => setRadius(parseInt(e.target.value))}
                />
              </Form.Group>
            )}

            <div className="d-grid">
              <Button 
                variant="primary" 
                onClick={analysisType === 'nearest' ? handleNearestNeighbors : handleRadiusAnalysis}
                disabled={loading}
                className="btn-geospatial"
              >
                {loading ? (
                  <>
                    <i className="fas fa-spinner fa-spin me-2"></i>
                    Analyzing...
                  </>
                ) : (
                  <>
                    <i className="fas fa-search me-2"></i>
                    Run Analysis
                  </>
                )}
              </Button>
            </div>
          </Form>
        </Card.Body>
      </Card>

      {analysisResults && (
        <Card>
          <Card.Header>
            <h6 className="mb-0">
              <i className="fas fa-list me-2"></i>
              Analysis Results
            </h6>
          </Card.Header>
          <Card.Body>
            <div className="mb-3">
              <strong>Found {analysisResults.features?.length || 0} features</strong>
            </div>
            
            {analysisResults.features && analysisResults.features.length > 0 && (
              <ListGroup>
                {analysisResults.features.slice(0, 10).map((feature, index) => (
                  <ListGroup.Item key={feature.id || index} className="d-flex justify-content-between align-items-center">
                    <div>
                      <div className="fw-bold">{feature.properties?.name || 'Unnamed Feature'}</div>
                      {feature.properties?.description && (
                        <small className="text-muted">{feature.properties.description}</small>
                      )}
                    </div>
                    {feature.properties?.distance && (
                      <span className="badge bg-primary">
                        {Math.round(feature.properties.distance)}m
                      </span>
                    )}
                  </ListGroup.Item>
                ))}
              </ListGroup>
            )}

            {analysisResults.features && analysisResults.features.length === 0 && (
              <Alert variant="info" className="mb-0">
                No features found in the specified area
              </Alert>
            )}
          </Card.Body>
        </Card>
      )}

      <Card className="mt-3">
        <Card.Header>
          <h6 className="mb-0">
            <i className="fas fa-info-circle me-2"></i>
            Analysis Tools
          </h6>
        </Card.Header>
        <Card.Body>
          <div className="small text-muted">
            <div className="mb-2">
              <strong>Nearest Neighbors:</strong> Find the closest features to a point
            </div>
            <div className="mb-2">
              <strong>Radius Analysis:</strong> Find all features within a specified distance
            </div>
            <div>
              <strong>Distance:</strong> Calculated in meters using spatial geometry
            </div>
          </div>
        </Card.Body>
      </Card>
    </div>
  );
};

export default AnalysisPanel;
