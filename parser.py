#########NODES###########
from lexer import *

class NumberNode:
    def __init__(self, token):
        self.token = token
        self.start = token.start_pos
        self.end = token.end_pos

class StringNode:
    def __init__(self, token):
        self.token = token
        self.start = token.start_pos
        self.end = token.end_pos

class BoolNode:
    def __init__(self, token):
        self.token = token
        self.start = token.start_pos
        self.end = token.end_pos

class ListNode:
    def __init__(self, nodes, start, end):
        self.nodes = nodes
        self.start = start
        self.end = end

class ListAccessNode:
    def __init__(self, name, index, start, end):
        self.name = name
        self.index = index
        self.start = start
        self.end = end

class VarAccessNode:
    def __init__(self, name, start, end):
        self.name = name
        self.start = start
        self.end = end

class VarAssignNode:
    def __init__(self, name, value, start, end):
        self.name = name
        self.value = value
        self.start = start
        self.end = end

class BinaryOpNode:
    def __init__(self, left_node, op_node, right_node):
        self.left_node = left_node
        self.op_node = op_node
        self.right_node = right_node
        self.start = left_node.start
        self.end = right_node.end

class UnaryOpNode:
    def __init__(self, op_node, right_node):
        self.op_node = op_node
        self.right_node = right_node
        self.start = op_node.start_pos
        self.end = right_node.end

class IfStatementNode:
    def __init__(self, cases, else_case, start, end):
        self.cases = cases
        self.else_case = else_case
        self.start = start
        self.end = end

class WhileLoopNode:
    def __init__(self, condition_node, body_node, start, end):
        self.condition_node = condition_node
        self.body_node = body_node
        self.start = start
        self.end = end

class ForLoopNode:
    def __init__(self, var_name, start_val, end_val, start, end, increment_val=None, body_node=None):
        self.var_name = var_name
        self.start_val = start_val
        self.end_val = end_val
        self.increment_val = increment_val
        self.body_node = body_node
        self.start = start
        self.end = end

class FunctionDefNode:
    def __init__(self, name, arg_names, body_node, start, end):
        self.name = name
        self.arg_names = arg_names
        self.body_node = body_node
        self.start = start
        self.end = end

class CallNode:
    def __init__(self, function_node, arg_nodes, start, end):
        self.function_node = function_node
        self.arg_nodes = arg_nodes
        self.start = start
        self.end = end

class MethodCallNode:
    def __init__(self, method_name, object_node, arg_nodes, start, end):
        self.method_name = method_name
        self.object_node = object_node
        self.arg_nodes = arg_nodes
        self.start = start
        self.end = end

class BreakNode:
    def __init__(self):
        pass

class ContinueNode:
    def __init__(self):
        pass

class ReturnNode:
    def __init__(self, return_node):
        self.return_node = return_node

########PARSERESULT##################
class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None

    def register(self, result): # returns node of parse result
        if isinstance(result, ParseResult):
            return result.node
        return result

    def success(self, node): # sets node of parse result
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self

