import random
import requests

class Host:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

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
                data[jointSetId]['components'] = self.hierarchicalControl.architectureGenerator.jointSets[jointSetId].getComponentIDList()                                             
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
generator.addMapping("C1", "O2"); 
generator.addMapping("C2", "O3"); 
generator.addMapping("C3", "O3"); 
generator.addMapping("C4", "O6"); 
generator.addMapping("C5", "O4"); 
generator.addMapping("C6", "O5"); 
generator.addMapping("C7", "O6"); 
generator.addMapping("C8", "O6"); 
generator.addMapping("C9", "O6"); 
generator.addMapping("C10", "O6"); 
generator.addMapping("C11", "O6"); 
generator.addMapping("C12", "O6"); 
generator.addMapping("C13", ""); 

# STAGE 5: Use the generator to construct the structure of control
controlStructure = HierarchicalControl(generator, dynamic)
#print(controlStructure.masters)       
#print(controlStructure.slaves)       

# STAGE 6: Allocate each joint set to a different IP, create a control for it and send it for remote deployment
host1 = Host('http://127.0.0.1', 8080)
host2 = Host('http://127.0.0.1', 8090)
deployer = Deployer(controlStructure, [host1, host2])
deployer.allocate()
deployer.deploy()