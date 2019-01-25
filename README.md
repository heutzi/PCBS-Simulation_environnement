# PCBS-Simulation_environnement
Python project meant to provide a simulation of a natural environment. This project was written as a requirement for the course Programming for Cognitive and Brain Sciences (PCBS) taught by Mr. Pallier at the ENS. A good care was taken toward the reusability of the class framework, developed to structure the program.

## Introduction

As writen, in the presentation note, This project was aiming at providing a framework for an environment simulation. We provided a good example of use, through the design of two categories of environmental objects, agents and plant, interacting together.
The present document will analyze in a first part, the structure of the environment class, and the second and third will describe respectively plants and agents sub-classes.

## The environment framework

The corresponding python file is available at this link:
[environment.py](environment.py).

### The environment class

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

### The EnvObject class

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

The Environment class is the one to which belongs the objects that populates the environment. Each instance has a position, recorded by the attributes x and y, that match the actual position of the object in the `Environment` object that was instanciated.
It also has a color, for representation and a name, commmon to all objects belonging to the same 'category', or `EnvObjectGlobal` instance.
Each `EnvObject` is linked to its global reference through the attribute globRef. No object of this kind, except the default object for `EnvObjectGlobal`, should be instantiated in an other way than through the `Environment`create function.
The `EnvObject` is an abstract class, meaning it can't be directly instantiated. One must design its own subclass. Particularly two methods needs to be implemented: the `iterate` method that gives the object a behavior (it is strongly recommended for it to integrate the `reproduce` method), and the `reproduce`method (that may actually not be used depending on how iterate was implemented).
Finally, the `tick` method expresses at which pace an object iterates.


### The EnvObjectGlobal class
The `EnvObject` works in pair with a `EnvEnvironmentGlobal` object:

```markdown
class EnvObjectGlobal(ABC):
    def __init__(self, name, EnvObject):
        super().__init__()
        self.name = name #id for identification
        self.size = 1
        self.dens_max = 100    #maximal density
        self.dens_min = 0    #minimal density
        self.speed = 1 #speed at which an object behave
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
        return copy.deepcopy(self.default)

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
```
The `EnvObjectGlobal` records properties common to a 'species'. Notably, the name, size, maximal and minimal density of individuals, and if passable or opaque.
Every `EnvObject`, as said previously, is done through the environment that calls the `instantiate` method of the corresponding `EnvObjectGlobal`.
Finally, `EnvObjectGlobal` are equiped to randomly populate an environment with the function `initEnv` that takes for argument an initial density `initDens`.
Note that EnvObjectGlobal is also an abstract object. It is recommended to implement your own sub-class in parallel to the implementation of the `EnvObject`. An example follows.

## Example: Plant objects

The corresponding python file is available at this link:
[plants.py](plants.py).

The plant objects are meant to simulate plants, that randomly grow in the environment and may catch fire.
Follows the implementation of the respective `EnvObjectGlobal` and `EnvObject class`.
```markdown
class PlantGlobal(EnvObjectGlobal):
    def __init__(self, name, plant, size, reprodRate, isPassable):
        super().__init__(name, plant)
        self.size = size
        self.reprodRate = reprodRate # chance for a plant to duplicate itself
        self.isPassable = isPassable

class Plant(EnvObject):
    """define a tree with 2 positionnal arguments, a size and a color"""

    def __init__(self, pos_x, pos_y, name, color):
        super().__init__(pos_x, pos_y, name, color)

    def __repr__(self):
        return "Pl"+str(self.pos_x)+"-"+str(self.pos_y)

    def __str__(self):
        return "Pl"+str(self.pos_x)+"-"+str(self.pos_y)

    def burn(self, environment):
        if self.color == FIRE[0]:
            self.color = FIRE[1]
        elif self.color == FIRE[1]:
            self.color = FIRE[2]
        elif self.color == FIRE[2]:
            self.color = FIRE[3]
        #propagate fire to all sides and diagonals
        elif self.color == FIRE[4]:
            for i in range(self.pos_x - 1, self.pos_x+self.getSize()+1):
                for j in (self.pos_y - 1, self.pos_y+self.getSize()+1):
                    for o in environment.value[i%environment.height][j%environment.width]:
                        if type(o) == Plant and o.color not in [FIRE[x] for x in FIRE.keys()]:
                            o.color = FIRE[4]
            for j in range(self.pos_y - 1, self.pos_y+self.getSize()+1):
                for i in (self.pos_x - 1, self.pos_x+self.getSize()+ 1):
                    for o in environment.value[i%environment.height][j%environment.width]:
                        if type(o) == Plant and o.color not in [FIRE[x] for x in FIRE.keys()]:
                            o.color = FIRE[4]
            self.color = FIRE[0]
        elif self.color == FIRE[3]:
            self.destruct(environment)
        elif BURN_RATE > random.uniform(0, 1):
            self.color = FIRE[4]

    def reproduce(self, environment):
        if self.globRef.reprodRate > random.uniform(0, 1):
            p = None
            while not p:
                x = random.randint(0, environment.height-1)
                y = random.randint(0, environment.width-1)
                p = environment.create(self.name, x, y)

    def iterate(self, environment):
        self.burn(environment)
        self.reproduce(environment)
```

