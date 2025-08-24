-- Database: crime_analytics
CREATE SCHEMA IF NOT EXISTS crime;

CREATE TABLE IF NOT EXISTS crime.dim_location (
    location_id SERIAL PRIMARY KEY,
    district VARCHAR(100),
    ward VARCHAR(100),
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    grid_x INTEGER,
    grid_y INTEGER
);

CREATE TABLE IF NOT EXISTS crime.dim_offense (
    offense_id SERIAL PRIMARY KEY,
    offense_code VARCHAR(20) UNIQUE,
    offense_name VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS crime.dim_calendar (
    date_key DATE PRIMARY KEY,
    year INT,
    month INT,
    day INT,
    dow INT,
    week INT,
    is_weekend BOOLEAN
);

CREATE TABLE IF NOT EXISTS crime.fact_crime (
    crime_id BIGSERIAL PRIMARY KEY,
    occurred_at TIMESTAMP NOT NULL,
    date_key DATE NOT NULL REFERENCES crime.dim_calendar(date_key),
    offense_id INT NOT NULL REFERENCES crime.dim_offense(offense_id),
    location_id INT NOT NULL REFERENCES crime.dim_location(location_id),
    severity INT,
    weapon_used BOOLEAN,
    arrested BOOLEAN
);

CREATE INDEX IF NOT EXISTS idx_fact_crime_date ON crime.fact_crime(date_key);
CREATE INDEX IF NOT EXISTS idx_fact_crime_offense ON crime.fact_crime(offense_id);
CREATE INDEX IF NOT EXISTS idx_fact_crime_location ON crime.fact_crime(location_id);

CREATE OR REPLACE VIEW crime.vw_daily_counts AS
SELECT
  date_key,
  COUNT(*) AS total_crimes
FROM crime.fact_crime
GROUP BY date_key;

CREATE OR REPLACE VIEW crime.vw_offense_breakdown AS
SELECT
  o.offense_name,
  c.date_key,
  COUNT(*) AS cnt
FROM crime.fact_crime f
JOIN crime.dim_offense o ON o.offense_id = f.offense_id
JOIN crime.dim_calendar c ON c.date_key = f.date_key
GROUP BY o.offense_name, c.date_key;

CREATE OR REPLACE VIEW crime.vw_hotspots AS
SELECT
  l.grid_x,
  l.grid_y,
  COUNT(*) AS incidents
FROM crime.fact_crime f
JOIN crime.dim_location l ON l.location_id = f.location_id
GROUP BY l.grid_x, l.grid_y;