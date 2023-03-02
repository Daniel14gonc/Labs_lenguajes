from regex import Regex
from NFA import NFA

print('Disclaimer: Debe ingresar las expresiones regulares sin "." en la concatenación, el programa los agregará.')

# expression = input("> Ingrese la expresion regular sin '.' en la concatenación: ")

# regex = Regex('0 ? ( 1 ? ) ? 0 *')
regex = Regex('(a|b)*(abba*|(ab)*ba)')
nfa = NFA(regex)
nfa.output_image('NFA')
dfa = nfa.convert_to_DFA()
dfa.output_image('DFA')

print("Su regex es: ", regex.expression)
print("Su regex en postfix es: ", regex.to_postfix())
print("Puede encontrar el AFN visual de su regex en la carpeta de output.\n")

# regex = Regex('0 ? ( 1 ? ) ? 0 *')
# regex = Regex('(a|b*c?d*ef+)+')
# regex = Regex('a|b*')
# regex = Regex('a|b*c')
# regex = Regex('a+')
# regex = Regex('a|x*a*|e')
# regex = Regex(')(()++a')
# regex = Regex('(a|b)*abb')