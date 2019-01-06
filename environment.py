from abc import ABC, abstractmethod
import random
import copy

class EnvObjectGlobal(ABC):
    def __init__(self, name, EnvObject):
        super().__init__()
        self.name = name #id for identification
        self.size = 1
        self.dens_max = 100    #maximal density
        self.dens_min = 0    #minimal density
        self.isPassable = True
        self.isOpaq = True

        #default environment object for initialisation
        self.default = EnvObject
        self.default.globRef = self

    def isAssignable(self, environment, x, y):
        """return True if an object fits at position (x,y)"""
        res = True
        H = environment.height
        W = environment.width
        for i in range(x, x+self.size):
            for j in range(y, y+self.size):
                # An object can be assigned at position p = (x,y) in 2 cases:
                #1) the object is passable and there is no impassable object at p,
                #2) there is no object at p.
                assignXY = (environment.isPassableXY(i%H, j%W) and self.isPassable) or not environment.value[i%H][j%W]
                res = res and assignXY
            if not res:
                break
        return res

    def instantiate(self):
        return copy.copy(self.default)

    def initEnv(self, environment, initDens):
        H = environment.height
        W = environment.width
        environment.objGlob[self.name] = self
        maxObj = (initDens*H*W)//1
        environment.objCounter[self.name] = 0
        oCount = 0
        while oCount < maxObj:
            x = random.randint(0, H-1)
            y = random.randint(0, W-1)
            o = environment.create(self.name, x, y)
            if o:
                oCount += 1

            
class EnvObject(ABC):
    def __init__(self, pos_x, pos_y, name, color):
        super().__init__()
        self.name = name #id for identification
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.color = color
        
        self.globRef = None #EnvObjectGlobal, grouping attributes for all objects sharing a same name

    def __repr__(self):
        return "Ag"+str(self.pos_x)+"-"+str(self.pos_y)

    def __str__(self):
        return "Ag"+str(self.pos_x)+"-"+str(self.pos_y)

    def getSize(self):
        return self.globRef.size

    def destruct(self, environment):
        if environment.objCounter[self.name] > environment.populationMin(self.name):
            for i in range(self.pos_x, self.pos_x+self.getSize()):
                for j in range(self.pos_y, self.pos_y+self.getSize()):
                    environment.value[i%environment.height][j%environment.width].remove(self)
            environment.objCounter[self.name] -= 1
            environment.objUpdate.remove(self)

    @abstractmethod
    def reproduce(self, environment):
        pass

    @abstractmethod
    def iterate(self, environment):
        reproduce(self, environment)

class Environment:
    """Matrix that holds the color values for the screen - includes functions to integrate the environment objects."""

    def __init__(self, height, width, bckGrndColor):
        self.height = height
        self.width = width
        self.bckGrndColor = bckGrndColor

        self.objGlob = {} #dictionnary recording the global properties for a specific type of object
        self.objCounter = {} #dictionnary recording the number of individuals per type of object
        self.objUpdate = set() #set of objects for update
        self.value = [] #matrix recording the objects at each position
        for i in range(height):
            self.value.append([set() for j in range(width)])

    def create(self, objName, x, y):
        r = None
        try:
            oGlob = self.objGlob[objName]
            if oGlob.isAssignable(self, x, y):
                r = oGlob.instantiate()
                r.pos_x = x
                r.pos_y = y
                for i in range(x, x+oGlob.size):
                    for j in range(y, y+oGlob.size):
                        self.value[i%self.height][j%self.width].add(r)
                self.objUpdate.add(r)
                self.objCounter[oGlob.name] += 1
        except KeyError:
            print("Object name unreferenced in environment")
        return r
            

    def populationMax(self, objName):
        try:
            r = self.width*self.height*self.objGlob[objName].dens_max
        except KeyError:
            print("Object name unreferenced in environment")
        return r

    def populationMin(self, objName):
        try:
            r = self.width*self.height*self.objGlob[objName].dens_min
        except KeyError:
            print("Object name unreferenced in environment")
        return r

    def getAnyOpaq(self, x, y):
        """return any object that is visible at position (x, y)"""
        r = None
        for o in self.value[x][y]:
            if o.globRef.isOpaq:
                r = o
                break
        return r

    def isPassableXY(self, x, y):
        """return True if no object is impassable at position (x, y)"""
        res = True
        for o in self.value[x][y]:
            if not o.globRef.isPassable:
                res = False
                break
        return res


    def getColorMatrix(self):
        colMat = []
        for x in range(self.height):
            l = []
            for y in range(self.width):
                if self.value[x][y]:
                    l.append(list(self.value[x][y])[0].color)
                else:
                    l.append(self.bckGrndColor)
            colMat.append(l)
        return colMat

    def iterate(self):
        O = list(self.objUpdate)
        random.shuffle(O)
        for o in O:
            try:
                o.iterate(self)
            except KeyError:
                pass
