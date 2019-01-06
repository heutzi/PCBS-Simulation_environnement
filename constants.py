TICK = 10
PX_SIZE = 5

#Colors
COL_DEFAULT = (192,253,118)

#Plant Objects - key: name, value = (color, size, reprodSpeed)
PLANT_CARACT ={"SMALL_TREE": ((153,102,0), 1, 0.003, True)}
#{"LARGE_TREE": ((128,0,0), 3, 0.001, False),\
#"MED_TREE": ((153,51,0), 2, 0.002, False),\
#"SMALL_TREE": ((153,102,0), 1, 0.003, True)}

#Plant Objects Initialisation - initial density
PLANT_INIT =\
{"LARGE_TREE": 0.01,\
"MED_TREE": 0.02,\
"SMALL_TREE": 0.04}

#Agent Object (color, reprod-speed, starv-speed)
#Agent Glob (Agent, maxDens, minDens, prays
AGENT_CARACT =\
{"HERBIVOROUS": (((0,165,255), 15, 40), 0.20, 0.10, {"SMALL_TREE"}),\
"CARNIVOROUS": (((234,0,42), 15, 40), 0.10, 0.05, {"HERBIVOROUS"})}

#Agent Objects Initialisation - initial TREE_DENSITY
AGENT_INIT =\
{"HERBIVOROUS": 0.002,\
"CARNIVOROUS": 0.001}
