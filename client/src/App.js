import React, { useState } from 'react';
import { Container, Row, Col, Navbar, Nav, Button, Offcanvas } from 'react-bootstrap';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import 'bootstrap/dist/css/bootstrap.min.css';

import MapComponent from './components/MapComponent';
import Sidebar from './components/Sidebar';
import DataPanel from './components/DataPanel';
import AnalysisPanel from './components/AnalysisPanel';
import StatsPanel from './components/StatsPanel';
import { GeospatialProvider } from './context/GeospatialContext';

function App() {
  const [showSidebar, setShowSidebar] = useState(false);
  const [activePanel, setActivePanel] = useState('data');

  const handleShowSidebar = () => setShowSidebar(true);
  const handleCloseSidebar = () => setShowSidebar(false);

  return (
    <GeospatialProvider>
      <div className="App">
        <Navbar bg="dark" variant="dark" expand="lg" className="mb-0">
          <Container fluid>
            <Navbar.Brand href="#">
              <i className="fas fa-map-marked-alt me-2"></i>
              Italy Geospatial Explorer
            </Navbar.Brand>
            <Navbar.Toggle aria-controls="basic-navbar-nav" />
            <Navbar.Collapse id="basic-navbar-nav">
              <Nav className="me-auto">
                <Nav.Link 
                  href="#" 
                  onClick={() => setActivePanel('data')}
                  className={activePanel === 'data' ? 'active' : ''}
                >
                  Data
                </Nav.Link>
                <Nav.Link 
                  href="#" 
                  onClick={() => setActivePanel('analysis')}
                  className={activePanel === 'analysis' ? 'active' : ''}
                >
                  Analysis
                </Nav.Link>
                <Nav.Link 
                  href="#" 
                  onClick={() => setActivePanel('stats')}
                  className={activePanel === 'stats' ? 'active' : ''}
                >
                  Statistics
                </Nav.Link>
              </Nav>
              <Button 
                variant="outline-light" 
                onClick={handleShowSidebar}
                className="d-lg-none"
              >
                <i className="fas fa-bars"></i>
              </Button>
            </Navbar.Collapse>
          </Container>
        </Navbar>

        <Container fluid className="p-0">
          <Row className="g-0">
            {/* Desktop Sidebar */}
            <Col lg={3} className="d-none d-lg-block">
              <Sidebar activePanel={activePanel} setActivePanel={setActivePanel} />
            </Col>

            {/* Main Content */}
            <Col lg={9} className="p-0">
              <div className="position-relative">
                <MapComponent />
                
                {/* Mobile Sidebar Overlay */}
                <Offcanvas 
                  show={showSidebar} 
                  onHide={handleCloseSidebar}
                  placement="start"
                  className="d-lg-none"
                >
                  <Offcanvas.Header closeButton>
                    <Offcanvas.Title>Controls</Offcanvas.Title>
                  </Offcanvas.Header>
                  <Offcanvas.Body>
                    <Sidebar activePanel={activePanel} setActivePanel={setActivePanel} />
                  </Offcanvas.Body>
                </Offcanvas>
              </div>
            </Col>
          </Row>
        </Container>

        <ToastContainer
          position="top-right"
          autoClose={3000}
          hideProgressBar={false}
          newestOnTop={false}
          closeOnClick
          rtl={false}
          pauseOnFocusLoss
          draggable
          pauseOnHover
        />
      </div>
    </GeospatialProvider>
  );
}

export default App;
