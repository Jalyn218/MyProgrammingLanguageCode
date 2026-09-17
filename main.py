###########IMPORTS##########
from interpreter import Interpreter
from lexer import Lexer
from parser import Parser

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