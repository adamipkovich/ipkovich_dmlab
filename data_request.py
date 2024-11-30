import os
from os import listdir,getcwd
import zipfile
import pandas as pd
import kaggle
from sqlalchemy import create_engine, text, Engine, inspect
import psycopg2 


def pull_kaggle_data(name : str) -> None:
    """Downloads kaggle dataset (uses kaggle.api)
    :args
        name (str) : name of the kaggle dataset  {user}/{dataset_name}
    """
    kaggle.api.authenticate()
    kaggle.api.dataset_download_files("pavansubhasht/ibm-hr-analytics-attrition-dataset", path = "temp")
    
def unzip_kaggle_data(loc : str):
    """This function finds all .zip files in the temp folder
    :args
        loc : """
    
    for dir in listdir(loc): ## This is a placeholder function if more than one dataset should be used.
        if dir.endswith(".zip"): ## find all zips in temp
            with zipfile.ZipFile(os.path.join(loc, dir), "r") as zip_file:
                zip_file.extractall("temp")
def read_kaggle_data(loc : str) -> dict:
    data = dict() # registry for datatables - each go to different tables in the DB
    for dir in listdir(loc): # I do this with consideration to multiple csv files in one zip
        if dir.endswith(".csv"): ## All .csv to memory
            name = dir.removesuffix(".csv").replace("-", "_").lower()
            data[name] = pd.read_csv(os.path.join(loc, dir))
    return data

def create_postgres_engine(dbname = "postgres",
    user = "postgres",
    host = "localhost",
    port ="5432",
    password = "mysecretpassword"):
    """Creates a sqlalchemy engine object for postgresql DB use."""    
    return create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}') 

def upload_datasets_to_db(data : dict[str, pd.DataFrame], engine : Engine) -> None:
    """Uses pandas .to_sql function to create/replace a table for a dataset in the data registry."""
    for k in data:
        data[k].to_sql(name=k, con = engine, if_exists ="replace")

def pull_data(engine : Engine, table_name : str = None) -> dict:
    data = dict()
    with engine.connect() as connection:
        ##get all table
        inspector = inspect(engine)
        for k in inspector.get_table_names():
            data[k] = pd.read_sql(f'SELECT * FROM public."{k}"', con=connection)
            data[k].set_index("index", inplace=True)
            #connection.execute(text(f'SELECT * FROM public."{k}"')).fetchall()
    return data

## Test
if __name__ == "__main__":
    ##TODO: create a decorator
    loc = os.path.join(getcwd(), "temp") 
    #pull_kaggle_data("pavansubhasht/ibm-hr-analytics-attrition-dataset")
    unzip_kaggle_data(loc) 
    data = read_kaggle_data(loc) # read in csv file
    engine = create_postgres_engine() #create engine
    upload_datasets_to_db(data, engine=engine)
    qdata = pull_data(engine)
    print(qdata)