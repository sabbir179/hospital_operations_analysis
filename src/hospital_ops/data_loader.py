from __future__ import annotations

from pathlib import Path
import pandas as pd


RAW_DATA_PATH = Path("data/raw/healthcare_analytics_patient_flow_data.csv")
PROCESSED_DATA_PATH = Path("data/processed/encounters_clean.parquet")

REQUIRED_COLUMNS = [
    "Patient Id",
    "Patient Admission Date",
    "Patient Admission Time",
    "Merged",
    "Patient Gender",
    "Patient Age",
    "Patient Race",
    "Department Referral",
    "Patient Admission Flag",
    "Patient Satisfaction Score",
    "Patient Waittime",
]


def load_raw_data() -> pd.DataFrame:
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Raw data not found at: {RAW_DATA_PATH}\n"
            f"Put the CSV in data/raw/ and confirm the filename matches exactly."
        )
    return pd.read_csv(RAW_DATA_PATH)


def validate_schema(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def standardise_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {
        "Patient Id": "patient_id",
        "Patient Admission Date": "admission_date",
        "Patient Admission Time": "admission_time",
        "Merged": "merged_datetime",
        "Patient Gender": "gender",
        "Patient Age": "age",
        "Patient Race": "race",
        "Department Referral": "department",
        "Patient Admission Flag": "admitted_raw",
        "Patient Satisfaction Score": "satisfaction_score",
        "Patient Waittime": "wait_time_minutes",
    }
    return df.rename(columns=rename_map)


def parse_datetimes(df: pd.DataFrame) -> pd.DataFrame:
    # merged_datetime seems to be the combined date-time field; parse it first
    df["merged_datetime"] = pd.to_datetime(df["merged_datetime"], errors="coerce")

    # Also create a timestamp from admission_date + admission_time (as a fallback/check)
    dt_str = df["admission_date"].astype(str) + " " + df["admission_time"].astype(str)
    df["arrival_datetime"] = pd.to_datetime(dt_str, errors="coerce")

    # Prefer merged_datetime when available; otherwise use arrival_datetime
    df["event_datetime"] = df["merged_datetime"].combine_first(df["arrival_datetime"])

    # Time-based features for forecasting/ops patterns
    df["event_date"] = df["event_datetime"].dt.date
    df["event_hour"] = df["event_datetime"].dt.hour
    df["event_dayofweek"] = df["event_datetime"].dt.dayofweek  # Mon=0
    df["event_month"] = df["event_datetime"].dt.month

    return df


def map_admission_flag(df: pd.DataFrame) -> pd.DataFrame:
    """
    Map the raw admission flag values to binary 0/1.

    Raw values confirmed from your dataset:
      - "Admission" -> 1
      - "Not Admission" -> 0
    """
    s = df["admitted_raw"].astype(str).str.strip().str.lower()

    mapping = {
        "admission": 1,
        "not admission": 0,
        # extra robustness (won't hurt)
        "1": 1,
        "0": 0,
        "true": 1,
        "false": 0,
        "yes": 1,
        "no": 0,
    }

    df["admitted"] = s.map(mapping)

    return df


def basic_cleaning(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates()

    # Coerce numerics
    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df["wait_time_minutes"] = pd.to_numeric(df["wait_time_minutes"], errors="coerce")
    df["satisfaction_score"] = pd.to_numeric(df["satisfaction_score"], errors="coerce")

    # Map admitted flag from raw strings to 0/1
    df = map_admission_flag(df)

    # Basic validity filters (adjust later if needed)
    df = df[(df["age"].isna()) | ((df["age"] >= 0) & (df["age"] <= 120))]
    df = df[(df["wait_time_minutes"].isna()) | (df["wait_time_minutes"] >= 0)]
    df = df[
        (df["satisfaction_score"].isna())
        | ((df["satisfaction_score"] >= 0) & (df["satisfaction_score"] <= 10))
    ]
    df = df[df["admitted"].isin([0, 1]) | df["admitted"].isna()]

    # Strip categorical whitespace
    for col in ["gender", "race", "department"]:
        df[col] = df[col].astype(str).str.strip()

    return df


def save_processed(df: pd.DataFrame) -> None:
    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(PROCESSED_DATA_PATH, index=False)


def main() -> None:
    df = load_raw_data()
    validate_schema(df)
    df = standardise_columns(df)
    df = parse_datetimes(df)
    df = basic_cleaning(df)

    # Drop the raw admitted column after mapping (keep warehouse clean)
    if "admitted_raw" in df.columns:
        df = df.drop(columns=["admitted_raw"])

    save_processed(df)

    print("✅ Data ingestion complete")
    print(f"Rows: {len(df):,}")
    print("Admitted value counts (including missing):")
    print(df["admitted"].value_counts(dropna=False))
    print(f"Saved: {PROCESSED_DATA_PATH}")


if __name__ == "__main__":
    main()
