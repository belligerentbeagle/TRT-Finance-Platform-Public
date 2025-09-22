import streamlit as st
import src.db.DbHelper as DbHelper

def GradYearSelectionBox(initial_value=None, key_prefix=""):
    grad_years = DbHelper.getAvailableGradYears()
    if initial_value:
        grad_yearSelector = st.selectbox("Select Graduation Year (from A levels)", grad_years, index=grad_years.index(initial_value), 
                                                 key=f"{key_prefix}_Preselectedgrad_yearSelector")
    else:
        grad_yearSelector = st.selectbox("Select Graduation Year (from A levels)", grad_years,
                                                 key=f"{key_prefix}_Defaultgrad_yearSelector")
    return grad_yearSelector