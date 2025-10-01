import React from 'react';
import { Nav, Tab, Container } from 'react-bootstrap';
import DataPanel from './DataPanel';
import AnalysisPanel from './AnalysisPanel';
import StatsPanel from './StatsPanel';

const Sidebar = ({ activePanel, setActivePanel }) => {
  return (
    <div className="sidebar h-100 p-3">
      <Container fluid>
        <Tab.Container activeKey={activePanel} onSelect={setActivePanel}>
          <Nav variant="pills" className="flex-column mb-3">
            <Nav.Item>
              <Nav.Link eventKey="data" className="d-flex align-items-center">
                <i className="fas fa-database me-2"></i>
                Data Management
              </Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link eventKey="analysis" className="d-flex align-items-center">
                <i className="fas fa-chart-line me-2"></i>
                Spatial Analysis
              </Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link eventKey="stats" className="d-flex align-items-center">
                <i className="fas fa-chart-bar me-2"></i>
                Statistics
              </Nav.Link>
            </Nav.Item>
          </Nav>

          <Tab.Content>
            <Tab.Pane eventKey="data">
              <DataPanel />
            </Tab.Pane>
            <Tab.Pane eventKey="analysis">
              <AnalysisPanel />
            </Tab.Pane>
            <Tab.Pane eventKey="stats">
              <StatsPanel />
            </Tab.Pane>
          </Tab.Content>
        </Tab.Container>
      </Container>
    </div>
  );
};

export default Sidebar;
