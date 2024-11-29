import os
from os import listdir,getcwd
import zipfile
import pandas as pd
import kaggle

def pull_kaggle_data(name : str) -> None:
    """Downloads kaggle dataset (uses kaggle.api)
    :args
        name (str) : name of the kaggle dataset  {user}/{dataset_name}
    """
    kaggle.api.authenticate()
    kaggle.api.dataset_download_files("pavansubhasht/ibm-hr-analytics-attrition-dataset", path = "temp")
    
def unzip_kaggle_data(loc : str):
    """This function finds all .zip files in the temp folder"""
    
    for dir in listdir(loc): ## This is a placeholder function if more than one dataset should be used.
        if dir.endswith(".zip"): ## find all zips in temp
            with zipfile.ZipFile(os.path.join(loc, dir), "r") as zip_file:
                zip_file.extractall("temp")
def read_kaggle_data(loc : str) -> dict:
    data = dict()
    for dir in listdir(loc): # I do this with consideration to multiple csv files in one zip
        if dir.endswith(".csv"): ## All .csv to memory
            data[dir.removesuffix(".csv")] = pd.read_csv(os.path.join(loc, dir))
            
    return data
## Test
if __name__ == "__main__":
    ## create a decorator
    ## create temp...
    loc = os.path.join(getcwd(), "temp") 
    pull_kaggle_data("pavansubhasht/ibm-hr-analytics-attrition-dataset")
    unzip_kaggle_data(loc) 
    data = read_kaggle_data(loc)
  
    ##send to postgres
    
    ##close connection, and delete temp
                
    print("Debug!")     
    
    ## delete temp, use it as a decorator...