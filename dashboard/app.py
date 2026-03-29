import streamlit as st

from analytics.impact_model import ImpactCalculator
from escalation_queue import render_queue


st.set_page_config(page_title="FinAgent")

st.title("Dashboard")

page = st.sidebar.radio("Navigation", ["Overview", "Escalation Queue"])

if page == "Overview":
    st.header("Overview")

    fte_saved_hours = ImpactCalculator.calculate_fte_saved(1500)
    dso_reduction_days = ImpactCalculator.calculate_dso_reduction(
        total_ar=1250000.0,
        credit_sales=18500000.0,
        previous_dso=36.5,
    )

    col1, col2 = st.columns(2)
    col1.metric("Total FTE Hours Saved", f"{fte_saved_hours:.2f} h")
    col2.metric("DSO Reduction", f"{dso_reduction_days:.2f} days")
else:
    render_queue()