The plant implementation of `EnvObjectGlobal`, `PlantGlobal` has one original attribute, `reprodRate` that will play a role in the speed at which plant reproduce. Otherwise, plant may vary in size and color.
This follows an old implementation of "speed" where it was linked to a probability of reproducing, rather than to a speed constant. It has the advantage of plants not duplicating all at the same time.
The plant implementation of `EnvObject`, `Plant`, in addition to randomly duplicate as a way of reproducing, may catch fire. the probability of catching fire is a constant to all plants : `BURN_RATE`. Fire propagates from plant to plant in every direction. Fire turns plant to ashes by changing their color to red first, then from black to white in four stages.

## Example: Agent objects

The corresponding python file is available at this link:
[agents.py](agents.py).

The agent objects are meant to simulate agents, that move, eat and reproduce in the environment.
Follows the implementation of the respective `EnvObjectGlobal` and `EnvObject class`.
```markdown
class AgentGlobal(EnvObjectGlobal):
    def __init__(self, name, agent, dens_min, dens_max, speed, diet):
        super().__init__(name, agent)
        self.speed = speed
        self.dens_max = dens_max
        self.dens_min = dens_min
        self.diet = diet
        

class Agent(EnvObject):
    """define an agent with 2 positionnal arguments and a color"""

    def __init__(self, pos_x, pos_y, name, color, rprd, starv):
        super().__init__(pos_x, pos_y, name, color)
        self.rprd = rprd
        self.starv = starv
        self.behav = {} #interpretation function associated to perceived object

    def __repr__(self):
        return "Ag"+str(self.pos_x)+"-"+str(self.pos_y)

    def __str__(self):
        return "Ag"+str(self.pos_x)+"-"+str(self.pos_y)

    def iterate(self, environment):
        self.reproduce(environment)
        self.move(environment)
        self.eat(environment)
        self.exhaust(environment)

    
    def reproduce(self, environment):
        if self.rprd <= 0 and environment.objCounter[self.name] < environment.populationMax(self.name):
            newAgent = environment.create(self.name, self.pos_x, self.pos_y)
            if newAgent:
                self.rprd = self.globRef.default.rprd
                newAgent.modifBehav()
        else:
            self.rprd -= 1

    def modifBehav(self):
        try:
            k = random.choice(list(self.behav.keys()))
            if random.random() > 0.5:
                self.behav[k] += 0.1
            else:
                self.behav[k] -= 0.1
        except IndexError:
            #self.behav empty -- happens when an agent has encountered no other object
            pass

    def move(self, environment):
        H = environment.height
        W = environment.width
        
        vis = self.lookAround(environment)
        #rewriting of vision dictionary keys, as absolute coordinates of agent's adjacent positions
        #the vision dictionary has originaly a couple sense (1 or -1) direction (0-x_axis or 1-y_axis) for keys
        #i: sense, j: direction
        vis = {((self.pos_x+(1-j)*i)%H, (self.pos_y+j*i)%W):vis[(i,j)] for (i,j) in vis}
        #rejection of the positions on which stands an impassable object
        vis = {k:vis[k] for k in vis if environment.isPassableXY(*k)}

        try:
            maxi = max([vis[k] for k in vis])
            options = [k for k in vis if vis[k]==maxi]
            newXY = random.choice(options)
            environment.value[self.pos_x][self.pos_y].remove(self)
            environment.value[newXY[0]][newXY[1]].add(self)
            self.pos_x = newXY[0]
            self.pos_y = newXY[1]
        except ValueError:
            #case of an agent surrounded by unpassable objects
            pass

    def distToObj(self, environment, x, y):
        """return the minimal number of movement to reach position (x,y) (Manhattan distance)"""
        distX = abs(self.pos_x-x)
        distY = abs(self.pos_y-y)
        return min(distX, environment.height-distX) + min(distY, environment.width-distY)

    def lookAround(self, environment):
        v = {}
        for i in (1, -1):
            for j in (1, 0):
                k = (i,j)
                v[k] = [self.interpretVis(k,l) for (k,l) in self.lookAt(environment, VISION_LENGTH, NBR_ELEM_VIS, *k)]
                v[k] = sum(v[i,j])
        return v
                

    def lookAt(self, environment, maxL, maxElem, sense, direction):
        """maxL: vision scope, maxElem: maximal number of element taken in account"""

        res = []
        L=0
        
        #queue and lines contain cells of format (X, Y, cursL, cursR)
        #X and Y for position, cursL and cursR to propagate vision from cell
        Queue = []
        Line1 = [(0, 1, -1, 0)]
        Line2 = [(-1, 1, -1, 0), (1, 1, -1, 0)]
        while any((Queue, Line1, Line2)):
            if not Queue:
                if Line1:
                    random.shuffle(Line1)
                    Queue = copy.copy(Line1)
                    Line1 = copy.copy(Line2)
                    Line2 = []
                else:
                    random.shuffle(Line2)
                    Queue = copy.copy(Line2)

            cell = Queue.pop(0)
            X = cell[0]
            Y = cell[1]
            cursL = cell[2]
            cursR = cell[3]

            nextCursL =  -(Y+1) if cursL+1 > 0 else cursL+1
            nextCursR = Y+1 if cursR-1 < 0 else cursR-1

            #default direction is along y axis, x and y are reversed to follow the x axis
            X2 = X if direction else Y*sense
            Y2 = Y*sense if direction else X
            x = (self.pos_x+X2)%environment.height
            y = (self.pos_y+Y2)%environment.width
            
            obj = environment.getAnyOpaq(x, y)
            if obj:
                res.append((obj, self.distToObj(environment, x, y)))
                if len(res)>= maxElem:
                    break

            if L != maxL and not obj:
                if X <= cursL:
                    Line2.append((X-1, Y+1, nextCursL, nextCursR))
                if X >= cursR:
                    Line2.append((X+1, Y+1, nextCursL, nextCursR))
                if X >= cursL and X <= cursR:
                    Line1.append((X, Y+1, nextCursL, nextCursR))
        
        return res

    def interpretVis(self, envObj, dist):
        k = envObj.name
        if k not in self.behav:
            self.behav[k] = 0
        try:
            return self.behav[k]/dist #the further an object, the less important it is
        except ZeroDivisionError:
            print(self, envObj)
            return 0

    def eat(self, environment):
        """eat one object at the same position as itself if it is part of its list of prays"""
        for o in list(environment.value[self.pos_x][self.pos_y]):
            if o.name in self.globRef.diet:
                self.starv = self.globRef.default.starv
                o.destruct(environment)
                break

    def exhaust(self, environment):
        self.starv -= 1
        if self.starv == 0:
            self.destruct(environment)
```
The agent implementation of `EnvObjectGlobal`, `AgentGlobal` has one additional attribute, diet, which lists by their name all the other categories (instances of `EnvObjectGlobal`) that a type of agent can eat.
The agent implementation of `EnvObject`, `Agent`, have three additional attribute `rprd` which is used to express the pace at chich an agent reproduces, `starv`, the speed at which an agent starve if not eating and `behav` which is a dictionnary referencing the behavior to adopt when perceiving various types of objects.

