import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from data_request import create_postgres_engine, pull_data
from modelling import *

from fastapi.responses import FileResponse
import pickle

engine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Connect to the DB on startup."""
    ## get global variables -> Docker may be used to define credentials
    global engine
    dbname = os.environ["DBNAME"]
    user = os.environ["DBUSER"]
    host = os.environ["DBHOST"]
    port = os.environ["DBPOST"]
    password = os.environ["DBPASS"] #TODO : secure password passing
    engine = create_postgres_engine(dbname=dbname, user=user, host=host, port=port, password=password)
    
    yield
    
app = FastAPI(lifespan=lifespan)

@app.get("/")
def landing():
    """API to check which service is opened on this port."""
    return "Welcome to the IMB HR explainer service! This only works with wa_fn_usec__hr_employee_attrition, yet!"

@app.post("/connect")
def connect_to_db(request : Request):
    """Use if you could not join to the DB on runtime"""
    global engine
    req = dict(request.query_params)
    dbname = req.get("dbname")
    user = req.get("user")
    host = req.get("host")
    port = req.get("port")
    password = req.get("password")
    engine = create_postgres_engine(dbname=dbname, user=user, host=host, port=port, password=password)

@app.post("/explain/{table_name}")
def explain(table_name : str):
    """Pull table 'table_name' from DB, preprocess data, train model and return an Explainer object pickler as a FileResponse."""
    global engine
    
    df = pull_data(engine, table_name=table_name)
    X_train, X_test, y_train, y_test = preprocess_hr_data(df) ## will not work with other than "wa_fn_usec__hr_employee_attrition"
    model = create_classification_model_xgboost(X_train, y_train)
    
    ##TODO save/export model -- MLFLOW service... 
    
    assert check_model(model,X_test, y_test) is True
    explainer = calculate_shap_values(model, pd.concat((X_train, X_test), axis = "index"))## do explanation, 
    with open("explainer.pkl", "wb") as f:
        pickle.dump(explainer, f)
    
    return FileResponse("explainer.pkl")
    ##send explainer to frontend!!!

if __name__ == "__main__":
    ## Test service with uvicorn
    os.environ["DBNAME"] = "postgres"
    os.environ["DBUSER"] = "postgres"
    os.environ["DBHOST"] = "localhost"
    os.environ["DBPOST"] = "5432"
    os.environ["DBPASS"] = "mysecretpassword"
    os.system("uvicorn explainer_service:app --host localhost --port 8010")