import requests


if __name__ == "__main__":
    url = "http://localhost:8010"
    
    table_name = "wa_fn_usec__hr_employee_attrition"
    response = requests.post(url=url + f"/explain/{table_name}")
    print(response)
    

