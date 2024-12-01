import requests


if __name__ == "__main__":
    url = "http://localhost:8015"
    
    req_data = dict()
    req_data["name"] = "pavansubhasht/ibm-hr-analytics-attrition-dataset"
    response = requests.post(url=url + "/pull", data=req_data)
    print(response)
    