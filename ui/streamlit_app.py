import os
import requests
import pandas as pd
import streamlit as st

API_BASE = os.getenv("API_BASE", "https://hospital-operations-analysis.onrender.com")

st.set_page_config(page_title="Hospital Operations Dashboard", layout="wide")
st.title("🏥 Hospital Operations Dashboard")
st.caption("Metrics + admission prediction powered by FastAPI + DuckDB + ML model.")

# ---------------------------
# Helpers
# ---------------------------
def get_json(path: str):
    url = f"{API_BASE}{path}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()

def post_json(path: str, payload: dict):
    url = f"{API_BASE}{path}"
    r = requests.post(url, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()

# ---------------------------
# Sidebar: Prediction form
# ---------------------------
st.sidebar.header("Settings")
st.sidebar.write("Backend API:")
st.sidebar.code(API_BASE)

st.sidebar.header("Admission Prediction")
age = st.sidebar.number_input("Age", min_value=0, max_value=120, value=45)
gender = st.sidebar.selectbox("Gender", ["Male", "Female", "Other"])
race = st.sidebar.text_input("Race", value="White")
department_id = st.sidebar.number_input("Department ID", min_value=0, value=1)
event_hour = st.sidebar.slider("Event hour", 0, 23, 14)
event_dayofweek = st.sidebar.slider("Day of week (Mon=0)", 0, 6, 2)
wait_time_minutes = st.sidebar.number_input("Wait time (minutes)", min_value=0.0, value=30.0)

if st.sidebar.button("Predict admission"):
    payload = {
        "age": float(age),
        "gender": gender,
        "race": race,
        "department_id": int(department_id),
        "event_hour": int(event_hour),
        "event_dayofweek": int(event_dayofweek),
        "wait_time_minutes": float(wait_time_minutes),
    }
    try:
        pred = post_json("/predict", payload)
        st.sidebar.success(f"Probability: {pred['admitted_probability']:.3f}")
        st.sidebar.info(f"Prediction (>=0.5): {pred['admitted_prediction']}")
    except Exception as e:
        st.sidebar.error(f"Prediction failed: {e}")

# ---------------------------
# Main dashboard tabs
# ---------------------------
tab1, tab2 = st.tabs(["📊 Daily Ops", "🏥 Departments"])

with tab1:
    st.subheader("Daily patient volume (Gold layer)")
    try:
        data = get_json("/metrics/daily-volume")
        df = pd.DataFrame(data)

        if "event_date" in df.columns:
            df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce")

        st.line_chart(df.set_index("event_date")["total_encounters"])

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Avg wait time (daily)")
            st.line_chart(df.set_index("event_date")["avg_wait_time_minutes"])
        with col2:
            st.subheader("Admission rate (daily)")
            st.line_chart(df.set_index("event_date")["admission_rate"])

        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Failed to load daily metrics: {e}")

with tab2:
    st.subheader("Department metrics")
    try:
        data = get_json("/metrics/department")
        df = pd.DataFrame(data)

        df_top = df.head(15)

        st.subheader("Total encounters (top 15)")
        st.bar_chart(df_top.set_index("department")["total_encounters"])

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Avg wait time by department (top 15)")
            st.bar_chart(df_top.set_index("department")["avg_wait_time_minutes"])
        with col2:
            st.subheader("Admission rate by department (top 15)")
            st.bar_chart(df_top.set_index("department")["admission_rate"])

        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Failed to load department metrics: {e}")

st.markdown("---")
st.caption("Streamlit frontend + FastAPI backend deployed on Render.")
