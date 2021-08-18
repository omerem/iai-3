ROUND = 7
COLOR = {
    "PURPLE" : '\033[95m',
    "CYAN" : '\033[96m',
    'DARKCYAN' : '\033[36m',
    'BLUE' : '\033[94m',
    'GREEN' : '\033[92m',
    'YELLOW' : '\033[93m',
    'RED' : '\033[91m',
    'BOLD' : '\033[1m',
    'UNDERLINE' : '\033[4m',
    'END' : '\033[0m'
}

THERE_ARE_PEOPLE = True
# Required: ALL_TIMES < 0
ALL_TIMES = -1

def generatorFunction():
    num = 0
    while True:
        yield num
        num+=1

generator = generatorFunction()

VERTICES = next(generator)
EDGES = next(generator)
PATH = next(generator)
MOST_LIKELY_PATH = next(generator)

VERTEX = VERTICES
EDGE = EDGES

RESET_EVIDENCE = next(generator)
ADD_EVIDENCE = next(generator)
PROB_REASONING = next(generator)
QUIT = next(generator)
SHOW_GRAPH = next(generator)
SHOW_BAYES_NET = next(generator)
EVIDENCES = next(generator)
MENU = next(generator)

TEMPORAL_PARENT = next(generator)
VERTEX_1_PARENT = next(generator)
VERTEX_2_PARENT = next(generator)

PROB_OF_VERTEX = next(generator)

PROB_GIVEN_0_VERTICES = next(generator)
PROB_GIVEN_1_VERTEX = next(generator)
PROB_GIVEN_2_VERTICES = next(generator)
PROB_GIVEN_PREV_TIME_IS_TRUE = next(generator)
PROB_GIVEN_PREV_TIME_IS_FALSE = next(generator)

def viewColors():
    for feature in COLOR:
        print(COLOR[feature])
        print(feature)
        print('ABCDEFGHabcdefgh')
        print(COLOR['END'])
