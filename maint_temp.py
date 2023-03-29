from regex import Regex
from NFA import NFA
from DFA import DFA

reg = Regex('ab')

print(reg.alphabet)
res = reg.to_postfix()
nfa = NFA(reg)
nfa.output_image('prueba')
reg = Regex('ab\+')
print(reg.to_postfix())
dfa = DFA(reg)
dfa.output_image('prueba2')