"""This frontend was made specifically for IBM HR data."""
import os

import streamlit as st
import pandas as pd
import shap
import matplotlib.pyplot as plt
from data_request import create_postgres_engine, pull_data, unzip_kaggle_data, read_kaggle_data, upload_datasets_to_db
from modelling import preprocess_hr_data, create_classification_model_xgboost, check_model, calculate_shap_values


if 'explainer' not in st.session_state:
    st.session_state['explainer'] = None

if 'data' not in st.session_state:
    st.session_state['data'] = None

def api_call():
    loc = os.path.join(os.getcwd(), "temp") 
    #pull_kaggle_data("pavansubhasht/ibm-hr-analytics-attrition-dataset")
    try:
        unzip_kaggle_data(loc) 
        data = read_kaggle_data(loc) # read in csv file
        engine = create_postgres_engine() #create engine
        upload_datasets_to_db(data, engine=engine)
        return True
    except:
        return False

@st.cache_data
def pull_data_from_db():
    """On startup, we download the dataset."""
    engine = create_postgres_engine()
    df = pull_data(engine)
    X_train, X_test, y_train, y_test = preprocess_hr_data(df["wa_fn_usec__hr_employee_attrition"])
    return X_train, X_test, y_train, y_test

@st.cache_resource
def create_explainer(X_train, X_test, y_train, y_test):
    model = create_classification_model_xgboost(X_train, y_train)
    assert check_model(model,X_test, y_test) is True
    return calculate_shap_values(model, pd.concat((X_train, X_test), axis = "index"))



@st.cache_resource
def create_fig(_explainer, X, mode = "Summary", id = 0):
    
    if _explainer is None or X is None:
        return plt.figure(), ""
    
    if mode == "Summary":
        desc ="""- Positive shapley value influences towards attrition
                - Grey values are categorical value
                - Colors show feature value, x-axis shows the contribution towards attrition
                - Features are ordered per importance
                - This only describes the model. These are NOT causal results. The next step would be causal inference and experimental design to validate hypotheses.
                - The thicker parts show the density of the data at a specific feature value range.
                This analysis can help understand which factors play an important role in the model's decision for employee turnover. Generally speaking, High daily rate, balanced work/life, promotions, providing stocks, environment satisfaction can help retain employees according ot the model. 
                """
        shap.summary_plot(_explainer, X)
        return plt.gcf(), desc
    elif mode == "Individual":
            desc = """This figure shows how a specific variable values influences the employee turnover. On the left hand side, the variable names also have values, which cause change in the output by the number shown in the bar. 
            For individual analyses, one can show why the Employee decided as such. Of course this is according to the model, and one should always confirm with the Employees."""
            shap.plots.waterfall(_explainer[id])
            
            return plt.gcf(), desc
    
    return plt.figure(), ""
    

with st.sidebar:
    st.title("Welcome to Employee attrition evaluation Dashboard!")
    st.text("The dashboard focuses employee attrition based on the IBM HR dataset. This analysis aims to provide answers to which factors contributed to employee turnover, and how significantly can one factor infuence the decision of the ML model. As you may know, employee turnover is very costly - companies have to retrain new employees, paying hiring fees and marketing, and effective time of the new employees will not be high in the first three months.")
    st.text("This dashboard pulls data from Kaggle, trains a classification model and creates Shapley-based explanation of variables's contribution to Employee Attrition")
    st.text("For acquiring data, you must have a postgres DB already running in Docker, already configured.")
    if st.button("Pull Data from kaggle"):
        if not api_call():
            st.text("API call was unsuccessful. Please check whether you have access token to Kaggle.")
        else:
            X_train, X_test, y_train, y_test = pull_data_from_db()
            st.session_state["data"] = pd.concat((X_train, X_test), axis="index")
            st.session_state["data"].sort_index()
            st.session_state['explainer'] = create_explainer(X_train, X_test, y_train, y_test )
    
    if st.button("Explain data!"):
        try:
            X_train, X_test, y_train, y_test = pull_data_from_db()
            st.session_state["data"] = pd.concat((X_train, X_test), axis="index")
            st.session_state["data"].sort_index()
            st.session_state['explainer'] = create_explainer(X_train, X_test, y_train, y_test )
        except:
            st.text("Try pulling data first!")
            
    option = st.selectbox("Figure type", ["Summary", "Individual"], placeholder= "Please pull data from kaggle first.") 
    if st.session_state["data"] is not None:
        id = st.selectbox("Employee number (for individual analysis)", st.session_state["data"].index.tolist())   

### TODO: description on how to interpret
fig, desc = create_fig(_explainer=st.session_state['explainer'], X = st.session_state["data"], mode = option, id = id)    
st.pyplot(fig)
st.text(desc)
