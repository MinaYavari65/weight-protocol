from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler, HTTPServer
import json
import threading
import time
import requests
import random
from datetime import datetime

class Component:
    def __init__(self, name, featureTuple):
        self.name = name
        self.featureTuple = featureTuple
        self.weight = 0.0

class Control:
    def __init__(self, id, masters, slaves, ip, port, components, tupleSize, mu):
        self.id = id
        self.masters = masters # Example {'O3': '192.168.0.1',...}
        self.slaves = slaves # Example {'O1': '192.168.0.3',...}
        self.ip = ip
        self.port = port
        self.components = components
        self.tupleSize = tupleSize
        self.mu = mu # This is the \mu mapping from SAG (components to joint sets)
    def isInitiator(self):        
        return not bool(self.slaves)
    def isEnder(self):
        return not bool(self.masters)
    def __str__(self):
        return f"{self.ip}:{self.port}"

def run_control_server(id, port, isInitiator, isEnder, masters, slaves, tupleSize, components, mu):

    class ControlServer(BaseHTTPRequestHandler):
        count_slaves = 0
        def do_POST(self): 
            # Deserialise JSON message from deployer
            content_len = int(self.headers.get('content-length', 0))
            post_body = self.rfile.read(content_len)
            post_body_str = post_body.decode('utf-8')
            data = json.loads(post_body_str)   

            # Aggregate weights from slave            
            slaveArchWeight[data['slaveID']] = (data['slaveArchitecture'], data['slaveWeight'], data['initiatorTimestamp'])            
                    
            # Send a response back to the client
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

            # Synchronises all slaves before deciding the optimal architecture
            ControlServer.count_slaves += 1                  
            
            # Choose the optimal architecture only if received message from all slaves            
            if ControlServer.count_slaves == len(slaves):
                optimalArchitectureWeight = chooseOptimalArchitecture(data['initiatorTimestamp'])
                print(f"{id}-->{optimalArchitectureWeight}")                
                if not(isEnder): 
                    sendToAllMasters(optimalArchitectureWeight[0], optimalArchitectureWeight[1], data['initiatorTimestamp'])
                else:
                    print(f"OPTIMAL ARCHITECTURE: {optimalArchitectureWeight[0]}")
                    print(f"WEIGHT: {optimalArchitectureWeight[1]}")
                    print(f"TIMESTAMP: {data['initiatorTimestamp']}")
                ControlServer.count_slaves = 0
    
    def updateWeights():
        while True:            
            time.sleep(2)
            environmentTuple = tuple(random.uniform(0.0, 1.0) for _ in range(tupleSize))
            
            # DOT Product (most optimisation problems are based on this)
            for component in components:
                sum = 0.0
                for i in range(0, tupleSize):
                    sum += environmentTuple[i]*component.featureTuple[i]
                component.weight = sum
                componentWeightsMap[component.name].append((component.weight, datetime.timestamp(datetime.now())))
                #print (f"{id}-->{component.name}: {componentWeightsMap[component.name]}")                        

    def initiateAggregation():
        while True:            
            time.sleep(10)
            print(f"Control {id} has initiated aggregation")
            timestamp = datetime.timestamp(datetime.now())

            # Initiator just chooses component with minimal weight
            optimalArchitectureList = []
            optimalWeight = float('inf')            
            for componentName, componentWeights in componentWeightsMap.items():                
                if componentWeights[-1][0] <= optimalWeight: # compare the most recent weight for each component
                    optimalWeight = componentWeights[-1][0]
                    optimalArchitectureList = [componentName]                    
                        
            sendToAllMasters(optimalArchitectureList, optimalWeight, timestamp)                          

    # Send the following to each master 
    # (slaveID, architecture - chosen component, chosen component weight, timestamp)
    def sendToAllMasters(optimalArchitectureList, optimalWeight, initiatorTimestamp):
        data = {}
        data['slaveID'] = id
        data['slaveArchitecture'] = optimalArchitectureList
        data['slaveWeight'] = optimalWeight
        data['initiatorTimestamp'] = initiatorTimestamp

        for masterID, masterIP in masters.items():            
            try:            
                response = requests.post(masterIP, json=data)            
                if response.status_code == 200:
                    print(response.text)
                else:
                    print(f"failed with code {response.status_code}")   
            except response.exception.requestException as e:
                print(f"An error occured: {e}") 

    def chooseOptimalArchitecture(initiatorTimestamp): # Optimal means minimum                
        optimalComponent = ""
        optimalWeight = float('inf')
        for componentName, componentWeights in componentWeightsMap.items():
            
            # For each component, choose the weight generated at 'the time' of the initiator
            chosenTimestamp = float('inf')
            for weightTimestamp in componentWeights:                
                delta = abs(weightTimestamp[1] - initiatorTimestamp)
                if delta <= chosenTimestamp:
                    chosenTimestamp = delta
                    chosenWeight = weightTimestamp[0]                

            # Next, choose the best architecture  
            aggregatedWeight = slaveArchWeight[mu[componentName]][1] + chosenWeight 

            if aggregatedWeight <= optimalWeight:
                optimalWeight = aggregatedWeight
                optimalComponent = componentName
                
        return (slaveArchWeight[mu[optimalComponent]][0] + [optimalComponent], optimalWeight)    
    
    # Each mapping has the form componentName-->[(weight1, timestamp1), (weight2, timestamp2), ...] 
    componentWeightsMap = {}   
    for component in components: componentWeightsMap[component.name] = []
    # Each mapping has the form SlaveID-->(architectureList, weight, initiatorTimestamp)
    slaveArchWeight = {} 

    updateThread = threading.Thread(target=updateWeights)
    updateThread.start()
    if isInitiator:
        aggregationThread = threading.Thread(target=initiateAggregation)
        aggregationThread.start()

    server_address = ('', port)
    new_server = ThreadingHTTPServer(server_address, ControlServer)
    print(f"Control {id} started on port {port}")
    new_server.serve_forever()

class ControlManager(BaseHTTPRequestHandler):   
    def do_POST(self):
        # Deserialise JSON message from deployer
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)
        post_body_str = post_body.decode('utf-8')
        data = json.loads(post_body_str)

        # Start control server
        for key, value in data.items():                               
            components = []
            tupleSize = 0
            for componentID, featureTuple in value['components'].items(): 
                components.append(Component(componentID, featureTuple))
                tupleSize = len(featureTuple)

            control = Control(key, value['masters'], value['slaves'], self.server.server_address[0], value['port'], components, tupleSize, value['mu'])              
            t2 = threading.Thread(target=run_control_server, args=(control.id, control.port, control.isInitiator(), control.isEnder(), control.masters, control.slaves, control.tupleSize, control.components, control.mu))
            t2.daemon = True  # daemon thread so it won't block program exit
            t2.start()                    
                
        # Send a response back to the client
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

def run_manager_server(ip, port):
    server_address = (ip, port)
    httpd = HTTPServer(server_address, ControlManager)
    print('Control Manager Server listening on ' + ip + ":" + str(port))
    httpd.serve_forever()

if __name__ == "__main__":
    ip = '127.0.0.1'
    port = 8080
    #ControlManager.next_port = port
    run_manager_server(ip, port)