`Agent` while iterating, performs four actions. It reproduces, the way a human cell would do, by duplicating itself at its current position and transmitting its behavioural gene (`behav`). It moves, implying a complex step of looking around, referencing what types of objects are in the near perimeter (the `look_at` method simulate vision, as object seen block further vision), and evaluating which direction to go is the best (contact me by email at jonas.noblet@gmail.com for further details). Then the Agent gets exhausted and, if not dead, eat.

This implementation of agents permits an evolution of their behavior over time, as selection will operate through starvation and predation. However, the simulation is hard to calibrate in order for the population to not end up annihilated by exhaustion in early stages of their evolution. 

## Graphic and environment running functions

### Graphic functions
The corresponding python file is available at this link:
[display_functions.py](display_functions.py).

The graphic functions were developped in order to represent graphicly the matrix contained in an `Environment` object.
```markdown
def DrawMatrix(mat, surface, px):
    """print the matrix elements to screen given a pixel size"""
    H, W = len(mat[0]), len(mat)
    #display the matrix
    for y in range(W):
        for x in range(H):
            #surface.set_at((x, y), mat[y][x])
            pygame.draw.rect(surface, mat[y][x], (x*px, y*px, px, px))

```

To summarize the functionning `DrawMatrix`, it draws a square of the corresponding color, for each position (x,y) in the matrix `mat`. The scale of the square is determined by `px`.

