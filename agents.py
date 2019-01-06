import random
import copy
from environment import EnvObject, EnvObjectGlobal

VISION_LENGTH = 6
NBR_ELEM_VIS = 6

class AgentGlobal(EnvObjectGlobal):
    def __init__(self, name, agent, dens_min, dens_max, diet):
        super().__init__(name, agent)
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
