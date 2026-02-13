-- name: department_metrics
SELECT
  department,
  total_encounters,
  avg_wait_time_minutes,
  admission_rate
FROM gold_department_waits
ORDER BY total_encounters DESC;

-- name: daily_volume
SELECT
  event_date,
  total_encounters,
  avg_wait_time_minutes,
  admission_rate
FROM gold_daily_volume
ORDER BY event_date;
