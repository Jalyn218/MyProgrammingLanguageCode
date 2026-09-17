#########IMPORTS########
from random import random

from values import *
from parser import *
from lexer import *
import math
import random
import os
import statistics

########RTResult###################
class RTResult:
    def __init__(self):
        self.value = None
        self.error = None
        self.return_value = None
        self.continue_ = False
        self.break_ = False

    def register(self, result): # registering/saving (copying) values in current result
        if isinstance(result, RTResult):
            self.return_value = result.return_value
            self.continue_ = result.continue_
            self.break_ = result.break_
            self.error = result.error
            return result.value
        return result

    def success(self, value): # saving actual value in register and returning register
        self.value = value
        return self

    def success_return(self, value):
        self.return_value = value
        return self

    def success_continue(self):
        self.continue_ = True
        return self

    def success_break(self):
        self.break_ = True
        return self

    def failure(self, error):
        self.error = error
        return self

################INTERPRETER########################
class Interpreter:
    def __init__(self):
        self.global_scope = Memory()
        # add built-in functions to global scope
        self.builtins = {
            'display': BuiltInFunction('display'),
            'input': BuiltInFunction('input'),
            'int': BuiltInFunction('int'),
            'float': BuiltInFunction('float'),
            'str': BuiltInFunction('str'),
            'length': BuiltInFunction('length'),
            'sqrt': BuiltInFunction('sqrt'),
            'min': BuiltInFunction('min'),
            'max': BuiltInFunction('max'),
            'sort': BuiltInFunction('sort'),
            'mean': BuiltInFunction('mean'),
            'median': BuiltInFunction('median'),
            'mode': BuiltInFunction('mode'),
            'total': BuiltInFunction('total'),
            'absolute': BuiltInFunction('absolute'),
            'random_item': BuiltInFunction('random_item'), # gets a random element of a list
            'random_int': BuiltInFunction('random_int'),
            'display_list': BuiltInFunction('display_list'), # puts list in string/table format so can be outputted
            'clear_screen': BuiltInFunction('clear_screen'),
            'is_int': BuiltInFunction('is_int'),
            'is_float': BuiltInFunction('is_float'),
            'is_str': BuiltInFunction('is_str'),
            'is_upper': BuiltInFunction('is_upper'),
            'is_lower': BuiltInFunction('is_lower')
        }
        self.global_scope.set('display', BuiltInFunction('display'))
        self.global_scope.set('input', BuiltInFunction('input'))
        self.global_scope.set('int', BuiltInFunction('int'))
        self.global_scope.set('float', BuiltInFunction('float'))
        self.global_scope.set('str', BuiltInFunction('str'))
        self.global_scope.set('length', BuiltInFunction('length'))
        self.global_scope.set('sqrt', BuiltInFunction('sqrt'))
        self.global_scope.set('min', BuiltInFunction('min'))
        self.global_scope.set('max', BuiltInFunction('max'))
        self.global_scope.set('sort', BuiltInFunction('sort'))
        self.global_scope.set('mean', BuiltInFunction('mean'))
        self.global_scope.set('median', BuiltInFunction('median'))
        self.global_scope.set('mode', BuiltInFunction('mode'))
        self.global_scope.set('total', BuiltInFunction('total'))
        self.global_scope.set('absolute', BuiltInFunction('absolute'))
        self.global_scope.set('random_item', BuiltInFunction('random_item'))
        self.global_scope.set('random_int', BuiltInFunction('random_int'))
        self.global_scope.set('display_list', BuiltInFunction('display_list'))
        self.global_scope.set('clear_screen', BuiltInFunction('clear_screen'))
        self.global_scope.set('is_int', BuiltInFunction('is_int'))
        self.global_scope.set('is_float', BuiltInFunction('is_float'))
        self.global_scope.set('is_str', BuiltInFunction('is_str'))
        self.global_scope.set('is_upper', BuiltInFunction('is_upper'))
        self.global_scope.set('is_lower', BuiltInFunction('is_lower'))



    def visit(self, node, context=None):
        name = f'visit_{type(node).__name__}'
        function = getattr(self, name, self.no_visit_method) # noinspection PyUnresolvedReferences
        # print("Visiting:", type(node).__name__)
        return function(node, context or self.global_scope) # noinspection

    def no_visit_method(self, node, context): # there is no visit method for that node
        print("No method")

    def visit_NumberNode(self, node, context):
        result = RTResult()
        return result.success(Number(node.token.value))

    def visit_StringNode(self, node, context):
        result = RTResult()
        return result.success(String(node.token.value))

    def visit_BoolNode(self, node, context):
        result = RTResult()
        if node.token.value == 'true':
            return result.success(Bool(True))
        return result.success(Bool(False))

    def visit_ListNode(self, node, context):
        result = RTResult()
        elements = []
        for element_node in node.nodes:
            element_value = result.register(self.visit(element_node, context))
            if result.error: return result
            elements.append(element_value)
            if result.break_:
                return result.success_break()

        return result.success(List(elements))

    def visit_ListAccessNode(self, node, context):
        result = RTResult()
        name = node.name
        index = result.register(self.visit(node.index, context))
        if result.error: return result
        list, error = context.get(name) # returns list node
        if error:
            return result.failure(RTError(node.start, node.end, error, context))
        value, error = list.get(index)
        if error:
            return result.failure(RTError(node.start, node.end, error, context))
        return result.success(value)

    def visit_VarAccessNode(self, node, context):
        result = RTResult()
        var_name = node.name
        value, error = context.get(var_name)

        if error:
            return result.failure(RTError(node.start, node.end, error, context))
        if value is None:
            return result.failure(RTError(node.start, node.end, 'Variable has no value', context))
        return result.success(value)

    def visit_VarAssignNode(self, node, context): # works for lists too
        result = RTResult()
        if node.value: # variable has been created but not assigned a value yet
            value = result.register(self.visit(node.value, context))
            if result.error: return result
            context.set(node.name, value)
        else:
            value = String('')
            context.set(node.name, value)

        return result.success(value)

    def visit_BinaryOpNode(self, node, context):
        result = RTResult()
        left = result.register(self.visit(node.left_node, context))
        if result.error: return result

        right = result.register(self.visit(node.right_node, context))
        if result.error: return result

        op = node.op_node
        output = None
        error = None
        if op.type == T_ADD: output, error = left.add(right)
        elif op.type == T_SUBTRACT: output, error = left.subtract(right)
        elif op.type == T_MULTIPLY: output, error = left.multiply(right)
        elif op.type == T_DIVIDE: output, error = left.divide(right)
        elif op.type == T_MODULUS: output, error = left.modulus(right)
        elif op.type == T_EXPONENT: output, error = left.exponent(right)
        elif op.type == T_EQUAL_TO:
            output = Bool(True) if left.value == right.value else Bool(False)
        elif op.type == T_NOT_EQUAL:
            output = Bool(True) if left.value != right.value else Bool(False)
        elif op.type == T_GREATER_THAN:
            output = Bool(True) if left.value > right.value else Bool(False)
        elif op.type == T_LESS_THAN:
            output = Bool(True) if left.value < right.value else Bool(False)
        elif op.type == T_GREATER_EQUAL:
            output = Bool(True) if left.value >= right.value else Bool(False)
        elif op.type == T_LESS_EQUAL:
            output = Bool(True) if left.value <= right.value else Bool(False)
        elif op.value == KEYWORDS['AND']:
            output = Bool(left.is_true() and right.is_true())
        elif op.value == KEYWORDS['OR']:
            output = Bool(left.is_true() or right.is_true())
        elif op.type == T_ASSIGN:
            pass
        if error:
            return result.failure(RTError(node.start, node.end, error, context))
        if output:
            return result.success(output)
        return result.failure(InvalidSyntaxError(node.start, node.end, "Invalid Operation!"))

    def visit_UnaryOpNode(self, node, context):
        result = RTResult()
        number = result.register(self.visit(node.right_node, context))
        if result.error: return result
        if node.op_node.type == T_SUBTRACT:
            return result.success(Number(-number.value))
        elif node.op_node.value == KEYWORDS['NOT']:
            return result.success(Bool(not number.is_true()))
        return result.success(Number(number.value))

    def visit_IfStatementNode(self, node, context):
        result = RTResult()
        otherwise = True  # determines whether else statement in played
        for condition, body in node.cases:
            logic = result.register(self.visit(condition, context))
            if result.error: return result
            if result.continue_:
                continue
            if logic.is_true(): # if true play if statement
                otherwise = False # don't need to play else statement
                body_res = result.register(self.visit(body, context))
                if result.error: return result

        if node.else_case and otherwise:
            body_res = result.register(self.visit(node.else_case, context))
            if result.error: return result
        return result.success(Number(0))

    def visit_WhileLoopNode(self, node, context):
        result = RTResult()
        while True:
            condition = node.condition_node
            logic = result.register(self.visit(condition, context))
            if result.error: return result
            if not logic.is_true():
                break
            body_res = result.register(self.visit(node.body_node, context))
            if result.break_:
                break
            if result.continue_:
                continue

        return result.success(Number(0))

    def visit_ForLoopNode(self, node, context):
        result = RTResult()
        start = result.register(self.visit(node.start_val))
        if result.error: return result
        end = result.register(self.visit(node.end_val))
        if result.error: return result
        # check they are integers
        if not(start.is_int() and end.is_int()):
            return result.failure(RTError(node.start, node.end, "Need integers to count", context))
        if node.increment_val: # there is an increment value
            increment = result.register(self.visit(node.increment_val))
            if result.error: return result
            i, error = start.copy()
            # check increment works
            if start.value > end.value: # need to keep decreasing)
                # CHECK
                if (start.value - end.value) % increment.value != 0:
                    return result.failure(RTError(node.start, node.end, '', context))
                stop, error = end.subtract(increment)
            else:
                if (end.value - start.value) % increment.value != 0:
                    return result.failure(RTError(node.start, node.end, '', context))
                stop, error = end.add(increment)

            while i.value != stop.value:
                context.set(node.var_name, i)
                # set var to i
                body_res = result.register(self.visit(node.body_node, context))
                if result.error: return result
                i, error = i.add(increment) # increment
                if error:
                    return result.failure(error)
                if result.break_:
                    break
                if result.continue_:
                    continue
        else: # no increment value so increase by 1 or -1 each time
            i, error = start.copy()

            if start.value > end.value: # need to keep decreasing
                stop, error = end.subtract(Number(1))
                increment = Number(-1)
            else:
                stop, error = end.add(Number(1))
                increment = Number(1)

            while i.value != stop.value:
                context.set(node.var_name, i)
                # set var to i
                body_res = result.register(self.visit(node.body_node, context))
                if result.error: return result
                i, error = i.add(increment) # increment
                if error:
                    return result.failure(error)
                if result.break_:
                    break
                if result.continue_:
                    continue
        return result.success(Number(0))


    def visit_FunctionDefNode(self, node, context):
        result = RTResult()
        function = Function(node.name, node.arg_names, node.body_node)
        context.set(function.name, function) # store function
        return result.success(function)

    def visit_CallNode(self, node, context):
        result = RTResult()
        args = []
        for arg_node in node.arg_nodes:
            arg_value_result = result.register(self.visit(arg_node, context))
            if result.error: return result
            args.append(arg_value_result)
        # if is a function
        if isinstance(node.function_node, VarAccessNode):
            name = node.function_node.name
            function = context.get(name)
        else:
            function = result.register(self.visit(node.function_node, context))
            if result.error: return result
        # if is a built in function
        if node.function_node.name in self.builtins:
            value = result.register(self.builtins[node.function_node.name].execute(args, node.start, node.end, context))
            if result.error: return result
            return value
        # if is a user defined function
        if isinstance(function, Function):
            value = result.register(function.execute(args, self, context, RTResult()))
            if result.error: return result
            return value
            #return result.success(value if value is not None else Number(0))
        return result.failure(RTError(node.start, node.end, "Undefined identifier!", result))

    def visit_MethodCallNode(self, node, context):
        result = RTResult()
        obj = result.register(self.visit(node.object_node, context))
        if result.error: return result
        if not hasattr(obj, "methods"):
            return RTResult().failure(RTError(node.start, node.end, "Object has no methods!", context))
        methods = obj.methods()
        args = []
        if node.method_name not in methods:
            return RTResult().failure(RTError(node.start, node.end, "Invalid method!", context))
        for arg_node in node.arg_nodes:
            arg = result.register(self.visit(arg_node, context))
            if result.error: return result
            args.append(arg)

        method = methods[node.method_name]
        return result.success(method(args))


    def visit_BreakNode(self, node, context):
        return RTResult().success_break()

    def visit_ContinueNode(self, node, context):
        return RTResult().success_continue()

    def visit_ReturnNode(self, node, context):
        result = RTResult()
        value = result.register(self.visit(node.return_node, context))
        if result.error: return result
        return result.success_return(value)


