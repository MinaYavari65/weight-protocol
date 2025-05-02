import requests
import json

try:
    data = {
    'O2': {
        'masters':{'O3':'192.168.0.1'}, 'slaves':{'O1':'192.168.0.3'}, 'components':{'C1': (0.5, 0.4, 9.8), 'C2': (0.5, 0.4, 9.8), 'C3': (0.5, 0.4, 9.8)}, 'mapping':{'C1':'O1', 'C2':'O2', 'C3':'O3'}, 'port':8081
        },
    'O4': {
        'masters':{'O8':'192.168.0.4'}, 'slaves':{'O3':'192.168.0.5', 'O5':'192.168.0.6'}, 'components':{'C4': (0.5, 0.4, 9.8), 'C5': (0.5, 0.4, 9.8)}
        },
    'O7': {
        'masters':{'O5':'192.168.0.7'}, 'slaves':{}, 'components':{'C6': (0.5, 0.4, 9.8)}
        }
    }
    response = requests.post('http://127.0.0.1:8080', json=data)
    
    if response.status_code == 200:
        print(response.text)
    else:
        print(f"failed with code {response.status_code}")   
except response.exception.requestException as e:
    print(f"An error occured: {e}")  

    


print(json.dumps(data))