from regex import Regex
from NFA import NFA
from DFA import DFA


def input_handler():
    expression = input('Ingrese expresión regular que desea evaluar> ')
    regex = Regex(expression)
    string = input('Ingrese la cadena que desea evaluar> ')
    nfa = NFA(regex)
    result = "aceptada" if nfa.simulate(string) else "rechazada"
    print("La expresión", string, "ha sido", result, "por el AFN.")
    nfa.output_image("NFA")
    nfa.create_table("NFA")
    
    dfa = nfa.convert_to_DFA()
    result = "aceptada" if dfa.simulate(string) else "rechazada"
    print("La expresión", string, "ha sido", result, "por el AFD a partir del AFN.")
    dfa.output_image('DFA_from_NFA')
    dfa.create_table("DFA_from_NFA")

    dfa_direct = DFA(regex)
    result = "aceptada" if dfa_direct.simulate(string) else "rechazada"
    print("La expresión", string, "ha sido", result, "por el AFD directo.")
    dfa_direct.output_image('DFA_direct')
    dfa_direct.create_table("DFA_direct")

    dfa.minimize()
    result = "aceptada" if dfa.simulate(string) else "rechazada"
    print("La expresión", string, "ha sido", result, "por el AFD a partir de AFN minimizado.")
    dfa.output_image('DFA_from_NFA_min')
    dfa.create_table("DFA_from_NFA_min")

    dfa_direct.minimize()
    result = "aceptada" if dfa_direct.simulate(string) else "rechazada"
    print("La expresión", string, "ha sido", result, "por el AFD directo minimizado.")
    dfa_direct.output_image('DFA_direct_min')
    dfa_direct.create_table("DFA_direct_min")

    print('Los diagramas los puede encontrar en la carpeta output.')
    print('Las tablas las puede encontrar en la carpeta tables.\n')


print('Disclaimer: Debe ingresar las expresiones regulares sin "." en la concatenación, el programa los agregará.')

# string = input("> Ingrese la expresion regular sin '.' en la concatenación: ")

# regex = Regex('0 ? ( 1 ? ) ? 0 +')

while True:
    try:
        input_handler()

    except ValueError as e:
        print(e)
