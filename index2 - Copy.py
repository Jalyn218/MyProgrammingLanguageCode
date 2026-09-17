def string_with_arrows(text, pos_start, pos_end):
    result = ''

    # Calculate indices
    idx_start = max(text.rfind('\n', 0, pos_start.index), 0)
    idx_end = text.find('\n', idx_start + 1)
    if idx_end < 0: idx_end = len(text)

    # Generate each line
    line_count = pos_end.line - pos_start.line + 1
    for i in range(line_count):
        # Calculate line columns
        line = text[idx_start:idx_end]
        col_start = pos_start.col if i == 0 else 0
        col_end = pos_end.col if i == line_count - 1 else len(line) - 1

        # Append to result
        result += line + '\n'
        result += ' ' * col_start + '^' * (col_end - col_start)

        # Re-calculate indices
        idx_start = idx_end
        idx_end = text.find('\n', idx_start + 1)
        if idx_end < 0: idx_end = len(text)

    return result.replace('\t', '')

###################ERRORS##################
class Error:
    def __init__(self, start, end, error_name, details):
        self.start = start
        self.end = end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result = f'{self.error_name}: {self.details}\n'
        result += f'File {self.start.file_name}, line {self.start.line + 1}'
        result += '\n\n' + string_with_arrows(self.start.file_text, self.start, self.end)
        return result


class IllegalCharError(Error):
  def __init__(self, start, end, details):
    super().__init__(start, end, 'Illegal Character', details)

class ExpectedCharError(Error):
  def __init__(self, start, end, details):
    super().__init__(start, end, 'Expected Character', details)

class InvalidSyntaxError(Error):
  def __init__(self, start, end, details=''):
    super().__init__(start, end, 'Invalid Syntax', details)


class RTError(Error):
  def __init__(self, start, end, details, context):
    super().__init__(start, end, 'Runtime Error', details)
    self.context = context

  def as_string(self):
    result  = self.error_name + "\n" + self.details
    return result

DIGITS = '0123456789'
LETTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


########TOKENS########
# Basically all the syntax I am using
# Operator
T_ADD = 'ADD'
T_SUBTRACT = 'SUBTRACT'
T_MULTIPLY = 'MULTIPLY'
T_DIVIDE = 'DIVIDE'
T_MODULUS = 'MODULUS'
T_EXPONENT = 'EXPONENT'
T_QUOTIENT = 'QUOTIENT'

T_ASSIGN = 'ASSIGN'

T_EQUAL_TO =  'EQUAL_TO'
T_GREATER_THAN = 'GREATER_THAN'
T_LESS_THAN = 'LESS_THAN'
T_GREATER_EQUAL = 'GREATER_EQUAL'
T_LESS_EQUAL = 'LESS_EQUAL'
T_NOT_EQUAL = 'NOT_EQUAL'

# Values
T_INTEGER = 'INTEGER'
T_FLOAT = 'FLOAT'
T_STRING = 'STRING'
T_BOOL = 'BOOL'
T_LIST = 'LIST'
T_NONE = 'NONE'

# Other
T_LEFT_PARENT = 'LEFT_PARENT'
T_RIGHT_PARENT = 'RIGHT_PARENT'
T_RIGHT_SQUARE = 'RIGHT_SQUARE'
T_LEFT_SQUARE = 'LEFT_SQUARE'

T_NEWLINE = 'NEWLINE'
# T_INDENT = 'INDENT'
T_COMMA = 'COMMA'
T_PERIOD = 'PERIOD'

T_IDENTIFIER = 'IDENTIFIER'
T_KEYWORD = 'KEYWORD'
T_EOF = 'END_OF_FILE'

# Keywords
KEYWORDS = { # dictionary so it is easier to edit syntax
    'VARIABLE': 'var',
    'CONTINUE': 'skip', # continue
    'BREAK': 'exit', # break
    'RETURN': 'return', # return
    'IF': 'if',
    'ELSE': 'otherwise',
    'ELIF': 'butif',
    'THEN': 'then',
    'WHILE': 'while',
    'FOR': 'count',
    'FROM': 'from',
    'TO': 'to',
    'USING': 'using',
    'END': 'end',
    'FUNCTION': 'function',
    'AND': 'and',
    'OR': 'or',
    'NOT': 'not',
    'TRUE': 'true',
    'FALSE': 'false'
}

