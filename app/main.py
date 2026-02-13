from __future__ import annotations

import os
from pathlib import Path
from urllib.request import urlretrieve

import duckdb
import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field


# -----------------------
# Paths (inside container)
# -----------------------
MODEL_PATH = Path("models/admission_model.joblib")
DB_PATH = Path("warehouse/hospital_ops.duckdb")

# SQL files (in your repo)
METRICS_SQL_PATH = Path("sql/metrics_queries.sql")


# -----------------------
# FastAPI app
# -----------------------
app = FastAPI(
    title="Hospital Operations ML API",
    version="0.1.0",
    description="Admission prediction + operational metrics (demo).",
)


# -----------------------
# Request / Response schemas
# -----------------------
class AdmissionRequest(BaseModel):
    age: float = Field(..., ge=0, le=120)
    gender: str
    race: str
    department_id: int
    event_hour: int = Field(..., ge=0, le=23)
    event_dayofweek: int = Field(..., ge=0, le=6)
    wait_time_minutes: float = Field(..., ge=0)


class AdmissionResponse(BaseModel):
    admitted_probability: float
    admitted_prediction: int


# -----------------------
# Globals (loaded at startup)
# -----------------------
MODEL = None


# -----------------------
# Helpers
# -----------------------
def ensure_file(path: Path, env_var: str, friendly_name: str) -> None:
    """
    Ensure a file exists locally. If missing, download from the URL in env_var.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        return

    url = os.getenv(env_var)
    if not url:
        raise RuntimeError(
            f"{friendly_name} is missing and {env_var} is not set. "
            f"Set {env_var} to a direct download link."
        )

    print(f"⬇️ Downloading {friendly_name} from {env_var} to {path} ...")
    urlretrieve(url, path)  # noqa: S310
    print(f"✅ {friendly_name} downloaded")


def load_metrics_sql() -> dict[str, str]:
    """
    Load named SQL queries from sql/metrics_queries.sql.

    Format in file:
      -- name: department_metrics
      SELECT ...

      -- name: daily_volume
      SELECT ...
    """
    if not METRICS_SQL_PATH.exists():
        raise RuntimeError(
            f"Missing SQL file: {METRICS_SQL_PATH}. "
            "Make sure you committed sql/metrics_queries.sql"
        )

    text = METRICS_SQL_PATH.read_text(encoding="utf-8")
    blocks = {}
    current_name = None
    current_sql_lines = []

    for line in text.splitlines():
        line_stripped = line.strip()
        if line_stripped.lower().startswith("-- name:"):
            # save previous
            if current_name and current_sql_lines:
                blocks[current_name] = "\n".join(current_sql_lines).strip()
            # start new
            current_name = line_stripped.split(":", 1)[1].strip()
            current_sql_lines = []
        else:
            # accumulate lines
            if current_name is not None:
                current_sql_lines.append(line)

    # save last
    if current_name and current_sql_lines:
        blocks[current_name] = "\n".join(current_sql_lines).strip()

    if not blocks:
        raise RuntimeError(
            "No named SQL blocks found in sql/metrics_queries.sql. "
            "Add blocks like: -- name: department_metrics"
        )

    return blocks


# Load SQL blocks once (on import)
METRICS_QUERIES = load_metrics_sql()


def duckdb_query_to_records(sql: str) -> list[dict]:
    con = duckdb.connect(str(DB_PATH), read_only=True)
    df = con.execute(sql).fetchdf()
    # Make dates JSON-friendly
    for col in df.columns:
        if "date" in col.lower():
            df[col] = df[col].astype(str)
    return df.to_dict(orient="records")


# -----------------------
# Startup
# -----------------------
@app.on_event("startup")
def startup() -> None:
    global MODEL

    # Model + DB are downloaded in production (Render) via env vars
    ensure_file(MODEL_PATH, "MODEL_URL", "Model file (admission_model.joblib)")
    ensure_file(DB_PATH, "DB_URL", "DuckDB warehouse (hospital_ops.duckdb)")

    MODEL = joblib.load(MODEL_PATH)
    print("✅ Model loaded")


# -----------------------
# Routes
# -----------------------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=AdmissionResponse)
def predict(req: AdmissionRequest):
    # Build one-row dataframe that matches training features
    X = pd.DataFrame(
        [{
            "age": req.age,
            "gender": req.gender,
            "race": req.race,
            "department_id": req.department_id,
            "event_hour": req.event_hour,
            "event_dayofweek": req.event_dayofweek,
            "wait_time_minutes": req.wait_time_minutes,
        }]
    )

    proba = float(MODEL.predict_proba(X)[:, 1][0])
    pred = int(proba >= 0.5)

    return AdmissionResponse(admitted_probability=proba, admitted_prediction=pred)


@app.get("/metrics/department")
def metrics_department():
    sql = METRICS_QUERIES["department_metrics"]
    return duckdb_query_to_records(sql)


@app.get("/metrics/daily-volume")
def metrics_daily_volume():
    sql = METRICS_QUERIES["daily_volume"]
    return duckdb_query_to_records(sql)
