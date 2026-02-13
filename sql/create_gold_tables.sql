-- ============================================================
-- Gold layer build script (DuckDB)
-- Builds:
--   - silver_encounters (view over parquet)
--   - dim_date
--   - dim_department
--   - fact_encounter
--   - gold_daily_volume
--   - gold_department_waits
-- ============================================================

-- Make the build re-runnable
DROP TABLE IF EXISTS gold_department_waits;
DROP TABLE IF EXISTS gold_daily_volume;
DROP TABLE IF EXISTS fact_encounter;
DROP TABLE IF EXISTS dim_department;
DROP TABLE IF EXISTS dim_date;
DROP VIEW  IF EXISTS silver_encounters;

-- ------------------------------------------------------------
-- Silver layer: view over the parquet
-- Note: build_gold.py sets `silver_parquet_path` to parquet file
-- ------------------------------------------------------------
CREATE VIEW silver_encounters AS
SELECT *
FROM read_parquet('data/processed/encounters_clean.parquet');


-- ------------------------------------------------------------
-- Dimensions
-- ------------------------------------------------------------

-- Date dimension (from event_date)
CREATE TABLE dim_date AS
SELECT DISTINCT
  CAST(event_date AS DATE)               AS date_id,
  EXTRACT(year  FROM CAST(event_date AS DATE)) AS year,
  EXTRACT(month FROM CAST(event_date AS DATE)) AS month,
  EXTRACT(day   FROM CAST(event_date AS DATE)) AS day,
  EXTRACT(dow   FROM CAST(event_date AS DATE)) AS day_of_week
FROM silver_encounters
WHERE event_date IS NOT NULL;

-- Department dimension
CREATE TABLE dim_department AS
SELECT
  ROW_NUMBER() OVER (ORDER BY department) AS department_id,
  department
FROM (
  SELECT DISTINCT department
  FROM silver_encounters
  WHERE department IS NOT NULL
    AND lower(trim(CAST(department AS VARCHAR))) <> 'nan'
) d;

-- ------------------------------------------------------------
-- Fact table
-- ------------------------------------------------------------
CREATE TABLE fact_encounter AS
SELECT
  s.patient_id,
  CAST(s.event_date AS DATE)            AS date_id,
  d.department_id                        AS department_id,

  -- keep original labels too (helpful for EDA/debug)
  s.department                           AS department,

  s.gender,
  s.race,

  CAST(s.age AS DOUBLE)                  AS age,
  CAST(s.wait_time_minutes AS DOUBLE)    AS wait_time_minutes,
  CAST(s.satisfaction_score AS DOUBLE)   AS satisfaction_score,

  CAST(s.event_hour AS INTEGER)          AS event_hour,
  CAST(s.event_dayofweek AS INTEGER)     AS event_dayofweek,
  CAST(s.event_month AS INTEGER)         AS event_month,

  -- admitted is already 0/1 in your silver layer now
  CAST(s.admitted AS INTEGER)            AS admitted

FROM silver_encounters s
LEFT JOIN dim_department d
  ON s.department = d.department;

-- ------------------------------------------------------------
-- Gold aggregates (for dashboards + monitoring)
-- ------------------------------------------------------------

-- Daily volume (time series)
CREATE TABLE gold_daily_volume AS
SELECT
  date_id AS event_date,
  COUNT(*) AS total_encounters,
  AVG(wait_time_minutes) AS avg_wait_time_minutes,
  AVG(satisfaction_score) AS avg_satisfaction_score,
  AVG(admitted) AS admission_rate
FROM fact_encounter
GROUP BY date_id
ORDER BY date_id;

-- Department wait / volume / admission rate
CREATE TABLE gold_department_waits AS
SELECT
  department_id,
  department,
  COUNT(*) AS total_encounters,
  AVG(wait_time_minutes) AS avg_wait_time_minutes,
  AVG(satisfaction_score) AS avg_satisfaction_score,
  AVG(admitted) AS admission_rate
FROM fact_encounter
GROUP BY department_id, department
ORDER BY avg_wait_time_minutes DESC;
