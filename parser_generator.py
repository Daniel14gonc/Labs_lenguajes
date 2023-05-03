from ParserDirector import ParserDirector
import sys

# yapar = input('Ingrese el nombre del archivo yapar\n> ')
# yalex = input ('Ingrese el nombre del archivo yalex\n> ')
#file = input ('Ingrese el nombre del archivo compilado\n> ')

# if ".py" not in file:
#     file += ".py"
# if ".yalp" not in yapar:
#     yapar += ".yal"
# if ".yal" not in yalex:
#     yalex += ".yal"

yapar = './yapar/slr-4.yalp'
yalex = './yalex/slr-1.yal'
director = ParserDirector(yapar = yapar, yalex = yalex)
director.construct_parser()