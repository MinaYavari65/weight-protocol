import random
import requests

class Component:
    def __init__(self, id):
        self.id = id    
    def __str__(self):
        return f"Component {self.id}"

class JointSet:
    def __init__(self, jointComponents, id):
        self.id = id
        self.jointComponents = jointComponents    
    def updateDynamicMap(self, dynamicMap):
        for component in self.jointComponents: dynamicMap[component.id] = self.id
        return 
    def getComponentIDList(self):
        list = []
        for component in self.jointComponents: list.append(component.id)
        return list
    def __str__(self):
        return f"JointSet {self.id}: {self.jointComponents}"

class ArchitectureGenerator:
    def __init__(self): 
        self.components = {}
        self.jointSets = {}
        self.mapping = {}

    def addComponent(self, component):
        self.components[component.id] = component        
    
    def addJointSet(self, jointSet):
        self.jointSets[jointSet.id] = jointSet        
    
    def addMapping(self, componentId, jointSetId):
        self.mapping[componentId] = jointSetId

class HierarchicalControl:
    def __init__(self, architectureGenerator, dynamicTable): 
        self.architectureGenerator = architectureGenerator
        self.dynamicTable = dynamicTable
        self.masters = self.createMasters()
        self.slaves = self.createSlaves()

    def createMasters(self):
        masters = {}
        for jointSetId, value in self.architectureGenerator.jointSets.items(): 
            m = set()        
            for componentId, jointSetId2 in self.architectureGenerator.mapping.items():
                if(jointSetId == jointSetId2): m.add(self.dynamicTable[componentId])            
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
        for manager in controlManagers: self.allocationIP[manager] = []

    def allocate(self):
        for jointSetId, jointSet in self.hierarchicalControl.architectureGenerator.jointSets.items():            
            ip = random.choice(self.controlManagers)
            self.allocation[jointSetId] = ip
            self.allocationIP[ip].append(jointSetId)

    def deploy(self):
        for ip in self.controlManagers:
            data = {}
            targets = self.allocationIP[ip]            
            for jointSetId in targets:
                data[jointSetId] = {}

                data[jointSetId]['masters'] = {}
                for master in self.hierarchicalControl.masters[jointSetId]:
                    data[jointSetId]['masters'][master] = self.allocation[master]
                data[jointSetId]['slaves'] = {}
                for slave in self.hierarchicalControl.slaves[jointSetId]:
                    data[jointSetId]['slaves'][slave] = self.allocation[slave]
                data[jointSetId]['components'] = self.hierarchicalControl.architectureGenerator.jointSets[jointSetId].getComponentIDList()                        
            try:            
                response = requests.post(ip, json=data)            
                if response.status_code == 200:
                    print(response.text)
                else:
                    print(f"failed with code {response.status_code}")   
            except response.exception.requestException as e:
                print(f"An error occured: {e}")    
            
dynamic = {}

# STAGE 1: Define software components 
c1 = Component("C1")
c2 = Component("C2")
c3 = Component("C3")
c4 = Component("C4")
c5 = Component("C5")
c6 = Component("C6")
c7 = Component("C7")
c8 = Component("C8")
c9 = Component("C9")
c10 = Component("C10")
c11 = Component("C11")
c12 = Component("C12")
c13 = Component("C13")

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

# STAGE 4: Define mappings from components to joint sets
generator.addMapping("C1", "A2"); 
generator.addMapping("C2", "A3"); 
generator.addMapping("C3", "A3"); 
generator.addMapping("C4", "A6"); 
generator.addMapping("C5", "A4"); 
generator.addMapping("C6", "A5"); 
generator.addMapping("C7", "A6"); 
generator.addMapping("C8", "A6"); 
generator.addMapping("C9", "A6"); 
generator.addMapping("C10", "A6"); 
generator.addMapping("C11", "A6"); 
generator.addMapping("C12", "A6"); 
generator.addMapping("C13", ""); 

# STAGE 5: Use the generator to construct the structure of control
controlStructure = HierarchicalControl(generator, dynamic)
#print(controlStructure.masters)       
#print(controlStructure.slaves)       

deployer = Deployer(controlStructure, ['http://127.0.0.1:8080', 'http://127.0.0.1:8090'])
deployer.allocate()
deployer.deploy()