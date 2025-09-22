import streamlit as st
import src.db.DbHelper as DbHelper

def termSelectionBox():
    terms = DbHelper.getExistingTerms()
    terms = [term[0] for term in terms]
    terms = ["Select Term"] + terms
    termSelector = st.sidebar.selectbox("Select Term", terms, index=0)

    return termSelector

