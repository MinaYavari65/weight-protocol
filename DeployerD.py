import random
import requests

class Host:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

class Component:
    def __init__(self, id, featureTuple):
        self.id = id    
        self.featureTuple = featureTuple # Preferences for n non-functional requirements

    def __str__(self):
        return f"Component {self.id}"

class JointSet:
    def __init__(self, jointComponents, id):
        self.id = id
        self.jointComponents = jointComponents    
    def updateDynamicMap(self, dynamic):
        for component in self.jointComponents: dynamic[component.id] = self.id
        return 
    def getComponentMap(self):
        map = {}
        for component in self.jointComponents: 
            map[component.id] = component.featureTuple            
        return map
    def __str__(self):
        return f"JointSet {self.id}: {self.jointComponents}"

class ArchitectureGenerator:
    def __init__(self): 
        self.components = {}
        self.jointSets = {}
        self.mu = {}

    def addComponent(self, component):
        self.components[component.id] = component        
    
    def addJointSet(self, jointSet):
        self.jointSets[jointSet.id] = jointSet        
    
    def addMappingToMu(self, componentId, jointSetId):
        self.mu[componentId] = jointSetId

class HierarchicalControl:
    def __init__(self, architectureGenerator, dynamic): 
        self.architectureGenerator = architectureGenerator
        self.dynamic = dynamic
        self.masters = self.createMasters()
        self.slaves = self.createSlaves()

    def createMasters(self):
        masters = {}
        for jointSetId, value in self.architectureGenerator.jointSets.items(): 
            m = set()        
            for componentId, jointSetId2 in self.architectureGenerator.mu.items():
                if(jointSetId == jointSetId2): m.add(self.dynamic[componentId])            
            masters[jointSetId] = m
        return masters

    def createSlaves(self):
        slaves = {}
        for jointSetId, value in self.architectureGenerator.jointSets.items():  
            s = []    
            for jointSetId2, mastersL in self.masters.items():        
                if jointSetId in mastersL: s.append(jointSetId2)
            slaves[jointSetId] = s
        return slaves

class Deployer:
    def __init__(self, hierarchicalControl, controlManagers): 
        self.hierarchicalControl = hierarchicalControl
        self.controlManagers = controlManagers
        self.allocation = {}
        self.allocationIP = {}
        self.controlIPs = {}
        self.controlPorts = {}
        for manager in controlManagers: self.allocationIP[manager.ip + ":" + str(manager.port)] = []

    def allocate(self):
        for jointSetId, jointSet in self.hierarchicalControl.architectureGenerator.jointSets.items():        
            random_index = random.randint(0, len(self.controlManagers) - 1)                            
            address = self.controlManagers[random_index].ip + ":" + str(self.controlManagers[random_index].port)
            self.allocation[jointSetId] = address
            self.allocationIP[address].append(jointSetId)
            self.controlIPs[jointSetId] = self.controlManagers[random_index].ip
            self.controlPorts[jointSetId] = self.controlManagers[random_index].port+len(self.allocationIP[address])

    def deploy(self):
        for manager in self.controlManagers:
            data = {}                                    
            for jointSetId in self.allocationIP[manager.ip + ":" + str(manager.port)]:
                data[jointSetId] = {}

                data[jointSetId]['masters'] = {}                
                for master in self.hierarchicalControl.masters[jointSetId]:                    
                    data[jointSetId]['masters'][master] = self.controlIPs[master] + ":" + str(self.controlPorts[master])
                data[jointSetId]['slaves'] = {}
                for slave in self.hierarchicalControl.slaves[jointSetId]:
                    data[jointSetId]['slaves'][slave] = self.controlIPs[slave] + ":" + str(self.controlPorts[slave])
                data[jointSetId]['components'] = self.hierarchicalControl.architectureGenerator.jointSets[jointSetId].getComponentMap()
                data[jointSetId]['mu'] = self.hierarchicalControl.architectureGenerator.mu                                           
                data[jointSetId]['port'] = self.controlPorts[jointSetId]
            try:            
                response = requests.post(manager.ip + ":" + str(manager.port), json=data)            
                if response.status_code == 200:
                    print(response.text)
                else:
                    print(f"failed with code {response.status_code}")   
            except response.exception.requestException as e:
                print(f"An error occured: {e}")    
            
dynamic = {}

# STAGE 1: Define software components 
c1 = Component("C1", (0.5,0.7))
c2 = Component("C2", (0.3,0.2))
c3 = Component("C3", (0.6, 0.3))
c4 = Component("C4", (0.9, 0.9))
c5 = Component("C5", (0.3, 0.2))
c6 = Component("C6", (0.43, 0.56))
c7 = Component("C7", (0.3, 0.4))
c8 = Component("C8", (0.3,0.3))
c9 = Component("C9", (0.9,0.3))
c10 = Component("C10", (0.8, 0.2))
c11 = Component("C11", (0.7, 0.3))
c12 = Component("C12", (0.2, 0.5))
c13 = Component("C13", (0.5, 0.4))

# STAGE 2: Group software components into joint sets
a1 = JointSet([c1], "O1"); a1.updateDynamicMap(dynamic)
a2 = JointSet([c2,c3], "O2"); a2.updateDynamicMap(dynamic)
a3 = JointSet([c4,c5, c6], "O3"); a3.updateDynamicMap(dynamic)
a4 = JointSet([c7,c8], "O4"); a4.updateDynamicMap(dynamic)
a5 = JointSet([c9, c10, c11, c12], "O5"); a5.updateDynamicMap(dynamic)
a6 = JointSet([c13], "O6"); a6.updateDynamicMap(dynamic)

# STAGE 3: Create software architecture generator
generator = ArchitectureGenerator()
generator.addComponent(c1)
generator.addComponent(c2)
generator.addComponent(c3)
generator.addComponent(c4)
generator.addComponent(c5)
generator.addComponent(c6)
generator.addComponent(c7)
generator.addComponent(c8)
generator.addComponent(c9)
generator.addComponent(c10)
generator.addComponent(c11)
generator.addComponent(c12)
generator.addComponent(c13)
generator.addJointSet(a1)
generator.addJointSet(a2)
generator.addJointSet(a3)
generator.addJointSet(a4)
generator.addJointSet(a5)
generator.addJointSet(a6)

# STAGE 4: Define mappings from components to joint sets (\mu)
generator.addMappingToMu("C1", "O2"); 
generator.addMappingToMu("C2", "O3"); 
generator.addMappingToMu("C3", "O3"); 
generator.addMappingToMu("C4", "O6"); 
generator.addMappingToMu("C5", "O4"); 
generator.addMappingToMu("C6", "O5"); 
generator.addMappingToMu("C7", "O5"); 
generator.addMappingToMu("C8", "O5"); 
generator.addMappingToMu("C9", "O6"); 
generator.addMappingToMu("C10", "O6"); 
generator.addMappingToMu("C11", "O6"); 
generator.addMappingToMu("C12", "O6"); 
generator.addMappingToMu("C13", ""); 

# STAGE 5: Use the generator to construct the structure of control
controlStructure = HierarchicalControl(generator, dynamic)
#print(controlStructure.masters)       
#print(controlStructure.slaves)       

# STAGE 6: Allocate each joint set to a different IP, create a control for it and send it for remote deployment
host1 = Host('http://127.0.0.1', 8080)
host2 = Host('http://127.0.0.1', 8090)
deployer = Deployer(controlStructure, [host1])
deployer.allocate()
deployer.deploy()