### Environment running function
The corresponding python file is available at this link:
[display_functions.py](display_functions.py).

The following function aims at instantiating an `Environment` object, populate it with various agents and plants and running the simulation.
```markdown
def MyMain(H, W):
    random.seed(time.time())

    environment = Environment(H, W, C.COL_DEFAULT)
    for AgName in list(C.AGENT_CARACT.keys()):
        AgCar = C.AGENT_CARACT[AgName]
        A = AgentGlobal(AgName, Agent(0,0,AgName,*AgCar[0]), *AgCar[1:])
        A.initEnv(environment, C.AGENT_INIT[AgName])

    for PlName in list(C.PLANT_CARACT.keys()):
        PlCar = C.PLANT_CARACT[PlName]
        P = PlantGlobal(PlName, Plant(0,0,PlName,PlCar[0]), *PlCar[1:])
        P.initEnv(environment, C.PLANT_INIT[PlName])

    pygame.init()
    screen = pygame.display.set_mode((C.PX_SIZE*W, C.PX_SIZE*H), pygame.DOUBLEBUF)
    screen.fill((0, 0, 0))

    disp.DrawMatrix(environment.getColorMatrix(), screen, C.PX_SIZE)

    # wait till the window is closed
    clock = pygame.time.Clock()
    done = False
    ticker = 0 #used to express time passing in the environment
    while not done:
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        done = True
        environment.tick(ticker)
        ticker += 1
        disp.DrawMatrix(environment.getColorMatrix(), screen, C.PX_SIZE)
        # display the backbuffer
        pygame.display.flip()
        clock.tick(C.TICK)
```
Note that the populating of the environment is separated from its ititialisation, which allows for all sorts of combination with various types of objects.
Here we used some data recorded in a file C to populate the environment and set the "pixel size" of the graphic window.
Follow the link below for the details:
[constants.py](constants.py)

## Conclusion

The `Environment` class was designed as a flexible tool that allows multiple usage.
In this project we developped two examples of use, in order to simulate plants and agents in a natural environment.
The simulation was giving encouraging results but displayed a very high sensitivity to various parameters. Even though it was expected, this made testing tedious.
Moreover, our program lacked tools that could assess any result it could provide.

Previous programming classes related to the course: *Introduction to natural language processing in Python*, *Introduction to object oriented design and programming*.
