from __future__ import annotations

import os
from pathlib import Path
from urllib.request import urlretrieve

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field


MODEL_PATH = Path("models/admission_model.joblib")

app = FastAPI(
    title="Hospital Operations ML API",
    description="Admission prediction API (demo).",
    version="0.1.0",
)


class AdmissionRequest(BaseModel):
    age: float | None = Field(default=None, ge=0, le=120)
    gender: str | None = None
    race: str | None = None
    department_id: int | None = None
    event_hour: int | None = Field(default=None, ge=0, le=23)
    event_dayofweek: int | None = Field(default=None, ge=0, le=6)
    wait_time_minutes: float | None = Field(default=None, ge=0)


class AdmissionResponse(BaseModel):
    admitted_probability: float
    admitted_prediction: int


model = None


def ensure_model() -> None:
    """Ensure model file exists locally; download it if needed."""
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    if MODEL_PATH.exists():
        return

    model_url = os.getenv("MODEL_URL")
    if not model_url:
        raise RuntimeError(
            "Model file is missing and MODEL_URL is not set. "
            "Set MODEL_URL to a direct download link for admission_model.joblib."
        )

    print(f"⬇️ Downloading model from MODEL_URL to {MODEL_PATH} ...")
    urlretrieve(model_url, MODEL_PATH)  # noqa: S310
    print("✅ Model downloaded")


@app.on_event("startup")
def load_model():
    global model
    ensure_model()
    model = joblib.load(MODEL_PATH)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=AdmissionResponse)
def predict(payload: AdmissionRequest):
    row = {
        "age": payload.age,
        "gender": payload.gender,
        "race": payload.race,
        "department_id": payload.department_id,
        "event_hour": payload.event_hour,
        "event_dayofweek": payload.event_dayofweek,
        "wait_time_minutes": payload.wait_time_minutes,
    }

    X = pd.DataFrame([row])
    proba = float(model.predict_proba(X)[:, 1][0])
    pred = int(proba >= 0.5)

    return AdmissionResponse(admitted_probability=proba, admitted_prediction=pred)