##########POSITION###########
class Position:
    def __init__(self, index, line, col, file_name, file_text):
        self.index = index
        self.line = line
        self.col = col
        self.file_name = file_name
        self.file_text = file_text # to show area in text for error messages

    def advance(self, current_char): # move one position to the left
        self.index += 1
        self.col += 1
        if current_char == '\n':
            self.col = 0
            self.line += 1
        new_char = self.file_text[self.index] if self.index < len(self.file_text) else None

        return new_char

    def peek_next(self): # check character at next index
        next_index = self.index + 1
        next_char = None if self.index >= len(self.file_text)-1 else self.file_text[next_index]
        return next_char

    def copy(self):
        return Position(self.index, self.line, self.col, self.file_name, self.file_text)

############TOKEN###########
class Token:
    def __init__(self, token_type, start_pos, end_pos=None, value=None):
        self.type = token_type
        self.value = value
        self.start_pos = start_pos.copy()
        self.end_pos = start_pos.copy()
        if end_pos: # if there is an end position
            self.end_pos = end_pos.copy()


############LEXER###########
class Lexer:
    def __init__(self, file_name, file_text):
        self.pos = Position(-1, 1, -1, file_name, file_text)
        self.current_char = ''
        self.error = None
        self.current_char = self.pos.advance(self.current_char)

    def make_tokens(self):
        tokens = []
        while self.current_char:
            # creating tokens
            if self.current_char == ' ':
                # indent = True
                # for i in range(3):
                #     if self.pos.peek_next() == ' ':
                #         self.current_char = self.pos.advance(self.current_char)
                #     else:
                #         indent = False
                #         break
                # if indent:
                #     tokens.append(Token(T_INDENT, self.pos))
                # else:
                pass
            elif self.current_char == '\n':
                tokens.append(Token(T_NEWLINE, self.pos))
            elif self.current_char == '"' or self.current_char == "'":
                tokens.append(self.make_string())
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier_keyword())
            elif self.current_char == '>':
                if self.pos.peek_next() == '>':
                    self.current_char = self.pos.advance(self.current_char)
                    self.skip_comment()
                elif self.pos.peek_next() == '=':
                    start_pos = self.pos.copy()
                    self.current_char = self.pos.advance(self.current_char)
                    tokens.append(Token(T_GREATER_EQUAL, start_pos, self.pos))
                else:
                    tokens.append(Token(T_GREATER_THAN, self.pos))
            elif self.current_char == '<':
                if self.pos.peek_next() == '=':
                    start_pos = self.pos.copy()
                    self.current_char = self.pos.advance(self.current_char)
                    tokens.append(Token(T_LESS_EQUAL, start_pos, self.pos))
                else:
                    tokens.append(Token(T_LESS_THAN, self.pos))
            elif self.current_char == '=':
                if self.pos.peek_next() == '=':
                    start_pos = self.pos.copy()
                    self.current_char = self.pos.advance(self.current_char)
                    tokens.append(Token(T_EQUAL_TO, start_pos, self.pos))
                else:
                    tokens.append(Token(T_ASSIGN, self.pos))
            elif self.current_char == '!':
                start_pos = self.pos.copy()
                if self.pos.peek_next() == '=':
                    self.current_char = self.pos.advance(self.current_char)
                    tokens.append(Token(T_NOT_EQUAL, start_pos, self.pos))
                else:
                    return [], IllegalCharError(start_pos, self.pos.copy(), "'" + self.current_char + "'")
            elif self.current_char == '+': tokens.append(Token(T_ADD, self.pos))
            elif self.current_char == '-': tokens.append(Token(T_SUBTRACT, self.pos))
            elif self.current_char == '*': tokens.append(Token(T_MULTIPLY, self.pos))
            elif self.current_char == '/': tokens.append(Token(T_DIVIDE, self.pos))
            elif self.current_char == '%': tokens.append(Token(T_MODULUS, self.pos))
            elif self.current_char == '(': tokens.append(Token(T_LEFT_PARENT, self.pos))
            elif self.current_char == ')': tokens.append(Token(T_RIGHT_PARENT, self.pos))
            elif self.current_char == '[': tokens.append(Token(T_LEFT_SQUARE, self.pos))
            elif self.current_char == ']': tokens.append(Token(T_RIGHT_SQUARE, self.pos))
            elif self.current_char == ',': tokens.append(Token(T_COMMA, self.pos))
            elif self.current_char == '.': tokens.append(Token(T_PERIOD, self.pos))
            elif self.current_char == '^': tokens.append(Token(T_EXPONENT, self.pos))
            else:
                start_pos = self.pos.copy()
                current_char = self.current_char
                self.current_char = self.pos.advance(self.current_char)
                return [], IllegalCharError(start_pos, self.pos.copy(), "'"+current_char+"'")

            if self.error:
                return [], self.error

            self.current_char = self.pos.advance(self.current_char) # automatically advances when token is made
        tokens.append(Token(T_EOF, self.pos))
        return tokens, None

    def skip_comment(self):
        self.current_char = self.pos.advance(self.current_char)
        while self.current_char != '\n' and self.current_char:
            self.current_char = self.pos.advance(self.current_char)

    def make_number(self):
        start_pos = self.pos.copy()
        point = False # check if it is a float
        value = self.current_char
        while self.pos.peek_next() in DIGITS or self.pos.peek_next() == '.':
            self.current_char = self.pos.advance(self.current_char)
            if self.current_char == '.':
                if point: # there is already a decimal point??
                    self.error = ExpectedCharError(start_pos, self.pos.copy(), "You can only have one decimal point in a decimal!")
                    return None
                else:
                    point = True
            value += self.current_char
        if self.pos.peek_next() in LETTERS:
            self.error = InvalidSyntaxError(start_pos, self.pos.copy(), "Identifiers can't start with digits")
            return None
        if self.current_char == '.':
            self.error = ExpectedCharError(start_pos, self.pos.copy(), "Expected digit after decimal point!")
            return None


        return Token(T_FLOAT, start_pos, self.pos, float(value)) if point else Token(T_INTEGER, start_pos, self.pos, int(value))

    def make_string(self):
        start_pos = self.pos.copy()
        value = ''
        stop_char = self.current_char
        while self.pos.peek_next() != stop_char:
            if self.pos.peek_next() == None:
                self.error = InvalidSyntaxError(start_pos, self.pos.copy(), "Unclosed string literal")
                return None
            self.current_char = self.pos.advance(self.current_char)
            value += self.current_char
        self.current_char = self.pos.advance(self.current_char)
        return Token(T_STRING, start_pos, self.pos, str(value))

    def make_identifier_keyword(self):
        start_pos = self.pos.copy()
        name = ''+self.current_char
        while self.pos.peek_next():
            if self.pos.peek_next() in LETTERS or self.pos.peek_next() in '_0123456789':
                self.current_char = self.pos.advance(self.current_char)
                name += self.current_char
            else:
                break

        token_type = T_KEYWORD if name in KEYWORDS.values() else T_IDENTIFIER
        return Token(token_type, start_pos, self.pos, str(name))


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
                node = result.register(self.expression())
                return result.success(node)
        node = result.register(self.expression())
        return result.success(node)

    def call(self):
        result = ParseResult()
        node = self.factor()
        if self.current_token.type == T_PERIOD: # Method call .name()
            start = self.current_token.start_pos.copy()
            self.advance()
            if self.current_token != T_IDENTIFIER:
                pass #ERROR
            name = self.current_token.value
            self.advance()
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

            end = self.current_token.end_pos.copy()  # Position of ')'
            self.advance()  # NOW advance past ')'

            return result.success(MethodCallNode(name, node, args, start, end))
        result.success(node)

    def factor(self): #
        result = ParseResult()
        token = self.current_token
        start = token.start_pos.copy()
        if self.current_token.type in (T_ADD, T_SUBTRACT): # unary operation
            op_token = token
            self.advance()
            right_node = result.register(self.factor()) # return a node
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
        result = self.bin_op(self.factor, [T_EXPONENT])
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
            return RTResult().success(String(self.value.upper()))
        #ERROR

    def method_lower_case(self, args): # makes lower case
        if len(args) == 1:
            pass
        if len(args) == 0:
            return RTResult().success(String(self.value.lower()))
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

    def methods(self):
        return {
            'get': self.method_get,
            'add': self.method_add,
            'remove': self.method_remove,
            'get_index': self.method_get_index,
            'clear': self.method_clear
        }

    def method_get(self, args):
        if len(args) != 1:
            pass # ERROR
        index = args[0]
        if index.value is not int:
            return None, "Can't access a list with a non-integer."
        if len(self.elements) <= index.value:
            return None, "Index out of range of list!"
        return self.elements[index.value], None

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
        return RTResult().success(self)

    def method_remove(self, args):
        if len(args) != 1:
            pass # ERROR
        index = args[0]
        self.elements.pop(index)
        return RTResult().success(self)

    def method_get_index(self, args): # finds first index of an element
        pass

    def method_clear(self, args):
        self.elements = []
        return RTResult().success(self)

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

