from FA import FA
from ST import ST

class DFA(FA):

    def __init__(self, regex=None) -> None:
        super().__init__(regex)
        if regex:
            self.build_direct()

    def build_direct(self):
        count = 1
        tree = ST(self.regex)
        table = tree.get_followpos_table()
        first_state = frozenset(tree.root.first_pos)
        self.create_special_alphabet()
        states = {first_state: count}
        unmarked_states = [first_state]
        self.build_matrix_entry(count)
        count += 1
        pos_augmented = tree.get_last_pos()
        self.initial_states.add(states[first_state])
        if pos_augmented in first_state:
            self.acceptance_states.add(states[first_state])

        while unmarked_states:
            S = unmarked_states.pop()
            for symbol in self.special_alphabet:
                U = set()
                for state in S:
                    if (state, symbol) in table:
                        U = U.union(table[(state, symbol)])
                            
                U = frozenset(U)
                if U not in states:
                    states[U] = count
                    self.build_matrix_entry(count)
                    unmarked_states.append(U)
                    count += 1
                self.create_transition(states[S], states[U], symbol)
                if pos_augmented in U:
                    self.acceptance_states.add(states[U])

    def build_from_NFA(self, NFA):
        self.regex = NFA.regex
        self.alphabet = NFA.alphabet
        self.external_transitions = NFA.transitions
        self.create_special_alphabet()
        count_states = 1
        D_states = {}
        first_state = frozenset(self.e_closure(NFA.initial_states))
        D_states[first_state] = count_states
        self.build_matrix_entry(D_states[first_state])
        unmarked_states = [first_state]
        count_states += 1

        self.initial_states = {D_states[first_state]}
        

        while unmarked_states:
            T = unmarked_states.pop()
            self.check_special_state(T, NFA, D_states[T])
            for symbol in self.special_alphabet:
                U = frozenset(self.e_closure(self.move(T, symbol)))
                if U not in D_states:
                    D_states[U] = count_states
                    unmarked_states.append(U)
                    count_states += 1
            
                if D_states[U] not in self.transitions:
                    self.build_matrix_entry(D_states[U])
                self.create_transition(D_states[T], D_states[U], symbol) 
        self.alphabet = self.special_alphabet
        print(self.transitions)

    def check_special_state(self, state, NFA, representation):
        for element in state:
            if element in NFA.acceptance_states:
                self.acceptance_states.add(representation)
    
    def create_special_alphabet(self):
        self.special_alphabet = [element for element in self.alphabet]
        self.special_alphabet.remove('ε')

    def get_symbol_index_special(self, symbol):
         for i in range(len(self.special_alphabet)):
            if self.special_alphabet[i] == symbol:
                return i

    def create_transition(self, initial_states, acceptance_states, symbol):
        symbol_index = self.get_symbol_index_special(symbol)
        self.transitions[initial_states][symbol_index].add(acceptance_states)

    def build_matrix_entry(self, state):
        entry = [set() for element in self.special_alphabet]
        self.transitions[state] = entry