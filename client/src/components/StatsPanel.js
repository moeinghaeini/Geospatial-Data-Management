import React, { useEffect } from 'react';
import { Card, Row, Col, Alert, Spinner } from 'react-bootstrap';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { useGeospatial } from '../context/GeospatialContext';

const StatsPanel = () => {
  const { stats, mapData, loading, fetchStats } = useGeospatial();

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  // Process data for charts
  const getFeatureTypeStats = () => {
    if (!mapData || !mapData.features) return [];
    
    const typeCount = {};
    mapData.features.forEach(feature => {
      const geometryType = feature.geometry?.type || 'Unknown';
      typeCount[geometryType] = (typeCount[geometryType] || 0) + 1;
    });
    
    return Object.entries(typeCount).map(([type, count]) => ({
      type,
      count,
      percentage: ((count / mapData.features.length) * 100).toFixed(1)
    }));
  };

  const getPropertyStats = () => {
    if (!mapData || !mapData.features) return [];
    
    const propertyCount = {};
    mapData.features.forEach(feature => {
      if (feature.properties) {
        Object.entries(feature.properties).forEach(([key, value]) => {
          if (key !== 'name' && key !== 'description' && typeof value === 'string') {
            const propKey = `${key}: ${value}`;
            propertyCount[propKey] = (propertyCount[propKey] || 0) + 1;
          }
        });
      }
    });
    
    return Object.entries(propertyCount)
      .map(([property, count]) => ({ property, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  const featureTypeData = getFeatureTypeStats();
  const propertyData = getPropertyStats();

  if (loading) {
    return (
      <Card>
        <Card.Body className="text-center">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
          <p className="mt-2">Loading statistics...</p>
        </Card.Body>
      </Card>
    );
  }

  return (
    <div>
      {/* Overview Stats */}
      <Card className="mb-3">
        <Card.Header>
          <h6 className="mb-0">
            <i className="fas fa-chart-bar me-2"></i>
            Overview Statistics
          </h6>
        </Card.Header>
        <Card.Body>
          {stats ? (
            <Row>
              <Col md={6}>
                <div className="stats-card text-center">
                  <h3>{stats.total_features}</h3>
                  <p className="mb-0">Total Features</p>
                </div>
              </Col>
              <Col md={6}>
                <div className="stats-card text-center">
                  <h3>{stats.area ? `${(stats.area / 1000000).toFixed(2)} km²` : 'N/A'}</h3>
                  <p className="mb-0">Coverage Area</p>
                </div>
              </Col>
            </Row>
          ) : (
            <Alert variant="warning" className="mb-0">
              No statistics available
            </Alert>
          )}
        </Card.Body>
      </Card>

      {/* Feature Type Distribution */}
      {featureTypeData.length > 0 && (
        <Card className="mb-3">
          <Card.Header>
            <h6 className="mb-0">
              <i className="fas fa-shapes me-2"></i>
              Feature Types
            </h6>
          </Card.Header>
          <Card.Body>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={featureTypeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="type" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </Card.Body>
        </Card>
      )}

      {/* Property Distribution */}
      {propertyData.length > 0 && (
        <Card className="mb-3">
          <Card.Header>
            <h6 className="mb-0">
              <i className="fas fa-tags me-2"></i>
              Property Distribution
            </h6>
          </Card.Header>
          <Card.Body>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={propertyData} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="property" type="category" width={100} />
                <Tooltip />
                <Bar dataKey="count" fill="#82ca9d" />
              </BarChart>
            </ResponsiveContainer>
          </Card.Body>
        </Card>
      )}

      {/* Feature Type Pie Chart */}
      {featureTypeData.length > 0 && (
        <Card className="mb-3">
          <Card.Header>
            <h6 className="mb-0">
              <i className="fas fa-chart-pie me-2"></i>
              Feature Distribution
            </h6>
          </Card.Header>
          <Card.Body>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={featureTypeData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ type, percentage }) => `${type} (${percentage}%)`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {featureTypeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card.Body>
        </Card>
      )}

      {/* Data Quality Info */}
      <Card>
        <Card.Header>
          <h6 className="mb-0">
            <i className="fas fa-info-circle me-2"></i>
            Data Quality
          </h6>
        </Card.Header>
        <Card.Body>
          <div className="small text-muted">
            <div className="mb-2">
              <strong>Total Features:</strong> {mapData?.features?.length || 0}
            </div>
            <div className="mb-2">
              <strong>Geometry Types:</strong> {featureTypeData.length}
            </div>
            <div className="mb-2">
              <strong>Features with Properties:</strong> {
                mapData?.features?.filter(f => f.properties && Object.keys(f.properties).length > 0).length || 0
              }
            </div>
            <div>
              <strong>Last Updated:</strong> {new Date().toLocaleString()}
            </div>
          </div>
        </Card.Body>
      </Card>
    </div>
  );
};

export default StatsPanel;
