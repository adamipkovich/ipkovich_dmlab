"""This frontend was made specifically for IBM HR data."""
import os
import pickle
import streamlit as st
import pandas as pd
import shap
import requests
import matplotlib.pyplot as plt
from data_request import create_postgres_engine, pull_data, pull_kaggle_data, unzip_kaggle_data, read_kaggle_data, upload_datasets_to_db
from modelling import preprocess_hr_data, create_classification_model_xgboost, check_model, calculate_shap_values


# init global variable for explainer
if 'explainer' not in st.session_state:
    st.session_state['explainer'] = None

# do not cache! -> this is a command!
def api_call(url = "http://localhost:8015", kaggle_project = "pavansubhasht/ibm-hr-analytics-attrition-dataset"):
    """Ask the collector service to pull data from kaggle."""
    req_data = dict()
    req_data["name"] = kaggle_project
    response = requests.post(url=url + "/pull", data=req_data)
    return response.status_code == 200


## Cache so that it does not have to retrain model each render cycle
@st.cache_resource
def get_explainer(url ="http://localhost:8010", table_name = "wa_fn_usec__hr_employee_attrition"):
    """Get shap explainer from explainer_service so that we can visualize the contributions of factors to Employee Attrition."""
    response = requests.post(url=url + f"/explain/{table_name}")
    assert response.status_code == 200, "There is something wrong with the explainer service."
    _explainer = pickle.loads(response.content)
    return _explainer



##Generate figure - only create figures once.
@st.cache_resource
def create_fig(_explainer,  mode = "Summary", id = 0):
    """Creates figures for the frontend to showcase to the decision maker. Mode and id should not be exposed to a user, and should be handled dynamically inside the frontend.
    """
    if _explainer is None:
        return plt.figure(), "" # show nothing
    
    if mode == "Summary":
        desc ="""- Positive shapley value influences towards attrition
                - Grey values are categorical value
                - Colors show feature value, x-axis shows the contribution towards attrition
                - Features are ordered per importance
                - This only describes the model. These are NOT causal results. The next step would be causal inference and experimental design to validate hypotheses.
                - The thicker parts show the density of the data at a specific feature value range.
                This analysis can help understand which factors play an important role in the model's decision for employee turnover. Generally speaking, High daily rate, low distance from home, providing stocks, high environment satisfaction, generally higher monthly income can help retain employees according to the model. 
                """
        #shap.summary_plot(_explainer)
        plt.figure()
        shap.plots.beeswarm(_explainer, max_display=20)
        return plt.gcf(), desc
    elif mode == "Individual":
            desc = """This figure shows how a specific variable values influences the employee turnover. On the left hand side, the variable names also have values, which cause change in the output by the number shown in the bar. 
            For individual analyses, one can show why the Employee decided as such. Of course this is according to the model, and one should always confirm with the Employees."""
            shap.plots.waterfall(_explainer[id])
            
            return plt.gcf(), desc
    
    return plt.figure(), "" # otherwise show nothing.


#%% Frontend features

with st.sidebar:
    st.title("Welcome to Employee attrition evaluation Dashboard!")
    st.text("The dashboard focuses employee attrition based on the IBM HR dataset. This analysis aims to provide answers to which factors contributed to employee turnover, and how significantly can one factor infuence the decision of the ML model. As you may know, employee turnover is very costly - companies have to retrain new employees, paying hiring fees and marketing, and effective time of the new employees will not be high in the first three months.")
    st.text("This dashboard pulls data from Kaggle, trains a xgboost classification model and creates Shapley-based explanation of variables' contribution to Employee Attrition")
    st.text("This interface requires a postgres DB already running in Docker, already configured, Collector Service and Explainer Service running.")
    if st.button("Pull Data from kaggle!"):
        if not api_call():
            st.text("API call was unsuccessful. Please check whether you have access token to Kaggle.")
        else:
            st.text("API loaded data to DB.")
    
    if st.button("Get explanation!"):
        try:
            st.session_state['explainer'] = get_explainer()
        except:
            st.text("Try pulling data first!")
            
    option = st.selectbox("Figure type", ["Summary", "Individual"], placeholder= "Please pull data from kaggle first.") 
    if option == "Individual":
        id = st.selectbox("Employee number (for individual analysis)", range(st.session_state['explainer'].shape[0]))   

### TODO: description on how to interpret
fig, desc = create_fig(_explainer=st.session_state['explainer'], mode = option, id = id)    
st.pyplot(fig)
st.text(desc)
