"""This frontend was made specifically for IBM HR data."""
import streamlit as st
import pandas as pd

from data_request import create_postgres_engine, pull_data


@st.cache_data()
def start_up():
    """On startup, we download the dataset."""
    engine = create_postgres_engine()
    return pull_data(engine)

@st.cache_resource()
def generate_results(data : pd.Dataframe):
    """Train a classification model, calcualte shap, and generate some EDA and visualizations"""

    pass

data = start_up()

    
