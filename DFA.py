from FA import FA
from ST import ST
from FAErrorChecker import FAErrorChecker

class DFA(FA):

    def __init__(self, regex = None, count = 1) -> None:
        super().__init__(regex)
        self.dead_state = None
        self.temp_transitions = None
        if regex:
            self.build_direct(count)

        self.error_checker = FAErrorChecker()

    def build_direct(self, counter):
        self.count = counter
        tree = ST(self.regex)
        table = tree.get_followpos_table()
        first_state = frozenset(tree.root.first_pos)
        self.create_special_alphabet()
        states = {first_state: self.count}
        unmarked_states = [first_state]
        self.build_matrix_entry(self.count)
        self.count += 1
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
                    states[U] = self.count
                    if not U:
                        self.dead_state = self.count
                    self.build_matrix_entry(self.count)
                    unmarked_states.append(U)
                    self.count += 1
                self.create_transition(states[S], states[U], symbol)
                if pos_augmented in U:
                    self.acceptance_states.add(states[U])

        self.alphabet = self.special_alphabet
        print(self.alphabet)
        self.temp_transitions = self.transitions
        self.delete_dead_state()
        self.set_external_transitions(self.transitions)

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
                    if not U:
                        self.dead_state = count_states
                    unmarked_states.append(U)
                    count_states += 1
            
                if D_states[U] not in self.transitions:
                    self.build_matrix_entry(D_states[U])
                self.create_transition(D_states[T], D_states[U], symbol) 
        self.alphabet = self.special_alphabet
        self.temp_transitions = self.transitions
        self.delete_dead_state()
        self.set_external_transitions(self.transitions)

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

    def delete_dead_state(self):
        transitions = self.transitions.copy()
        for transition in self.transitions:
            if transition == self.dead_state:
                transitions.pop(transition)
            else:
                new_element = []
                for element in self.transitions[transition]:
                    if self.dead_state in element:
                        new_element.append(set())
                    else:
                        new_element.append(element)
                transitions[transition] = new_element
        
        self.transitions = transitions
    
    def get_initial_partition(self):
        states = self.get_states(self.temp_transitions)
        acceptance = frozenset({state for state in states if state in self.acceptance_states})
        non_acceptance = frozenset(states - acceptance)
        partition = {acceptance, non_acceptance}
        return partition

    def get_group(self, element, groups, symbol):
        index = self.get_symbol_index_special(symbol)
        transition = list(self.temp_transitions[element][index])[0]
        for group in groups:
            if transition in group:
                return list(group)
            
    def check_equal(self, tag):
        last = tag[0]
        for element in tag:
            if element != last:
                return False
            last = element
        
        return True

    def create_partition(self, group, group_tag):
        group_dict_helper = {}
        for i in range(len(group_tag)):
            tag = tuple(group_tag[i])
            element = group[i]
            if tag in group_dict_helper:
                group_dict_helper[tag].add(element)
            else:
                group_dict_helper[tag] = {element}

        new_partition = set()
        for key in group_dict_helper:
            new_partition.add(frozenset(group_dict_helper[key]))

        return new_partition

    def create_new_partition(self, group, partition):
        groups = list(partition)
        group_list = list(group)
        for symbol in self.alphabet:
            group_tag = []
            for element in group_list:
                group_tag.append(self.get_group(element, groups, symbol))
            if not self.check_equal(group_tag):
                return self.create_partition(group_list, group_tag)
           
        return {group}
                
    def representatives(self, partition):
        table = {}
        representatives = []
        initial = list(self.initial_states)[0]
        for element in partition:
            if element:
                representative = None
                if self.dead_state in element:
                    representative = self.dead_state
                if initial in element:
                    representative = initial
                else:
                    representative = list(element)[0]
                table[element] = representative
                representatives.append(representative)

        return representatives, table

    def get_transition_representative(self, element, table):
        element = list(element)[0]
        for key in table:
            if element in key:
                return table[key]

    def build_new_transitions(self, partition):
        representatives, table = self.representatives(partition)
        transitions = {}
        for element in representatives:
            if element not in transitions:
                transitions[element] = [set() for element in self.alphabet]
            for symbol in self.alphabet:
                index = self.get_symbol_index(symbol)
                state = self.temp_transitions[element][index]
                transition_representative = self.get_transition_representative(state, table)
                transitions[element][index].add(transition_representative)

        self.transitions = transitions


    def minimize(self):
        partition = self.get_initial_partition()
        final_partition = self.hopcroft(partition)
        self.build_new_transitions(final_partition)
        self.delete_dead_state()
        self.set_external_transitions(self.transitions)


    def hopcroft(self, partition):
        partition_new = list(partition.copy())
        for group in partition:
            if group:
                new_group = self.create_new_partition(group, partition)
                partition_new.remove(group)
                for element in new_group:
                    partition_new.append(element)
        
        partition_new = set(partition_new)
        
        if partition_new == partition:
            return partition
        else:
            return self.hopcroft(partition_new)
    
    def get_states_with_symbol(self, states, symbol):
        index = self.get_symbol_index(symbol)
        result = set()
        for element in states:
            for state in self.transitions:
                if element in self.transitions[state][index]:
                    result.add(state)
        
        return result

    def get_states(self, transitions):
        return {state for state in transitions}
    
    def simulate(self, string):
        # self.error_checker.check_alphabet_errors(string, self.alphabet)
        s = self.initial_states
        string = 'ε' if not string else string
        for element in string:
            if element not in self.alphabet:
                return False
            if element != 'ε':
                s = self.move(s, element)
            
        if s.intersection(self.acceptance_states):
            return True
        return False 