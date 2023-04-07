from LexerDirector import LexerDirector
import sys

args = sys.argv

path = None
if len(args) > 1: 
    path = args[1]

director = LexerDirector(path)
director.construct_lexer()