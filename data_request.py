import os
from os import listdir,getcwd
import zipfile
import pandas as pd
import kaggle


## Test
if __name__ == "__main__":
    ## create a decorator
    ## create temp...
    kaggle.api.authenticate()
    kaggle.api.dataset_download_files("pavansubhasht/ibm-hr-analytics-attrition-dataset", path = "temp")
    ## This code finds all zips and decompresses them to the local temp folder.
    ## find all zips in temp
    data = dict()
    
    loc = os.path.join(getcwd(), "temp") 
    for dir in listdir(loc): ## This is a placeholder function if more than one dataset should be used.
        if dir.endswith(".zip"):
            with zipfile.ZipFile(os.path.join(loc, dir), "r") as zip_file:
                zip_file.extractall("temp")
                
                
    ## All .csv to memory
    for dir in listdir(loc): # I do this with consideration to multiple csv files in one zip
        if dir.endswith(".csv"):
            data[dir.removesuffix(".csv")] = pd.read_csv(os.path.join(loc, dir))
            
    ##send to postgres
    
    ##close connection, and delete temp
                
    print("Debug!")     
    
    ## delete temp, use it as a decorator...