#########PARSER##############
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = -1
        self.current_token = None
        self.advance()

    def advance(self):
        self.index += 1
        self.current_token = self.tokens[self.index]

    def parse(self):
        result = self.statements()
        if self.index >= len(self.tokens)-1:
            return result  # Success: consumed all tokens
        if self.current_token.type != T_EOF:
            return result.failure(InvalidSyntaxError(self.current_token.start_pos, self.current_token.end_pos,"Expected end of file!"))
        return result

    def statements(self): # return a ParseResult
        result = ParseResult()
        statements = []
        start = self.current_token.start_pos.copy()
        while self.current_token.type == T_NEWLINE:
            self.advance()
        statement = result.register(self.statement())
        if result.error: return result
        if statement is not None:
            statements.append(statement)

        while self.current_token.type == T_NEWLINE and self.current_token.type != T_EOF:
            self.advance()
            if self.current_token.type == T_EOF:
                break
            statement = result.register(self.statement())
            if result.error: return result
            if statement is not None:
                statements.append(statement)

        # print(len(statements))
        node = ListNode(statements, start, self.current_token.end_pos.copy())
        return result.success(node)

    def statement(self):
        result = ParseResult()
        if self.current_token.type == T_KEYWORD:
            if self.current_token.value == KEYWORDS['IF']:
                node = result.register(self.if_statement())
                return result.success(node)
            if self.current_token.value == KEYWORDS['WHILE']:
                node = result.register(self.while_statement())
                return result.success(node)
            if self.current_token.value == KEYWORDS['FOR']:
                node = result.register(self.for_statement())
                return result.success(node)
            if self.current_token.value == KEYWORDS['FUNCTION']:
                node = result.register(self.func_definition())
                return result.success(node)
            if self.current_token.value == KEYWORDS['RETURN']:
                self.advance()
                value = result.register(self.expression())
                return result.success(ReturnNode(value))
            if self.current_token.value == KEYWORDS['BREAK']:
                self.advance()
                return result.success(BreakNode())
            if self.current_token.value == KEYWORDS['CONTINUE']:
                self.advance()
                return result.success(ContinueNode())
            if self.current_token.value == KEYWORDS['VARIABLE']:
                self.advance()
                node = result.register(self.expression())
                return result.success(node)
        node = result.register(self.expression())
        return result.success(node)

    def call(self):
        result = ParseResult()
        node = result.register(self.factor())
        if self.current_token.type == T_PERIOD: # Method call .name()
            start = self.current_token.start_pos.copy()
            self.advance()
            if self.current_token.type != T_IDENTIFIER:
                pass #ERROR
            name = self.current_token.value
            self.advance()
            if self.current_token.type != T_LEFT_PARENT:
                return result.failure(InvalidSyntaxError(
                    self.current_token.start_pos, self.current_token.end_pos,
                    "Expected '(' for method"
                ))
            self.advance()
            args = []

            if self.current_token.type != T_RIGHT_PARENT:
                # Parse args until ')'
                while True:
                    self.advance()
                    arg = result.register(self.expression())
                    if result.error: return result
                    args.append(arg)
                    if self.current_token.type == T_RIGHT_PARENT:
                        break
                    if self.current_token.type != T_COMMA:
                        return result.failure(InvalidSyntaxError(
                            self.current_token.start_pos, self.current_token.end_pos,
                            "Expected ',' or ')' in argument list"
                        ))
                    self.advance()  # Skip comma
            end = self.current_token.end_pos.copy()  # Position of ')'
            self.advance()  # NOW advance past ')'5
            return result.success(MethodCallNode(name, node, args, start, end))
        return result.success(node)

    def factor(self): #
        result = ParseResult()
        token = self.current_token
        start = token.start_pos.copy()
        if self.current_token.type in (T_ADD, T_SUBTRACT): # unary operation
            op_token = token
            self.advance()
            right_node = result.register(self.call()) # return a node
            self.advance()
            return result.success(UnaryOpNode(op_token, right_node))
        if self.current_token.type in (T_INTEGER, T_FLOAT):
            self.advance()
            return result.success(NumberNode(token))
        if self.current_token.type == T_STRING:
            self.advance()
            return result.success(StringNode(token))
        if self.current_token.type == T_KEYWORD and self.current_token.value in (KEYWORDS['TRUE'], KEYWORDS['FALSE']):
            self.advance()
            return result.success(BoolNode(token))
        if self.current_token.type == T_IDENTIFIER:  # variable or function call

            func_token = self.current_token
            name = self.current_token.value
            start = func_token.start_pos.copy()
            self.advance()

            if self.current_token.type != T_LEFT_PARENT: # variables or list access or assignment
                if self.current_token.type == T_LEFT_SQUARE: # list access (NOT assignment)
                    self.advance()
                    index = result.register(self.expression())

                    if self.current_token.type != T_RIGHT_SQUARE:
                        return result.failure(InvalidSyntaxError(start, token.end_pos.copy(), "Expected ']'"))
                    self.advance()
                    return result.success(ListAccessNode(name, index, start, self.current_token.start_pos.copy()))

                if self.current_token.type != T_ASSIGN: # variable access
                    return result.success(VarAccessNode(name, start, self.current_token.start_pos.copy()))
                self.advance()

                if self.current_token.type == T_LEFT_SQUARE:
                    list_node = result.register(self.expression())
                    return result.success(VarAssignNode(name, list_node, start, self.current_token.start_pos.copy()))
                value = result.register(self.expression()) # variable assignment
                return result.success(VarAssignNode(name, value, start, self.current_token.start_pos.copy()))

            # Function call
            self.advance()  # Skip '('
            args = []
            if self.current_token.type != T_RIGHT_PARENT:
                # Parse args until ')'
                while True:
                    arg = result.register(self.expression())

                    if result.error: return result
                    args.append(arg)
                    if self.current_token.type == T_RIGHT_PARENT:
                        break
                    if self.current_token.type != T_COMMA:
                        return result.failure(InvalidSyntaxError(
                            self.current_token.start_pos, self.current_token.end_pos,
                            "Expected ',' or ')' in argument list"
                        ))
                    self.advance()  # Skip comma

                end_pos = self.current_token.end_pos.copy()  # Position of ')'
                self.advance()  # NOW advance past ')'
                return result.success(CallNode(VarAccessNode(name, start, end_pos.copy()), args, start, end_pos))
            return VarAccessNode(name, start, self.current_token.end_pos.copy())

        if self.current_token.type == T_LEFT_PARENT: # expression
            self.advance()
            expression = result.register(self.expression())

            if self.current_token.type != T_RIGHT_PARENT:
                return result.failure(InvalidSyntaxError(start, self.current_token.end_pos.copy(), "Expected ')'"))
            self.advance()
            return result.success(expression)

        if self.current_token.type == T_LEFT_SQUARE: # List creation/assignment
            start = self.current_token.start_pos.copy()
            self.advance()  # skip '['
            elements = []

            if self.current_token.type != T_RIGHT_SQUARE:
                while True:
                    element = result.register(self.expression())
                    if result.error: return result
                    elements.append(element)

                    if self.current_token.type == T_RIGHT_SQUARE:
                        break
                    if self.current_token.type != T_COMMA:
                        return result.failure(InvalidSyntaxError(
                            self.current_token.start_pos,
                            self.current_token.end_pos,
                            "Expected ',' or ']'"
                        ))
                    self.advance()  # skip comma

            self.advance()  # skip ']'
            return result.success(ListNode(elements, start, self.current_token.end_pos.copy()))

        if self.current_token.type == T_KEYWORD and self.current_token.value == KEYWORDS["VARIABLE"]:  # variable creation/initialisation
            start = self.current_token.start_pos.copy()
            self.advance()
            name = self.current_token.value
            self.advance()
            if self.current_token.type == T_ASSIGN:
                self.advance()
                value = result.register(self.expression())
                return result.success(VarAssignNode(name, value, start, self.current_token.end_pos.copy()))
            return result.success(VarAssignNode(name, None, start, self.current_token.end_pos.copy()))


    def exponent_expr(self): # MOST PRECEDENCE
        result = self.bin_op(self.call, [T_EXPONENT])
        return result

    def modulo_expr(self):
        result = self.bin_op(self.exponent_expr, [T_MODULUS])
        return result

    def term(self):
        result = self.bin_op(self.modulo_expr, [T_MULTIPLY, T_DIVIDE])
        return result

    def arithmetic_expr(self): # LEAST PRECEDENCE
        result = self.bin_op(self.term, [T_ADD, T_SUBTRACT])
        return result

    def bin_op(self, function, ops): #
        result = ParseResult()
        node = result.register(function())
        while self.current_token.type in ops:
            op_token = self.current_token
            self.advance()
            right = result.register(function())
            node = BinaryOpNode(node, op_token, right)

        return result.success(node)


    def logic_expr(self): # a < 3
        result = ParseResult()

        # Handle unary NOT
        if self.current_token.type == T_KEYWORD and self.current_token.value == KEYWORDS['NOT']:
            op_token = self.current_token
            self.advance()
            right = result.register(self.logic_expr())  # recursive call
            if result.error:
                return result
            return result.success(UnaryOpNode(op_token, right))

        # Handle comparison as base
        node = result.register(self.comparison_expr())
        if result.error:
            return result

        # Handle AND / OR
        while (self.current_token.type == T_KEYWORD and
               self.current_token.value in (KEYWORDS['AND'], KEYWORDS['OR'])):
            op_token = self.current_token
            self.advance()
            right = result.register(self.logic_expr())
            if result.error:
                return result
            node = BinaryOpNode(node, op_token, right)

        return result.success(node)

    def comparison_expr(self):
        result = ParseResult()
        node = result.register(self.bin_op(self.arithmetic_expr, [T_EQUAL_TO, T_LESS_THAN, T_GREATER_THAN, T_LESS_EQUAL, T_GREATER_EQUAL, T_NOT_EQUAL]))

        return result.success(node)

    def expression(self): # assignment or binary
        result = ParseResult()
        node = result.register(self.logic_expr())
        return result.success(node)

    def if_statement(self):
        result = ParseResult() # if (expr) then
        cases = []
        else_case = None
        start = self.current_token.start_pos.copy()
        self.advance()
        if self.current_token.type != T_LEFT_PARENT:
            return result.failure(InvalidSyntaxError(start, self.current_token.end_pos.copy(), "Expected '('"))
        self.advance()
        condition = result.register(self.expression())
        if self.current_token.type != T_RIGHT_PARENT:
            return result.failure(InvalidSyntaxError(start, self.current_token.end_pos.copy(), "Expected ')'"))
        self.advance()

        if not(self.current_token.type == T_KEYWORD and self.current_token.value == KEYWORDS['THEN']):
            return result.failure(InvalidSyntaxError(start, self.current_token.end_pos.copy(), "Expected " + "'" + KEYWORDS['THEN']  + "'"))
        self.advance()
        while self.current_token.type == T_NEWLINE:
            self.advance()

        body = result.register(self.statements())
        cases.append((condition, body))
        if self.current_token.type == T_KEYWORD and self.current_token.value == KEYWORDS['END']:
            node = IfStatementNode(cases, else_case, start, self.current_token.end_pos.copy())
            self.advance()
            return result.success(node)

        # elif
        while self.current_token.type == T_KEYWORD and self.current_token.value == KEYWORDS['ELIF']:
            self.advance()
            if self.current_token.type != T_LEFT_PARENT:
                return result.failure(InvalidSyntaxError(start, self.current_token.end_pos.copy(), "Expected '('"))
            self.advance()
            condition = result.register(self.expression())
            if self.current_token.type != T_RIGHT_PARENT:
                return result.failure(InvalidSyntaxError(start, self.current_token.end_pos.copy(), "Expected ')'"))
            self.advance()
            if not (self.current_token.type == T_KEYWORD and self.current_token.value == KEYWORDS['THEN']):
                return result.failure(InvalidSyntaxError(start, self.current_token.end_pos.copy(), "Expected " + "'" + KEYWORDS['THEN'] + "'"))
            self.advance()

            body = result.register(self.statements())
            cases.append((condition, body))
            if self.current_token.type == T_KEYWORD and self.current_token.value == KEYWORDS['END']:
                node = IfStatementNode(cases, else_case, start, self.current_token.end_pos.copy())
                self.advance()
                return result.success(node)

        # else
        if self.current_token.type == T_KEYWORD and self.current_token.value == KEYWORDS['ELSE']:
            self.advance()

            else_case = result.register(self.statements())
            if self.current_token.type != T_KEYWORD or self.current_token.value != KEYWORDS['END']:
                return result.failure(InvalidSyntaxError(start, self.current_token.end_pos.copy(), "Expected " + "'" + KEYWORDS['END'] + "'"))
            self.advance()

        node = IfStatementNode(cases, else_case, start, self.current_token.end_pos.copy())
        return result.success(node)

    def while_statement(self):
        result = ParseResult() # while (expr)
        start = self.current_token.start_pos.copy()
        self.advance()
        if self.current_token.type != T_LEFT_PARENT:
            return result.failure(InvalidSyntaxError(start, self.current_token.end_pos.copy(), "Expected '('"))
        self.advance()
        condition = result.register(self.expression())
        if self.current_token.type != T_RIGHT_PARENT:
            return result.failure(InvalidSyntaxError(start, self.current_token.end_pos.copy(), "Expected ')'"))
        self.advance()
        while self.current_token.type == T_NEWLINE:
            self.advance()

        body = result.register(self.statements())
        if self.current_token.type != T_KEYWORD or self.current_token.value != KEYWORDS['END']:
            return result.failure(InvalidSyntaxError(start, self.current_token.end_pos.copy(), "Expected 'end'"))
        self.advance()

        node = WhileLoopNode(condition, body, start, self.current_token.end_pos.copy())
        return result.success(node)

    def for_statement(self):
        result = ParseResult() # count i from start to end using increment
        self.advance()
        start_pos = self.current_token.start_pos.copy()
        if self.current_token.type != T_IDENTIFIER:
            return result.failure(InvalidSyntaxError(start_pos, self.current_token.end_pos.copy(), "Expected variable to count with!"))
        name = self.current_token.value
        increment = None
        self.advance()
        if not(self.current_token.type == T_KEYWORD and self.current_token.value == KEYWORDS['FROM']):
            return result.failure(InvalidSyntaxError(start_pos, self.current_token.end_pos.copy(), "Expected " + "'" + KEYWORDS['FROM'] + "'"))
        self.advance()
        start = result.register(self.expression())
        if not(self.current_token.type == T_KEYWORD and self.current_token.value == KEYWORDS['TO']):
            return result.failure(InvalidSyntaxError(start_pos, self.current_token.end_pos.copy(), "Expected " + "'" + KEYWORDS['TO'] + "'"))
        self.advance()
        end = result.register(self.expression())
        if self.current_token.type == T_KEYWORD and self.current_token.value == KEYWORDS['USING']:
            self.advance()
            increment = result.register(self.expression())

        body = result.register(self.statements())
        if self.current_token.type != T_KEYWORD or self.current_token.value != KEYWORDS['END']:
            return result.failure(InvalidSyntaxError(start, self.current_token.end_pos.copy(), "Expected 'end'"))
        self.advance()

        node = ForLoopNode(name, start, end, start_pos, self.current_token.end_pos.copy(), increment, body)
        return result.success(node)

    def func_definition(self):
        result = ParseResult() # function (args)
        start = self.current_token.start_pos.copy()
        self.advance()
        name = self.current_token.value
        self.advance()
        args = []
        if self.current_token.type != T_LEFT_PARENT:
            return result.failure(InvalidSyntaxError(start, self.current_token.end_pos.copy(), "Expected '('"))
        self.advance()

        # getting a list of arguments
        if self.current_token.type == T_IDENTIFIER: #has arguments
            args.append(self.current_token.value)
            self.advance()
            while self.current_token.type == T_COMMA:
                self.advance()
                if self.current_token.type != T_IDENTIFIER:
                    return result.failure(InvalidSyntaxError(start, self.current_token.end_pos.copy(), "Expected a an argument"))
                args.append(self.current_token.value)
                self.advance()

        if self.current_token.type != T_RIGHT_PARENT:
            return result.failure(InvalidSyntaxError(start, self.current_token.end_pos.copy(), "Expected ')'"))
        self.advance()

        body = result.register(self.statements())

        if self.current_token.type != T_KEYWORD or self.current_token.value != KEYWORDS['END']:
            return result.failure(InvalidSyntaxError(start, self.current_token.end_pos.copy(), "Expected 'end'"))
        self.advance()

        node = FunctionDefNode(name, args, body, start, self.current_token.end_pos.copy())
        return result.success(node)

