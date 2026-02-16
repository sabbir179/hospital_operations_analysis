# 🏥 Hospital Operations Intelligence Platform

### End-to-End Healthcare Data Engineering & Machine Learning System

---

# 1️⃣ Executive Summary

This project demonstrates a production-oriented healthcare analytics and machine learning system designed to support hospital operational decision-making and patient admission risk prediction.

Healthcare organisations must continuously balance:

- Increasing patient demand
- Capacity constraints
- Operational efficiency
- Clinical risk management
- Patient experience

This platform simulates real-world hospital operational challenges by:

- Forecasting daily patient volume
- Monitoring average wait times
- Evaluating department-level admission rates
- Predicting patient admission probability in real time

The system follows a **Medallion Architecture (Bronze → Silver → Gold)**, integrates a DuckDB analytical warehouse, deploys a Random Forest admission prediction model, exposes REST endpoints via FastAPI, and delivers an interactive decision-support dashboard using Streamlit.

This project demonstrates the complete lifecycle of healthcare data science delivery — from data engineering to model deployment, cloud hosting, and governance considerations.

---

# 2️⃣ Data Governance & Responsible AI Considerations

Although this project uses non-sensitive educational data, the architecture reflects best practices required in real-world healthcare environments.

## Data Privacy & GDPR Alignment

In production healthcare systems:

- Patient-identifiable information (PII) must be anonymised or pseudonymised
- Data processing must comply with GDPR and the Data Protection Act (DPA)
- Access must follow role-based access control (RBAC)
- API endpoints must use encrypted communication (HTTPS)
- Data retention policies must be clearly defined

The project separates ingestion, transformation, analytics, and deployment layers to reflect secure system design principles.

## Model Governance

Healthcare ML systems require:

- Transparent evaluation metrics
- Bias assessment across demographic groups
- Continuous monitoring for data drift
- Clear documentation of model limitations
- Version-controlled model artifacts

This project includes:

- Reproducible training scripts
- Explicit feature engineering logic
- Versioned model artifact storage (GitHub Releases)
- Structured evaluation (ROC-AUC, recall analysis, threshold logic)

## Responsible AI in Healthcare

Machine learning systems in healthcare should:

- Support, not replace, clinical or operational judgement
- Be explainable to stakeholders
- Avoid unfair bias across population groups
- Be continuously monitored post-deployment

The modular architecture allows future integration of model monitoring, performance tracking, and audit logging.

---

# 3️⃣ System Architecture (Medallion Pattern)

## High-Level Architecture

```
Bronze Layer (Raw Ingested Data)
        │
        ▼
Silver Layer (Cleaned & Feature-Engineered Data)
        │
        ▼
Gold Layer (Analytical Warehouse - DuckDB)
        │
        ├── ML Model Training (Random Forest)
        │
        └── FastAPI Backend (Prediction + Metrics)
                │
                ▼
         Streamlit Dashboard (Frontend)
```

---

# 4️⃣ Technical Implementation

## 🟤 Bronze Layer (Raw Data)

- Original hospital patient encounter dataset
- Stored in `data/raw/`
- Represents ingested source data without transformation

This mirrors ingestion pipelines in cloud healthcare platforms.

---

## ⚪ Silver Layer (Cleaned & Structured Data)

- Data cleaning and validation
- Schema standardisation
- Missing value handling
- Feature engineering (time features, department encoding)
- Output stored as optimised Parquet

Script:

```
src/hospital_ops/data_loader.py
```

Output:

```
data/processed/encounters_clean.parquet
```

---

## 🟡 Gold Layer (Analytical Warehouse)

Built using DuckDB.

Purpose:

- Pre-aggregated daily patient metrics
- Department-level statistics
- Fast SQL-based analytical queries

Script:

```
src/hospital_ops/build_gold.py
```

Warehouse file:

```
warehouse/hospital_ops.duckdb
```

Gold tables include:

- `gold_daily_volume`
- `gold_department_waits`

This layer simulates analytical marts used in healthcare operations teams.

---

## 🤖 Machine Learning Layer

Model: Random Forest Classifier  
Target: `admitted` (binary classification)

Features:

- Age
- Gender
- Race
- Department ID
- Event hour
- Day of week
- Wait time

Training script:

```
src/hospital_ops/train_admission_model.py
```

Model artifact:

```
models/admission_model.joblib
```

Evaluation approach:

- ROC-AUC
- Recall analysis (operational risk perspective)
- Threshold-based classification logic

---

## ⚙ Backend (FastAPI)

Production API serving:

### Health Check

```
GET /health
```

### Admission Prediction

```
POST /predict
```

### Operational Metrics

```
GET /metrics/daily
GET /metrics/departments
```

Key characteristics:

- Loads model and warehouse via GitHub release artifacts
- SQL-based metrics queries
- Docker containerised
- Deployed on Render
- Separation of ML logic and API layer

---

## 🖥 Frontend (Streamlit Dashboard)

Interactive features:

- Admission probability calculator
- Daily patient volume trend
- Average wait time analysis
- Admission rate tracking
- Department-level comparison

Communicates with deployed FastAPI backend.

This mirrors real-world healthcare operational dashboards used by management teams.

---

# 5️⃣ Cloud Deployment Strategy

## Backend Deployment

Platform: Render

- Dockerised FastAPI service
- Artifact-driven model loading
- Environment-based configuration

Environment Variables:

```
MODEL_URL = GitHub release link to admission_model.joblib
DB_URL    = GitHub release link to hospital_ops.duckdb
```

---

## Frontend Deployment

Platform: Streamlit Community Cloud

- Separate frontend service
- Connected to production backend
- Scalable service separation

---

# 6️⃣ Results & Impact

This system demonstrates:

- Operational healthcare demand modelling
- Real-time admission risk prediction
- Department-level performance visibility
- Production ML system deployment
- Cloud-hosted analytics infrastructure

The architecture reflects how modern healthcare data science teams combine:

- Data engineering
- Statistical modelling
- API systems
- Cloud deployment
- Governance considerations

---

# 7️⃣ Repository Structure

```
hospital_operations_analysis/
│
├── app/                     # FastAPI backend
├── src/hospital_ops/        # Data + ML logic
├── ui/                      # Streamlit dashboard
├── data/
├── models/
├── warehouse/
├── sql/
├── notebooks/
├── reports/figures/
├── Dockerfile
├── requirements.txt
└── README.md
```

---

# 8️⃣ Future Improvements

- Model performance monitoring
- Data drift detection
- Feature importance dashboard
- CI/CD integration
- Role-based API authentication
- Azure / Kubernetes deployment
- Health economics modelling
- Time-series forecasting for demand
- Survival analysis extension

---

# Intended Use

This project is designed as an analytical and educational demonstration of healthcare operational intelligence and machine learning deployment.

It is not intended for clinical diagnosis or direct patient treatment decisions.

---

# Author

Sabbir Ahmed  
Healthcare Data Science & Machine Learning
