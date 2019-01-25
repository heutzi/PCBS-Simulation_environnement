# PCBS-Simulation_environnement
Python project meant to provide a simulation of a natural environment. This project was written as a requirement for the course Programming for Cognitive and Brain Sciences (PCBS) taught by Mr. Pallier at the ENS. A good care was taken toward the reusability of the class framework, developed to structure the program.

## Introduction

As writen, in the presentation note, This project was aiming at providing a framework for an environment simulation. We provided a good example of use, through the design of two categories of environmental objects, agents and plant, interacting together.
The present document will analyze in a first part, the structure of the environment class, and the second and third will describe respectively plants and agents sub-classes.

### The environment class

You can download the python file at this link:
[environment.py](environment.py)

The environment class is as follows:

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

For more details see [GitHub Flavored Markdown](https://guides.github.com/features/mastering-markdown/).



### Support or Contact

Having trouble with Pages? Check out our [documentation](https://help.github.com/categories/github-pages-basics/) or [contact support](https://github.com/contact) and we’ll help you sort it out.
