# 🏥 Hospital Operations Intelligence Platform

### End-to-End Data Engineering + Machine Learning + Cloud Deployment

Production-ready hospital analytics and admission prediction system built with:

- Data Engineering (ETL + Warehouse)
- Machine Learning (Random Forest Classifier)
- FastAPI Production Backend
- Streamlit Analytical Dashboard
- Docker + Cloud Deployment (Render + Streamlit Cloud)

---

# 🚀 Live Demo

**Backend API (FastAPI):**  
https://hospital-operations-analysis.onrender.com/docs

**Interactive Dashboard (Streamlit):**  
https://hospitalopanalysis.streamlit.app

---

# 🎯 Project Objective

Hospitals require operational intelligence to:

- Monitor daily patient volume
- Track average wait times
- Analyze department-level performance
- Predict patient admission probability in real time

This platform delivers:

✔ Data warehouse for operational analytics  
✔ ML-based admission prediction API  
✔ Cloud-hosted dashboard for decision-makers

---

# 🧱 System Architecture

## High-Level Architecture

```
Raw CSV Dataset
        │
        ▼
Silver Layer (Cleaned Parquet)
        │
        ▼
Gold Layer (DuckDB Warehouse)
        │
        ├── ML Model (Random Forest)
        │
        └── FastAPI Backend
                │
                ▼
         Streamlit Dashboard
```

---

# 🏗️ Architecture Layers

## 1️⃣ Data Engineering Layer

### Raw Layer

- Original hospital patient flow CSV
- Stored in `data/raw/`

### Silver Layer

- Data cleaning
- Feature engineering
- Missing value handling
- Parquet optimization

Script:

```
src/hospital_ops/data_loader.py
```

Output:

```
data/processed/encounters_clean.parquet
```

---

## 2️⃣ Gold Layer (Analytics Warehouse)

Built using DuckDB.

Purpose:

- Pre-aggregated daily metrics
- Department-level statistics
- Fast dashboard queries

Script:

```
src/hospital_ops/build_gold.py
```

Warehouse:

```
warehouse/hospital_ops.duckdb
```

---

## 3️⃣ Machine Learning Layer

Model: Random Forest Classifier  
Target: `admitted`

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

Saved artifact:

```
models/admission_model.joblib
```

---

## 4️⃣ Backend Layer (FastAPI)

Endpoints:

### Health Check

GET /health

### Admission Prediction

POST /predict

### Operational Metrics

GET /metrics/daily  
GET /metrics/departments

Responsibilities:

- Loads ML model from GitHub Release artifact
- Loads DuckDB warehouse from Release artifact
- Serves prediction + metrics endpoints
- Containerized with Docker

---

## 5️⃣ Frontend Layer (Streamlit)

Interactive dashboard:

- Admission probability calculator
- Daily patient volume
- Average wait time trends
- Admission rate tracking
- Department comparison

Communicates with FastAPI backend.

---

# 📂 Repository Structure

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

# ☁️ Cloud Deployment

## Backend

Platform: Render  
Containerized FastAPI service

Environment Variables:

```
MODEL_URL = direct download link to admission_model.joblib
DB_URL    = direct download link to hospital_ops.duckdb
```

Artifacts stored in GitHub Releases.

## Dashboard

Platform: Streamlit Cloud  
Connected to Render backend.

---

# 🧪 Local Development

Install dependencies:

```
pip install -r requirements.txt
```

Build Gold Layer:

```
python src/hospital_ops/build_gold.py
```

Train Model:

```
python src/hospital_ops/train_admission_model.py
```

Run API:

```
uvicorn app.main:app --reload
```

Run Dashboard:

```
streamlit run ui/streamlit_app.py
```

---

# 📊 EDA Notebook

Located in:

```
notebooks/01_eda_admission_prediction.ipynb
```

Includes:

- Admission distribution
- Admission rate by department
- ROC curve
- Confusion matrix
- Wait time analysis

---

# 🧠 Engineering Concepts Demonstrated

- Layered data architecture (Raw → Silver → Gold)
- Analytical data modeling
- Feature engineering
- Model serialization
- Production API design
- Artifact-based deployment strategy
- Backend/Frontend decoupling
- Docker containerization
- Cloud deployment

---

# 📈 Future Enhancements

- CI/CD pipeline
- Model monitoring
- Feature importance visualization
- Authentication layer
- Kubernetes deployment

---

# 👨‍💻 Author

Sabbir Ahmed  
Data Engineering & Machine Learning Project
