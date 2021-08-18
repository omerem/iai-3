import HurricaneEnv
import main
stdin = input
preferred_input = None
DEBUG_MODE = False

def makeInputAuto(user_input_file):
    global stdin
    global preferred_input
    def auto_input(message=""):
        try:
            print(message)
            p = next(user_input_file)
            print(p)
            if p[-1] == '\n':
                p = p[0:-1]
            return p
        except:
            HurricaneEnv._setInputFunction(stdin)
            main._setInputFunction(stdin)
            p = stdin()
            return p
    preferred_input = auto_input

def makeInputManual():
    global stdin
    global preferred_input
    preferred_input = stdin

def debug_print(msg):
    if DEBUG_MODE:
        print(msg)
    else:
        pass

