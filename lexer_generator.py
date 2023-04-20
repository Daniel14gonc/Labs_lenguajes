from LexerDirector import LexerDirector
import sys

path = input('Ingrese el nombre del archivo.yal\n> ')
file = input ('Ingrese el nombre del archivo compilado\n> ')

if ".py" not in file:
    file += ".py"
if ".yal" not in path:
    path += ".yal"
# path = "ej5.yal"
# file = "ej5.py"
director = LexerDirector(path = path, file = file)
director.construct_lexer()