###############VALUES###################
from interpreter import *
# All the things that could be stored

class Number:
    def __init__(self, value):
        self.value = value
        self.error = None

    def add(self, other): # takes in a NumberValue
        if self.type_check(other):
            return None, self.error
        return Number(self.value + other.value), self.error

    def subtract(self, other): # takes in a NumberValue
        if self.type_check(other):
            return None, self.error
        return Number(self.value - other.value), self.error

    def multiply(self, other): # takes in a NumberValue
        if self.type_check(other):
            return None, self.error
        return Number(self.value * other.value), self.error

    def divide(self, other): # takes in a NumberValue
        if self.type_check(other):
            return None, self.error
        # divide by zero error
        if other.value == 0:
            self.error = "Divide by zero error"
            return None, self.error
        return Number(self.value / other.value), self.error

    def modulus(self, other): # takes in a NumberValue
        if type(self.value) is not int or type(other.value) is not int:
            self.error = "Can't modulus a non-integer"
            return None, self.error
        return Number(self.value % other.value), self.error

    def exponent(self, other):
        if self.type_check(other):
            return None, self.error
        return Number(pow(self.value, other.value)), self.error

    def is_int(self):
        return True if type(self.value) is int else False

    def type_check(self, other): #check are integers/floats
        if type(other.value) is not int and type(other.value) is not float:
            self.error = "Cannot add a  non-number to a number."
        return self.error

    def is_true(self):
        if self.value > 0:
            return True
        else:
            return False

    def copy(self):
        return Number(self.value), self.error


class String:
    def __init__(self, value):
        self.value = value
        self.error = None

    def methods(self):
        return {
            'upper_case': self.method_upper_case,
            'lower_case': self.method_lower_case
        }

    def add(self, other): # takes in a String
        if self.type_check(other):
            return None, self.error
        return Number(self.value + other.value), self.error

    def method_upper_case(self, args): # makes upper case
        if len(args) == 1:
            pass
        if len(args) == 0:
            return String(self.value.upper())
        #ERROR

    def method_lower_case(self, args): # makes lower case
        if len(args) == 1: # index or letter they want to make lower
            pass
        if len(args) == 0:
            return String(self.value.lower())
        # ERROR
    def type_check(self, other): #check are strings
        if type(other.value) is not str:
            self.error = "Cannot add a non-string to a string."
        return self.error

    def copy(self):
        return String(self.value)

class Bool:
    def __init__(self, value):
        self.value = value
        self.error = None

    def is_true(self):
        if self.value:
            return True
        else:
            return False

    def copy(self):
        return Bool(self.value)


class List:
    def __init__(self, elements):
        self.elements = elements
        self.value = [el.value for el in self.elements]

    def methods(self):
        return {
            'add': self.method_add,
            'remove': self.method_remove,
            'get_index': self.method_get_index,
            'clear': self.method_clear
        }

    def get(self, index):
        if index.value is str:
            return None, "Can't access a list with a non-integer."
        if len(self.elements) <= index.value:
            return None, "Index out of range of list!"
        return self.elements[int(index.value)], None

    def method_add(self, args):
        if len(args) == 1:
            element, index = args[0], None
        elif len(args) == 2:
            element, index = args[0], args[1]
        else:
            return
            pass # ERROR
        if index:
            self.elements.insert(index, element)
        else:
            self.elements.append(element)
        self.value = [el.value for el in self.elements]
        return self

    def method_remove(self, args):
        if len(args) != 1:
            pass # ERROR
        index = args[0]
        self.elements.pop(index)
        self.value = [el.value for el in self.elements]
        return self

    def method_get_index(self, args): # finds first index of an element
        pass

    def method_clear(self, args):
        if len(args) != 0:
            return
            pass # ERROR
        self.elements = []
        self.value = [el.value for el in self.elements]
        return self

    def copy(self):
        return List(self.elements)

class Function:
    def __init__(self, name, args, body):
        self.name = name
        self.args = args
        self.body = body

    def execute(self, parameters, interpreter, context, RTResult):
        # check the number of arguments and parameters


        new_context = Memory(parent=context)

        for i in range(len(parameters)):
            new_context.set(self.args[i], parameters[i])

        result = interpreter.visit(self.body, new_context)

        if result.return_value:
            return RTResult.success(result.return_value)
        return RTResult.success(Number(0))


class Memory: # can store any of the values above
    def __init__(self, parent=None): # where all the variables and functions are stored
        self.parent = parent
        self.variables = {} # dictionary

    def get(self, name): # retrieve a variable value
        if name in self.variables:
            return self.variables[name], None
        if self.parent:
            return self.parent.get(name), None
        return None, "Can't find variable "+name+ "!"

    def set(self, name, value): # create/change a variable
        self.variables[name] = value