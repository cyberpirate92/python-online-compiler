from enum import Enum
import subprocess
import random
import os


class Language(Enum):
    PYTHON = 1
    JAVA = 2


class TestCase:
    input_data = None
    output_data = None

    def __init__(self,input_data,expected_output):
        self.input_data = input_data
        self.output_data = expected_output

    def getInput(self):
        return self.input_data

    def getOutput(self):
        return self.output_data


def generateTestCases(inputString,outputString):
    test_cases = []
    inputs = [x.strip() for x in inputString.split(sep='$END')]
    outputs = [x.strip() for x in outputString.split(sep='$END')]
    if len(inputs) is not len(outputs):
        return None  # need a better way :(
    else:
        # removing last blank space (if any) generated due to split function
        if len(inputs[len(inputs)-1]) == 0:
            del inputs[len(inputs)-1]
            del outputs[len(outputs)-1]
        for i in range(len(inputs)):
            test_cases.append(TestCase(inputs[i],outputs[i]))
        return test_cases


class Compiler:
    code = None
    template = None
    test_cases = None
    outputs = None
    errors = None
    language = None
    filename = None
    hasErrors = False
    hasExecuted = False
    hasFile = False
    maxExecTime = 60  # Default value, can be overridden

    def addTestCase(self,test_case):
        if isinstance(test_case,TestCase):
            if self.test_cases is None:
                self.test_cases = []
            self.test_cases.append(test_case)
        else:
            raise ValueError("Trying to add Invalid test case!")
        return

    def setLanguage(self,l):
        if isinstance(l,Language):
            self.language = l
        else:
            self.language = None
            raise ValueError("Invalid language")

    def setCode(self,code):
        self.code = code
        return

    def setTemplate(self,template):
        self.template = template + "\r\n"
        return

    def setMaxExecTime(self,timeInSeconds):
        self.maxExecTime = timeInSeconds
        return

    # returns a list of outputs according to the respective test cases
    def getOutput(self):
        if self.hasExecuted:
            return self.outputs
        else:
            return None

    # returns a list of errors according to the respective test cases
    def getErrors(self):
        if self.hasErrors:
            return self.errors
        else:
            return None

    def containsErrors(self):
        return self.hasErrors

    def generateRandName(self,length):
        generated = ""
        for i in range(length):
            base = 97 if random.randint(0,1)==0 else 65
            offset = random.randint(0,25)
            generated += chr(base+offset)
        return generated

    def generateCodeFile(self):
        self.filename = self.generateRandName(10)
        completeCode = None
        if self.template is not None:
            completeCode = self.template +"\r\n"+ self.code
        else:
            completeCode = self.code+"\r\n"
        file_handle = open(self.filename,"w")
        file_handle.write(completeCode)
        file_handle.flush()
        file_handle.close()

    def deleteCodeFile(self):
        os.remove(self.filename)
        self.hasFile = False
        self.filename = None

    def checkOutputs(self):
        index = 0
        values = []
        for testcase in self.test_cases:
            expected_output = testcase.getOutput()
            actual_output = self.outputs[index].strip()

            # Debug ONLY..........................
            print("EX: "+expected_output)
            print("len : "+str(len(str(expected_output))))
            print("AC: "+actual_output)
            print("len : "+str(len(str(actual_output))))
            # Debug ONLY............................

            values.append(expected_output is actual_output)
            index += 1

        # Debug ONLY .....................
        print("Values .... ")
        for v in values:
            print(str(v))
        # Debug ONLY .....................

        return values


    def execute(self):
        if self.language is not None:
            if not self.hasFile or self.filename is None:
                self.generateCodeFile()
            if self.language == Language.PYTHON:
                command = ["python",self.filename]
                if self.outputs is None:
                    self.outputs = []
                if self.errors is None:
                    self.errors = []
                print("Testcases # : "+str(len(self.test_cases)))
                for test_case in self.test_cases:
                    process = subprocess.Popen(command,stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
                    o,e = process.communicate(str(test_case.getInput()).encode('utf-8'))
                    self.outputs.append(o.decode('utf-8'))
                    if len(e) != 0:
                        self.errors.append(e.decode('utf-8'))
                        self.hasErrors = True
                    else:
                        self.errors.append(None)
                self.hasExecuted = True
            else:
                pass
        else:
            pass
        return
