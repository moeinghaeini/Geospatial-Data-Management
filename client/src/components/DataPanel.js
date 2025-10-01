import React, { useState } from 'react';
import { Card, Button, Form, Alert, Modal } from 'react-bootstrap';
import { toast } from 'react-toastify';
import { useGeospatial } from '../context/GeospatialContext';

const DataPanel = () => {
  const { 
    mapData, 
    selectedFeature, 
    loading, 
    fetchMapData, 
    addGeospatialData, 
    updateGeospatialData, 
    deleteGeospatialData 
  } = useGeospatial();
  
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    properties: {}
  });

  const handleAddData = async () => {
    try {
      // For demo purposes, create a simple point
      const geometry = {
        type: "Point",
        coordinates: [-74.0060, 40.7128] // NYC coordinates
      };
      
      await addGeospatialData({
        ...formData,
        geometry,
        properties: JSON.parse(formData.properties || '{}')
      });
      
      setShowAddModal(false);
      setFormData({ name: '', description: '', properties: {} });
      toast.success('Data added successfully!');
    } catch (error) {
      toast.error('Failed to add data');
    }
  };

  const handleEditData = async () => {
    try {
      await updateGeospatialData(selectedFeature.id, {
        ...formData,
        properties: JSON.parse(formData.properties || '{}')
      });
      
      setShowEditModal(false);
      toast.success('Data updated successfully!');
    } catch (error) {
      toast.error('Failed to update data');
    }
  };

  const handleDeleteData = async () => {
    if (window.confirm('Are you sure you want to delete this feature?')) {
      try {
        await deleteGeospatialData(selectedFeature.id);
        toast.success('Data deleted successfully!');
      } catch (error) {
        toast.error('Failed to delete data');
      }
    }
  };

  const handleRefresh = () => {
    fetchMapData();
    toast.info('Data refreshed');
  };

  const openEditModal = () => {
    if (selectedFeature) {
      setFormData({
        name: selectedFeature.properties?.name || '',
        description: selectedFeature.properties?.description || '',
        properties: JSON.stringify(selectedFeature.properties || {}, null, 2)
      });
      setShowEditModal(true);
    }
  };

  return (
    <div>
      <Card className="mb-3">
        <Card.Header>
          <h6 className="mb-0">
            <i className="fas fa-database me-2"></i>
            Data Management
          </h6>
        </Card.Header>
        <Card.Body>
          <div className="d-grid gap-2">
            <Button 
              variant="primary" 
              onClick={() => setShowAddModal(true)}
              className="btn-geospatial"
            >
              <i className="fas fa-plus me-2"></i>
              Add New Feature
            </Button>
            
            <Button 
              variant="outline-secondary" 
              onClick={handleRefresh}
              disabled={loading}
            >
              <i className="fas fa-sync-alt me-2"></i>
              Refresh Data
            </Button>
          </div>
        </Card.Body>
      </Card>

      {selectedFeature && (
        <Card className="mb-3">
          <Card.Header>
            <h6 className="mb-0">
              <i className="fas fa-map-marker-alt me-2"></i>
              Selected Feature
            </h6>
          </Card.Header>
          <Card.Body>
            <div className="mb-2">
              <strong>Name:</strong> {selectedFeature.properties?.name || 'Unnamed'}
            </div>
            {selectedFeature.properties?.description && (
              <div className="mb-2">
                <strong>Description:</strong> {selectedFeature.properties.description}
              </div>
            )}
            <div className="d-grid gap-2">
              <Button 
                variant="outline-primary" 
                size="sm" 
                onClick={openEditModal}
              >
                <i className="fas fa-edit me-2"></i>
                Edit
              </Button>
              <Button 
                variant="outline-danger" 
                size="sm" 
                onClick={handleDeleteData}
              >
                <i className="fas fa-trash me-2"></i>
                Delete
              </Button>
            </div>
          </Card.Body>
        </Card>
      )}

      <Card>
        <Card.Header>
          <h6 className="mb-0">
            <i className="fas fa-info-circle me-2"></i>
            Data Info
          </h6>
        </Card.Header>
        <Card.Body>
          {mapData ? (
            <div>
              <div className="mb-2">
                <strong>Total Features:</strong> {mapData.features?.length || 0}
              </div>
              <div className="mb-2">
                <strong>Type:</strong> {mapData.type}
              </div>
              {loading && (
                <Alert variant="info" className="mb-0">
                  <i className="fas fa-spinner fa-spin me-2"></i>
                  Loading data...
                </Alert>
              )}
            </div>
          ) : (
            <Alert variant="warning" className="mb-0">
              No data available
            </Alert>
          )}
        </Card.Body>
      </Card>

      {/* Add Data Modal */}
      <Modal show={showAddModal} onHide={() => setShowAddModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Add New Feature</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Name</Form.Label>
              <Form.Control
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                placeholder="Enter feature name"
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                placeholder="Enter feature description"
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Properties (JSON)</Form.Label>
              <Form.Control
                as="textarea"
                rows={4}
                value={formData.properties}
                onChange={(e) => setFormData({...formData, properties: e.target.value})}
                placeholder='{"type": "landmark", "category": "tourism"}'
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowAddModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleAddData}>
            Add Feature
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Edit Data Modal */}
      <Modal show={showEditModal} onHide={() => setShowEditModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Edit Feature</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Name</Form.Label>
              <Form.Control
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                placeholder="Enter feature name"
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                placeholder="Enter feature description"
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Properties (JSON)</Form.Label>
              <Form.Control
                as="textarea"
                rows={4}
                value={formData.properties}
                onChange={(e) => setFormData({...formData, properties: e.target.value})}
                placeholder='{"type": "landmark", "category": "tourism"}'
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowEditModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleEditData}>
            Update Feature
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default DataPanel;
