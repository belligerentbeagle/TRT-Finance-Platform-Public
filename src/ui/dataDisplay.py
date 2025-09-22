import streamlit as st
import src.db.dbHelper as dbHelper

def displayTermData(selectedTerm):
    data = dbHelper.getTermData(selectedTerm)
    st.write(data)
    
    
