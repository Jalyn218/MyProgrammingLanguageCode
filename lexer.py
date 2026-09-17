DIGITS = '0123456789'
LETTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

##########IMPORTS#############
from errors import *

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