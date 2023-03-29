from FA import FA
from DFA import DFA
from FAErrorChekcer import FAErrorChecker

class NFA(FA):

    def __init__(self, regex = None, count = 1) -> None:
        super().__init__(regex)
        self.count = count
        self.root = self.regex.get_root()
        self.build_afn()
        self.error_checker = FAErrorChecker()

    
    def build_afn(self):
        first, last = self.build_helper(self.root)
        self.initial_states.add(first)
        self.acceptance_states.add(last)

    def build_helper(self, node):
        if node:
            if node.value == '*':
                child = self.build_helper(node.left_child)
                return self.create_kleene(child)
            elif node.value == '+':
                child = self.build_helper(node.left_child)
                return self.create_positive_closure(child)
            elif node.value in '|.':
                left = self.build_helper(node.left_child)
                right = self.build_helper(node.right_child)
                if node.value == '|':
                    return self.create_or(left, right)
                else:
                    return self.create_concatenation(left, right)
            else:
                return self.create_unit(node)
    
    def create_positive_closure(self, child):
        first = self.count
        self.count += 1
        last = self.count
        self.count += 1

        self.build_matrix_entry(first)
        self.build_matrix_entry(last)

        self.create_transition(first, child[0], 'ε')
        self.create_transition(child[1], child[0], 'ε')
        self.create_transition(child[1], last, 'ε')

        return first, last


    def create_kleene(self, child):
        first = self.count
        self.count += 1
        last = self.count
        self.count += 1

        self.build_matrix_entry(first)
        self.build_matrix_entry(last)

        self.create_transition(first, child[0], 'ε')
        self.create_transition(first, last, 'ε')
        self.create_transition(child[1], child[0], 'ε')
        self.create_transition(child[1], last, 'ε')
        
        return first, last
    
    def create_or(self, left, right):
        first = self.count
        self.count += 1
        last = self.count
        self.count += 1

        self.build_matrix_entry(first)
        self.build_matrix_entry(last)

        self.create_transition(first, left[0], 'ε')
        self.create_transition(first, right[0], 'ε')
        self.create_transition(left[1], last, 'ε')
        self.create_transition(right[1], last, 'ε')

        return first, last

    def create_concatenation(self, left, right):
        self.replace_transitions(right[0], left[1])

        return left[0], right[1]
    
    def replace_transitions(self, old_state, new_state):
        new_state_transitions = self.transitions[new_state]
        
        for i in range(len(self.transitions[old_state])):
            new_state_transitions[i] = new_state_transitions[i].union(self.transitions[old_state][i])
        
        self.transitions.pop(old_state)

    def create_unit(self, node):
        symbol = node.value
        first = self.count
        self.count += 1
        last = self.count
        self.count += 1

        self.build_matrix_entry(first)
        self.build_matrix_entry(last)
        self.create_transition(first, last, symbol)

        return first, last

    def convert_to_DFA(self):
        dfa = DFA()
        dfa.build_from_NFA(self)
        
        return dfa
    
    def create_transition(self, initial_states, acceptance_states, symbol):
        symbol_index = self.get_symbol_index(symbol)
        self.transitions[initial_states][symbol_index].add(acceptance_states)

    def build_matrix_entry(self, state):
        entry = [set() for element in self.alphabet]
        self.transitions[state] = entry

    def simulate(self, string):
        # self.error_checker.check_alphabet_errors(string, self.alphabet)
        s = self.e_closure(self.initial_states)
        string = 'ε' if not string else string
        i = 0
        print(string)
        print(self.alphabet)
        while i < len(string):
            element = string[i]
            if element == '\\':
                element += string[i + 1]
                i += 1
            if element not in self.alphabet:
                return False
            if element != 'ε':
                s = self.e_closure(self.move(s, element))

            i += 1

        if s.intersection(self.acceptance_states):
            return True
        return False 
