import HurricaneEnv
import Tests
import _settings
input = input

def _setInputFunction(func):
    global input
    input = func


def runProgram():
    graph_number = int(input("What graph number?\t"))
    env = HurricaneEnv.HurricaneEnv("tests/graph_"+str(graph_number)+".txt")
    env.run_env()


if __name__ == '__main__':
    #TO USE AUTOMATIC FILL USE THIS:

    test_number = 4
    user_input_file = open("tests/user_input_"+str(test_number)+".txt")
    _settings.makeInputAuto(user_input_file)
    _setInputFunction(_settings.preferred_input)
    HurricaneEnv._setInputFunction(_settings.preferred_input)
    runProgram()
    user_input_file.close()

    #TO USE A MANUAL FILL USE THIS:
    #runProgram()