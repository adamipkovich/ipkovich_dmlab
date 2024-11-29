"""This frontend was made specifically for IBM HR data."""
import streamlit as st
from data_request import create_postgres_engine, pull_data

@st.cache
def start_up():
    engine = create_postgres_engine()
    pull_data(engine)
    
start_up()

    
