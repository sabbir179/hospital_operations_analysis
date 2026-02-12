from pathlib import Path
import duckdb
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import roc_auc_score, classification_report
from sklearn.ensemble import RandomForestClassifier
import joblib

DB_PATH = Path("warehouse/hospital_ops.duckdb")
MODEL_PATH = Path("models/admission_model.joblib")


def load_training_data() -> pd.DataFrame:
    con = duckdb.connect(str(DB_PATH))

    # Minimal, leakage-safe features available at/near arrival time
    query = """
        SELECT
            age,
            gender,
            race,
            department_id,
            event_hour,
            event_dayofweek,
            wait_time_minutes,
            admitted
        FROM fact_encounter
        WHERE admitted IS NOT NULL
    """
    df = con.execute(query).fetchdf()
    con.close()
    return df


def main():
    df = load_training_data()

    X = df.drop(columns=["admitted"])
    y = df["admitted"].astype(int)

    # Split (simple random split for now; later we can do time-based split)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    numeric_features = ["age", "event_hour", "event_dayofweek", "wait_time_minutes"]
    categorical_features = ["gender", "race", "department_id"]

    numeric_transformer = Pipeline(
        steps=[("imputer", SimpleImputer(strategy="median"))]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ]
    )

    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
    )

    clf = Pipeline(steps=[("preprocessor", preprocessor), ("model", model)])

    clf.fit(X_train, y_train)

    y_proba = clf.predict_proba(X_test)[:, 1]
    y_pred = (y_proba >= 0.5).astype(int)

    auc = roc_auc_score(y_test, y_proba)

    print("✅ Admission model trained")
    print("ROC-AUC:", round(auc, 4))
    print("\nClassification Report (threshold=0.50):")
    print(classification_report(y_test, y_pred))

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf, MODEL_PATH)
    print(f"\n✅ Saved model to: {MODEL_PATH}")


if __name__ == "__main__":
    main()
