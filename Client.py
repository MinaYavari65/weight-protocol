import requests

try:
    
    data = {'weight': '5'}
    response = requests.post('http://127.0.0.1:8080', json=data)
    if response.status_code == 200:
        print(response.text)
    else:
        print(f"failed with code {response.status_code}")   
except response.exception.requestException as e:
    print(f"An error occured: {e}")  
