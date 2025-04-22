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

def createMasters(generator, dynamic):
    masters = {}
    for jointSetId, value in generator.jointSets.items(): 
        m = set([])        
        for componentId, jointSetId2 in generator.mapping.items():
            if(jointSetId == jointSetId2): m.add(dynamic[componentId])            
        masters[jointSetId] = m
    return masters

def createSlaves(generator, masters):
    slaves = {}
    for jointSetId, value in generator.jointSets.items():  
        s = []    
        for jointSetId2, mastersL in masters.items():        
            if jointSetId in mastersL: s.append(jointSetId2)
        slaves[jointSetId] = s
    return slaves

dynamic = {}

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

a1 = JointSet([c1], "A1"); a1.updateDynamicMap(dynamic)
a2 = JointSet([c2,c3], "A2"); a2.updateDynamicMap(dynamic)
a3 = JointSet([c4,c5, c6], "A3"); a3.updateDynamicMap(dynamic)
a4 = JointSet([c7,c8], "A4"); a4.updateDynamicMap(dynamic)
a5 = JointSet([c9, c10, c11, c12], "A5"); a5.updateDynamicMap(dynamic)
a6 = JointSet([c13], "A6"); a6.updateDynamicMap(dynamic)

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

masters = createMasters(generator, dynamic)
slaves = createSlaves(generator, dynamic)
print(masters)       
print(slaves)       