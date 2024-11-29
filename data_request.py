import os
from os import listdir,getcwd
import zipfile

import kaggle



## Test
if __name__ == "__main__":
    ## create a decorator
    ## create temp...
    kaggle.api.authenticate()
    kaggle.api.dataset_download_files("pavansubhasht/ibm-hr-analytics-attrition-dataset", path = "temp")
    ## This code finds all zips and decompresses them to the local temp folder.
    ## find all zips in temp
    loc = os.path.join(getcwd(), "temp")
    for dir in listdir(loc):
        if dir.endswith(".zip"):
            with zipfile.ZipFile(os.path.join(loc, dir), "r") as zip_file:
                zip_file.extractall("temp")
                
    print("Debug!")     
    
    ## delete temp, use it as a decorator...