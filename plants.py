import random
from environment import EnvObject, EnvObjectGlobal

FIRE = {0:(0,0,0), 1:(75,75,75), 2:(150,150,150), 3:(225,225,225), 4:(255,0,0)}
BURN_RATE = 0.00003

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
