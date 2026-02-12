from pathlib import Path
import duckdb

DB_PATH = Path("warehouse/hospital_ops.duckdb")
SILVER_PATH = Path("data/processed/encounters_clean.parquet")


def main():
    if not SILVER_PATH.exists():
        raise FileNotFoundError(f"Silver file not found: {SILVER_PATH}")

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(DB_PATH))

    # Create a view over Silver parquet (DuckDB reads parquet directly)
    con.execute("DROP VIEW IF EXISTS silver_encounters;")
    con.execute(f"""
        CREATE VIEW silver_encounters AS
        SELECT * FROM read_parquet('{SILVER_PATH.as_posix()}');
    """)

    # Dimensions
    con.execute("DROP TABLE IF EXISTS dim_department;")
    con.execute("""
        CREATE TABLE dim_department AS
        SELECT
            dense_rank() OVER (ORDER BY department) AS department_id,
            department AS department_name
        FROM (SELECT DISTINCT department FROM silver_encounters)
        WHERE department IS NOT NULL AND department <> 'nan';
    """)

    con.execute("DROP TABLE IF EXISTS dim_date;")
    con.execute("""
        CREATE TABLE dim_date AS
        SELECT DISTINCT
            CAST(event_date AS DATE) AS date,
            EXTRACT(year FROM CAST(event_date AS DATE)) AS year,
            EXTRACT(month FROM CAST(event_date AS DATE)) AS month,
            EXTRACT(day FROM CAST(event_date AS DATE)) AS day,
            EXTRACT(dow FROM CAST(event_date AS DATE)) AS day_of_week
        FROM silver_encounters
        WHERE event_date IS NOT NULL;
    """)

    # Fact table
    con.execute("DROP TABLE IF EXISTS fact_encounter;")
    con.execute("""
        CREATE TABLE fact_encounter AS
        SELECT
            row_number() OVER () AS encounter_id,
            patient_id,
            d.department_id,
            CAST(s.event_datetime AS TIMESTAMP) AS event_datetime,
            CAST(s.event_date AS DATE) AS event_date,
            s.event_hour,
            s.event_dayofweek,
            s.event_month,
            s.age,
            s.gender,
            s.race,
            s.wait_time_minutes,
            s.satisfaction_score,
            CAST(s.admitted AS INTEGER) AS admitted
        FROM silver_encounters s
        LEFT JOIN dim_department d
            ON s.department = d.department_name;
    """)

    # Gold aggregates (useful for ops + forecasting)
    con.execute("DROP TABLE IF EXISTS gold_daily_volume;")
    con.execute("""
        CREATE TABLE gold_daily_volume AS
        SELECT
            event_date,
            COUNT(*) AS encounters,
            AVG(wait_time_minutes) AS avg_wait_time_minutes,
            AVG(satisfaction_score) AS avg_satisfaction
        FROM fact_encounter
        GROUP BY event_date
        ORDER BY event_date;
    """)

    con.execute("DROP TABLE IF EXISTS gold_department_waits;")
    con.execute("""
        CREATE TABLE gold_department_waits AS
        SELECT
            department_id,
            COUNT(*) AS encounters,
            AVG(wait_time_minutes) AS avg_wait_time_minutes,
            quantile_cont(wait_time_minutes, 0.5) AS median_wait_time_minutes,
            quantile_cont(wait_time_minutes, 0.9) AS p90_wait_time_minutes
        FROM fact_encounter
        GROUP BY department_id
        ORDER BY p90_wait_time_minutes DESC;
    """)

    con.close()

    print("✅ Gold layer built successfully")
    print(f"Saved DuckDB database to: {DB_PATH}")


if __name__ == "__main__":
    main()
