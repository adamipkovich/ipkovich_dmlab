import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from data_request import pull_kaggle_data, read_kaggle_data, create_postgres_engine, upload_datasets_to_db

engine = None
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    ## set global variables
    dbname = os.environ["DBNAME"]
    user = os.environ["DBUSER"]
    host = os.environ["DBHOST"]
    port = os.environ["DBPOST"]
    password = os.environ["DBPASS"] #due to lack of time password is not secured. It SHOULD BE.
    engine = create_postgres_engine(dbname=dbname, user=user, host=host, port=port, password=password)
    yield
    


app = FastAPI(lifespan=lifespan)

@app.get("/")
def landing():
    return "Welcome to the kaggle collector service!"

@app.post("/connect")
def connect_to_db(request : Request):
    global engine
    req = dict(request.query_params)
    dbname = req.get("dbname")
    user = req.get("user")
    host = req.get("host")
    port = req.get("port")
    password = req.get("password")
    engine = create_postgres_engine(dbname=dbname, user=user, host=host, port=port, password=password)
    
@app.post("/pull")
def get_kaggle_dataset(request : Request):  
    global engine ## Errors from
    loc = os.path.join(os.getcwd(), "temp")   
    req = dict(request.query_params)
    name = req.get("name")
    pull_kaggle_data(name)
    data = read_kaggle_data(loc) # read in csv file
    upload_datasets_to_db(data, engine=engine)
    return "Successfully downloaded and sent the data to the DB."


if __name__ == "__main__":
    ## Test service with uvicorn
    os.environ["DBNAME"] = "postgres"
    os.environ["DBUSER"] = "postgres"
    os.environ["DBHOST"] = "localhost"
    os.environ["DBPOST"] = "5432"
    os.environ["DBPASS"] = "mysecretpassword"
    os.system("uvicorn collector_service:app --host localhost --port 8015")
    