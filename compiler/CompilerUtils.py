from enum import Enum
import subprocess
import random
import os


class Language(Enum):
    PYTHON = 1
    JAVA = 2


# The ExecutionStatus class is an enum, one of which will be returned by the execute method
class ExecutionStatus(Enum):
    NYR = 0  # Still Executing .... may take a few more time to get results
    ACC = 1  # Executed successfully, Solution correct, accepted
    WRA = 2  # Executed successfully, Solution wrong, rejected
    TLE = 3  # Executed, but exceeded time limit
    COE = 4  # Compilation failed
    RTE = 5  # Error encountered during Execution
    INE = 6  # Internal error has occurred, prompt user to try again! ( we'll be screwed if this happens often)


class TestCase:
    input_data = None
    output_data = None

    def __init__(self, input_data, expected_output):
        self.input_data = input_data
        self.output_data = expected_output

    def get_input(self):
        return self.input_data

    def get_output(self):
        return self.output_data


def generate_test_cases(input_string, output_string):
    test_cases = []
    inputs = [x.strip() for x in input_string.split(sep='$END')]
    outputs = [x.strip() for x in output_string.split(sep='$END')]
    if len(inputs) is not len(outputs):
        return None  # need a better way :(
    else:
        # removing last blank space (if any) generated due to split function
        if len(inputs[len(inputs)-1]) == 0:
            del inputs[len(inputs)-1]
            del outputs[len(outputs)-1]
        for i in range(len(inputs)):
            test_cases.append(TestCase(inputs[i], outputs[i]))
        return test_cases


def generate_rand_name(length):
    generated = ""
    for i in range(length):
        base = 97 if random.randint(0, 1) == 0 else 65
        offset = random.randint(0, 25)
        generated += chr(base+offset)
    return generated


class Compiler:
    exec_status = None  # exec_status:None denotes that the program has'nt been executed yet (hasExecuted=False)
    code = None
    template = None
    test_cases = None
    outputs = None
    errors = None
    failed_test_cases = None  # once execute() is called, this value will be set
    language = None
    filename = None
    hasErrors = False
    hasExecuted = False
    hasFile = False
    maxExecTime = 5  # [unit: seconds] Default value, can be overridden

    def add_test_case(self, test_case):
        print("** Test case added **")
        if isinstance(test_case, TestCase):
            if self.test_cases is None:
                self.test_cases = []
            self.test_cases.append(test_case)
        else:
            raise ValueError("Trying to add Invalid test case!")
        return

    def get_num_test_cases(self):
        if self.test_cases is None:
            return 0
        else:
            return len(self.test_cases)

    def get_num_failed_test_cases(self):
        return self.failed_test_cases

    def set_language(self, l):
        if isinstance(l, Language):
            self.language = l
        else:
            self.language = None
            raise ValueError("Invalid language")

    def set_code(self, code):
        self.code = code
        return

    def set_template(self, template):
        if template is not None:
            self.template = template + "\r\n"
        return

    def set_max_exec_time(self, time_in_seconds):
        self.maxExecTime = time_in_seconds
        return

    # returns a list of outputs according to the respective test cases
    def get_output(self):
        if self.hasExecuted:
            return self.outputs
        else:
            return None

    # returns a list of errors according to the respective test cases
    def get_errors(self):
        if self.hasErrors:
            return self.errors
        else:
            return None

    def contains_errors(self):
        return self.hasErrors

    def generate_code_file(self):
        self.filename = generate_rand_name(10)
        if self.filename is None:
            print("*** ERROR : Filename cannot be generated! ***")
        if self.template is not None:
            complete_code = self.template + "\r\n" + self.code
        else:
            complete_code = self.code+"\r\n"
        file_handle = open(self.filename, "w")
        file_handle.write(complete_code)
        file_handle.flush()
        file_handle.close()

    def delete_code_file(self):
        if self.filename is None:
            print("*** ERROR: filename NONE ***")
        os.remove(self.filename)
        self.hasFile = False
        self.filename = None

    def compare_outputs(self):
        index = 0
        values = []
        for test_case in self.test_cases:
            expected_output = test_case.get_output()
            actual_output = self.outputs[index].strip()

            # Debug ONLY..........................
            print("## len(self.outputs) = "+str(len(self.outputs)))
            print("## index = "+str(index))
            print("# EX: "+expected_output)
            print("# len : "+str(len(str(expected_output))))
            print("# AC: "+actual_output)
            print("# len : "+str(len(str(actual_output))))
            print("# Comparison : "+str(expected_output == actual_output))
            print("\n")
            # Debug ONLY............................

            values.append(expected_output == actual_output)
            index += 1

        # Debug ONLY .....................
        print("Values .... ")
        for v in values:
            print(str(v))
        # Debug ONLY .....................

        return values

    def execute(self):
        self.exec_status = ExecutionStatus.NYR

        if self.language is not None:

            if not self.hasFile or self.filename is None:
                self.generate_code_file()

            if self.language == Language.PYTHON:
                command = ["python", self.filename]

                if self.outputs is None:
                    self.outputs = []

                if self.errors is None:
                    self.errors = []

                print("Test cases # : "+str(len(self.test_cases)))
                for test_case in self.test_cases:
                    process = subprocess.Popen(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

                    try:
                        o, e = process.communicate(str(test_case.get_input()).encode('utf-8'), timeout=self.maxExecTime)
                        self.outputs.append(o.decode('utf-8'))

                        if len(e) != 0:
                            self.errors.append(e.decode('utf-8'))
                            self.hasErrors = True
                        else:
                            self.errors.append(None)

                        self.hasExecuted = True

                    except subprocess.TimeoutExpired:
                        print("*** TIMEOUT, killing process... ***")
                        if process is not None:
                            process.kill()
                        self.hasExecuted = False
                        self.exec_status = ExecutionStatus.TLE
                        break

                if self.hasExecuted:
                    comparisons = self.compare_outputs()
                    if False in comparisons:
                        self.exec_status = ExecutionStatus.WRA
                        self.failed_test_cases = comparisons.count(False)
                    else:
                        self.exec_status = ExecutionStatus.ACC
                        self.failed_test_cases = 0
            else:
                print("*** Error : Unknown Programming language Selected ****")
                self.exec_status = ExecutionStatus.INE
        else:
            print("*** Error : No Programming Language Selected ***")
            self.exec_status = ExecutionStatus.INE
        return self.exec_status