########BUILT-IN FUNCTIONS################
class BuiltInFunction:
    def __init__(self, name):
        self.name = name

    def execute(self, args, start, end, context):
        if self.name == 'display':
            print(*[str(a.value) for a in args])
            return RTResult().success(Number(0))
        elif self.name == 'input':
            prompt = ''
            if len(args) > 0:
                prompt = str(args[0].value)
            user_input = input(prompt)
            return RTResult().success(String(user_input))
        elif self.name == 'int':
            if len(args) != 1:
                return RTResult().failure(RTError(start, end, "Expected 1 argument!", context))
            if not isinstance(args[0], Number):
                return RTResult().failure(RTError(start, end, "Can't convert a non-number to an integer!", context))
            return RTResult().success(Number(int(args[0].value)))
        elif self.name == 'float':
            if len(args) != 1:
                return RTResult().failure(RTError(start, end, "Expected 1 argument!", context))
            if not isinstance(args[0], Number):
                return RTResult().failure(RTError(start, end, "Can't convert a non-number to a float!", context))
            return RTResult().success(Number(float(args[0].value)))
        elif self.name == 'string':
            if len(args) != 1:
                return RTResult().failure(RTError(start, end, "Expected 1 argument!", context))
            if isinstance(args[0], List):
                return RTResult().failure(RTError(start, end, "Invalid argument!", context))
            return RTResult().success(Number(str(args[0].value)))
        elif self.name == 'length':
            if len(args) == 1 and isinstance(args[0], List):
                length = len(args[0].elements)
            else:
                length = len(args)
            return RTResult().success(Number(length))
        elif self.name == 'sqrt':
            if len(args) != 1:
                return RTResult().failure(RTError(start, end, "Expected 1 argument!", context))
            return math.sqrt(args[0])
        elif self.name == 'min': #
            lowest, index = 100000000000, -1
            if len(args) != 1:
                return RTResult().failure(RTError(start, end, "Expected 1 argument!", context))
            for i in range(len(args[0].elements)):
                el = args[0].elements[i]
                if el < lowest:
                    lowest, index =  el, i
            return RTResult().success(Number(lowest))
        elif self.name == 'max': #
            highest, index = -100000000000,  -1
            if len(args) != 1:
                return RTResult().failure(RTError(start, end, "Expected 1 argument!", context))
            for i in range(len(args[0].elements)):
                el = args[0].elements[i]
                if el > highest:
                    highest, index =  el, i
            return RTResult().success(Number(highest))
        elif self.name == 'sort': # use quicksort TODO7
            if len(args) == 1:
                l = args[0].elements
                l.sort()
                return RTResult().success(List(l))
            elif len(args) == 2:
                if args[1] == 'decreasing':
                    l = args[0].elements
                    l.sort(reverse=True)
                else: # increasing is default
                    l = args[0].elements
                    l.sort()
                return RTResult().success(List(l))
            return RTResult().failure(RTError(start, end, "Expected 1 or 2 arguments!", context))
        elif self.name == 'mean':
            total = 0
            if len(args) == 1 and isinstance(args[0], List): # is a list
                list_ = args[0].elements
            else:
                list_ = args
            number = len(list_)
            for x in list_:
                total += x.value
            return RTResult().success(Number(total/number))
        elif self.name == 'median':
            if len(args) != 1:
                return RTResult().failure(RTError(start, end, "Expected 1 argument!", context))
            if isinstance(args[0], List):
                middle = math.ceil(len(args[0].elements)/2) - 1
                l = []
                for el in args[0].elements:
                    l.append(el.value)
                l.sort()
                if len(args[0].elements) % 2 == 0:
                    lower_middle = l[middle]
                    upper_middle = l[middle+1]
                    return RTResult().success(Number((lower_middle+upper_middle)/2))
                else:
                    return RTResult().success(Number(l[middle]))

            return RTResult().success(args[0])
        elif self.name == 'mode':
            if len(args) != 1:
                return RTResult().failure(RTError(start, end, "Expected 1 argument!", context))
            if not isinstance(args[0], List):
                return RTResult().failure(RTError(start, end, "Expected a list", context))
            l = args[0].value
            item = statistics.mode(l)
            if type(item) is int or type(item) is float:
                return RTResult().success(Number(item))
            elif type(item) is str:
                return RTResult().success(String(item))
        elif self.name == 'total':
            total = 0
            if len(args) == 1 and isinstance(args[0], List): # is a list
                list_ = args[0].elements
            else:
                list_ = args
            for x in list_:
                total += x.value
            return RTResult().success(Number(total))
        elif self.name == 'absolute':
            if len(args) != 1:
                return RTResult().failure(RTError(start, end, "Expected 1 argument!", context))
            if args[0] >= 0:
                return RTResult().success(args[0])
            else:
                return RTResult().success(args[0].multiply(Number(-1)))
        elif self.name == 'random_item':
            if len(args) != 1:
                return RTResult().failure(RTError(start, end, "Expected 1 argument!", context))
            if not isinstance(args[0], List):
                return RTResult().success(args[0])
            random_index = random.randint(1,len(args[0].elements))
            return RTResult().success(args[0].elements[random_index])
        elif self.name == 'random_int':
            if len(args) != 2:
                return RTResult().failure(RTError(start, end, "Expected 2 arguments!", context))
            return RTResult().success(Number(random.randint(args[0].value, args[1].value)))
        elif self.name == 'display_list': # TODO
            if len(args) != 1:
                return RTResult().failure(RTError(start, end, "Expected 1 argument!", context))
            if isinstance(args[0], List):
                return RTResult().failure(RTError(start, end, "Expected a list!", context))
            l = [el.value for el in args[0].elements]
            r = [[str(i)] for i in l] if not isinstance(l[0], list) else [list(map(str, row)) for row in l]
            w = [max(map(len, c)) for c in zip(*r)]
            s = ("\n".join("  ".join(f"{c:<{w[i]}}" for i, c in enumerate(row)) for row in r))
            return RTResult.success(String(s))
        elif self.name == 'clear_screen':
            if len(args) != 0:
                return RTResult().failure(RTError(start, end, "Expected NO argument!", context))
            os.system('cls')
        elif self.name == 'is_int':
            if isinstance(args[0], Number):
                if args[0].is_int():
                    return RTResult().success(Bool(True))
            RTResult().success(Bool(False))
        elif self.name == 'is_float':
            if isinstance(args[0], Number):
                if not args[0].is_int():
                    return RTResult().success(Bool(True))
            RTResult().success(Bool(False))
        elif self.name == 'is_str':
            if isinstance(args[0], String):
                return RTResult().success(Bool(True))
            RTResult().success(Bool(False))
        elif self.name == 'is_upper':
            if len(args) == 1:
                if isinstance(args[0], String):
                    if args[0].value == args[0].value.upper():
                        return RTResult().success(Bool(True))
                RTResult().success(Bool(False))
            elif len(args) == 2:
                if isinstance(args[0], String):
                    l, i = args[0], args[1]
                    if len(l.elements) <= i:
                        return RTResult().failure(RTError(start, end, "Index argument out of range!", context))
                    if l[i].value == l[i].value.upper():
                        return RTResult().success(Bool(True))
                RTResult().success(Bool(False))
            return RTResult().failure(RTError(start, end, "Expected 1 or 2 arguments!", context))
        elif self.name == 'is_lower': # TODO
            if len(args) == 1:
                if isinstance(args[0], String):
                    if args[0].value == args[0].value.upper():
                        return RTResult().success(Bool(True))
                RTResult().success(Bool(False))
            elif len(args) == 2:
                if isinstance(args[0], String):
                    l, i = args[0], args[1]
                    if len(l.elements) <= i:
                        return RTResult().failure(RTError(start, end, "Index argument out of range!", context))
                    if l[i].value == l[i].value.upper():
                        return RTResult().success(Bool(True))
                RTResult().success(Bool(False))
            return RTResult().failure(RTError(start, end, "Expected 1 or 2 arguments!", context))
        else:
            return RTResult().failure(RTError(start, end, "No in-built function with that name!", context))