#########IMPORTS########
import math

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
            if result.continue_:
                continue
            if logic.is_true(): # if true play if statement
                otherwise = False # don't need to play else statement
                body_res = result.register(self.visit(body, context))

        if node.else_case and otherwise:
            body_res = result.register(self.visit(node.else_case, context))
        return result.success(Number(0))

    def visit_WhileLoopNode(self, node, context):
        result = RTResult()
        while True:
            condition = node.condition_node
            logic = result.register(self.visit(condition, context))
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
        end = result.register(self.visit(node.end_val))
        # check they are integers
        if not(start.is_int() and end.is_int()):
            return result.failure(RTError(node.start, node.end, "Need integers to count", context))
        if node.increment_val: # there is an increment value
            increment = result.register(self.visit(node.increment_val))
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
            arg_value_result = self.visit(arg_node, context)
            if arg_value_result.error: return arg_value_result
            args.append(arg_value_result.value)
        # if is a function
        if isinstance(node.function_node, VarAccessNode):
            name = node.function_node.name
            function = context.get(name)
        else:
            function = result.register(self.visit(node.function_node, context))
        # if is a built in function
        if node.function_node.name in self.builtins:
            return self.builtins[node.function_node.name].execute(args)
        # if is a user defined function
        if isinstance(function, Function):
            return function.execute(args, self, context, RTResult())

            #return result.success(value if value is not None else Number(0))
        return result.failure(RTError(node.start, node.end, "Undefined identifier!", result))

    def visit_MethodCallNode(self, node, context):
        result = RTResult()
        obj = self.visit(node.object_node, context)

        if not hasattr(obj, "methods"):
            pass # ERROR
        methods = obj.methods()
        args = []
        if node.method_name not in methods:
            pass # ERROR
        for arg_node in node.arg_nodes:
            arg = self.visit(arg_node, context)
            args.append(arg)

        method = methods[node.method_name]
        return method(args)


    def visit_BreakNode(self, node, context):
        return RTResult().success_break()

    def visit_ContinueNode(self, node, context):
        return RTResult().success_continue()

    def visit_ReturnNode(self, node, context):
        result = RTResult()
        value = result.register(self.visit(node.return_node, context))
        return result.success_return(value)


