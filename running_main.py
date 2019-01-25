import pygame
import random
import time
#My modules
from plants import PlantGlobal, Plant
from agents import AgentGlobal, Agent
from environment import Environment
import display_functions as disp
import constants as C


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

MyMain(100, 150)
