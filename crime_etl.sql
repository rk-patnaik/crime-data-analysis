-- Example upsert pattern for calendar and dimensions.
INSERT INTO crime.dim_calendar(date_key, year, month, day, dow, week, is_weekend)
SELECT d::date,
       EXTRACT(YEAR FROM d)::int,
       EXTRACT(MONTH FROM d)::int,
       EXTRACT(DAY FROM d)::int,
       EXTRACT(DOW FROM d)::int,
       EXTRACT(WEEK FROM d)::int,
       CASE WHEN EXTRACT(DOW FROM d) IN (0,6) THEN TRUE ELSE FALSE END
FROM generate_series('2024-06-01'::date,'2024-07-31'::date, interval '1 day') d
ON CONFLICT (date_key) DO NOTHING;

-- Example: insert offenses
INSERT INTO crime.dim_offense (offense_code, offense_name) VALUES
('BURG','Burglary'),('ROBB','Robbery'),('ASSL','Assault'),
('THEF','Theft'),('VAND','Vandalism')
ON CONFLICT (offense_code) DO NOTHING;

-- Example: load locations (replace with your real GIS seeds)
-- Suppose we map city into a 10x10 grid
WITH grid AS (
  SELECT x AS grid_x, y AS grid_y
  FROM generate_series(0,9) x CROSS JOIN generate_series(0,9) y
)
INSERT INTO crime.dim_location(district, ward, lat, lon, grid_x, grid_y)
SELECT 'District '||grid_x, 'Ward '||grid_y, 0.0 + grid_x*0.01, 0.0 + grid_y*0.01, grid_x, grid_y
FROM grid
ON CONFLICT DO NOTHING;