########BUILT-IN FUNCTIONS################
class BuiltInFunction:
    def __init__(self, name):
        self.name = name

    def execute(self, args):
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
            pass
        elif self.name == 'float':
            pass
        elif self.name == 'string':
            pass
        elif self.name == 'length':
            if len(args) == 1 and isinstance(args[0], List):
                length = len(args[0].elements)
            else:
                length = len(args)
            return RTResult().success(Number(length))
        elif self.name == 'sqrt':
            if len(args) != 1:
                pass #ERROR
            return math.sqrt(args[0])
        elif self.name == 'min':
            lowest = 100000000000
            RTResult().success(Number(lowest))
        elif self.name == 'max':
            highest = 0

            return RTResult().success(Number(highest))
        elif self.name == 'sort':
            pass
        elif self.name == 'mean':
            total = 0
            list_ = []
            if len(args) == 1 and isinstance(args[0], List): # is a list
                list_ = args[0].elements
            else:
                list_ = args
            number = len(list_)
            for x in list_:
                total += x.value
            return RTResult().success(Number(total/number))
        elif self.name == 'median':
            pass
        elif self.name == 'mode':
            pass
        else:
            pass # ERROR


###########RUN##############
def run(file_name, file_text):
    lexer = Lexer(file_name, file_text)
    tokens, error = lexer.make_tokens()

    if error: return None, error # there is an error so stop the program
    parser = Parser(tokens)
    ast = parser.parse() # make an abstract syntax tree
    if ast.error: return None, ast.error # there is an error so stop the program (ParseResult object)

    interpreter = Interpreter()
    result = interpreter.visit(ast.node)

    if result.error: return None, result.error
    return result.value, result.error

############MAIN#############
if __name__ == '__main__':
    name = 'test_file.cool' # the name of the file your using goes here

    with open(name, 'r') as file:
        text = file.read()

    result, error = run(name, text)

    if error:
        print(error.as_string())
    else:
        print('\nProgram run successfully!')