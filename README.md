# PCBS-Simulation_environnement
Python project meant to provide a simulation of a natural environment. This project was written as a requirement for the course Programming for Cognitive and Brain Sciences (PCBS) taught by Mr. Pallier at the ENS. A good care was taken toward the reusability of the class framework, developed to structure the program.

## Introduction

As writen, in the presentation note, This project was aiming at providing a framework for an environment simulation. We provided a good example of use, through the design of two categories of environmental objects, agents and plant, interacting together.
The present document will analyze in a first part, the structure of the environment class, and the second and third will describe respectively plants and agents sub-classes.

### The environment class

You can download the python file relative to this section at this link:
[environment.py](environment.py)

The `Environment` class is as follows:

```markdown
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

    def tick(self, tick):
        O = list(self.objUpdate)
        random.shuffle(O)
        for o in O:
            try:
                o.tick(self, tick)
            except KeyError:
                pass

```
The `Environment` class is instiated with a height and width, that defines its size, and a background color bckGrndColor.
It mains attribute are a grid, `self.value`, (of type list\*list\*set) that contains `EnvObject` at various positions, and a set listing those recoded objects, `self.objUpdate`.The `EnvObject` class will be later described.
`Environment` also holds the count of the number of object it contains per instances of `EnvObjectGlobal`, class that will be described later as well.

The main purpose of the environment is to be iterated, in order for it to simulate an evolution of a system.
This is the role of the method `tick` that, given a time counter, will iterate the objects contained within the environment object. The purpose of the attribute `self.objUpdate` was to accelerate this procedure by avoiding going through the height\*width cells of `self.value`, that might be empty.

Another import method is `getColorMatrix` that returns a color (RVB format) grid of size height\*width, representing for each pocition either the background color when no object, or the color of one of the object if any. This method allows later for graphic representation.

`Environment` object are also respondible for `EnvObject` creation within itself, through the method `create`. This is mainly to avoid conflict with objects that may not allow for superposition, having attribute `isPassable == False`.

Finally, `Environment` are capable of returning various computations involving some of its feature, such as `populationMax` that returns the absolute `populationMax` given a name (corresponding to EnvAgentGlobal instance), or `getAnyOpaq`, that returns any object at position (x,y) having attribute `isOpaq == True`.

As described previously, the Environment class works in combination with two other classes, that works in pair.
The first one is the `EnvObject` class:

```markdown
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
        pass
    
    def tick(self, environment, tick):
        if tick%self.globRef.speed == 0:
            self.iterate(environment)
```



### Support or Contact

Having trouble with Pages? Check out our [documentation](https://help.github.com/categories/github-pages-basics/) or [contact support](https://github.com/contact) and we’ll help you sort it out.
