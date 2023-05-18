from ParserDirector import ParserDirector
import sys

yapar = input('Ingrese el nombre del archivo yapar\n> ')
yalex = input('Ingrese el nombre del archivo yalex\n> ')
file = input('Ingrese el nombre del archivo compilado\n> ')

# if ".py" not in file:
#     file += ".py"
if ".yalp" not in yapar:
    yapar += ".yalp"
if ".yal" not in yalex:
    yalex += ".yal"
if ".py" not in file:
    file += ".py"

# yapar = './yapar/slr-6.yalp'
# yalex = './yalex/slr-2.yal'
director = ParserDirector(yapar = yapar, yalex = yalex, file = file)
director.construct_parser()