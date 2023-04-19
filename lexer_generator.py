from LexerDirector import LexerDirector
import sys

args = sys.argv

path = None
file = None
if len(args) > 2: 
    path = args[1]
    file = args[2]

director = LexerDirector(path, file)
director.construct_lexer()