import main
import _settings
input = input

def _setInputFunction():
    global input
    input = _settings.preferred_input
    main._setInputFunction()

def AutoTestAll(): #Don't run manualTest in the same run of an autoTest
    test_numbers = [7]
    for test_number in test_numbers:
        AutoTest(test_number)

def manualTest():
    _settings.makeInputManual()
    _setInputFunction()
    main.runProgram()

def AutoTest(test_number):
    user_input_file = open("tests/user_input_"+str(test_number)+".txt")
    _settings.makeInputAuto(user_input_file)
    _setInputFunction()
    main.runProgram()
    user_input_file.close()