-- Create database and enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Create geospatial_data table
CREATE TABLE IF NOT EXISTS geospatial_data (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    geometry GEOMETRY,
    properties JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create spatial index
CREATE INDEX IF NOT EXISTS idx_geospatial_data_geometry 
ON geospatial_data USING GIST (geometry);

-- Create properties index
CREATE INDEX IF NOT EXISTS idx_geospatial_data_properties 
ON geospatial_data USING GIN (properties);

-- Create sample data
INSERT INTO geospatial_data (name, description, geometry, properties) VALUES
('Central Park', 'Famous park in Manhattan', 
 ST_GeomFromText('POLYGON((-73.9730 40.7648, -73.9580 40.7648, -73.9580 40.7829, -73.9730 40.7829, -73.9730 40.7648))', 4326),
 '{"type": "park", "area": "843 acres", "established": "1857"}'),

('Times Square', 'Famous intersection in Manhattan',
 ST_GeomFromText('POINT(-73.9857 40.7580)', 4326),
 '{"type": "landmark", "visitors": "50 million annually"}'),

('Brooklyn Bridge', 'Historic suspension bridge',
 ST_GeomFromText('LINESTRING(-73.9969 40.7061, -73.9974 40.7032)', 4326),
 '{"type": "bridge", "length": "1595 feet", "opened": "1883"}'),

('Manhattan Island', 'Main island of New York City',
 ST_GeomFromText('POLYGON((-74.0479 40.6795, -73.9067 40.6795, -73.9067 40.8822, -74.0479 40.8822, -74.0479 40.6795))', 4326),
 '{"type": "island", "area": "22.82 sq mi", "population": "1.6 million"}');

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_geospatial_data_updated_at 
    BEFORE UPDATE ON geospatial_data 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
