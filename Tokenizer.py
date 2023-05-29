from NFA import NFA
from regex import Regex
import pandas as pd
import re
from Reader import Reader
from TokenLex import TokenLex
from termcolor import colored

# Función para convertir sets a listas
def set_to_tuple(val):
    if isinstance(val, set):
        return tuple(val)
    else:
        return val
    
def tuple_to_set(val):
    if isinstance(val, tuple):
        return set(val)
    else:
        return val

def replace_empty(val):
    if val == '':
        return tuple()
    else:
        return val

class Tokenizer(NFA):
    
    def __init__(self, regex=None, count=1) -> None:
        temp_regex = Regex('a')
        super().__init__(temp_regex, 0)
        self.transitions = {}
        self.initial_states.add(0)
        self.alphabet = ['ε']
        self.build_matrix_entry(0)
        self.acceptance_states = set()
        self.tokens = {}

    def concatenate_FA(self, FA):
        other_alphabet = FA.alphabet.copy()
        other_transitions = FA.transitions.copy()
        other_acceptance_states = FA.acceptance_states.copy()
        self.acceptance_states = self.acceptance_states.union(other_acceptance_states)
        other_initial_states = FA.initial_states
        self.create_initial_transition(other_initial_states)
        self.merge_transitions(other_transitions, other_alphabet)

    def create_initial_transition(self, initial_states):
        initial = list(initial_states)[0]
        self.create_transition(0, initial, 'ε')

    def build_extra_columns(self, df, other_alphabet, common_keys):
        missing_keys = set(other_alphabet) - set(common_keys)
        if missing_keys:
            for key in missing_keys:
                df[key] = ''

    def merge_transitions(self, new_table, new_alphabet):
        common_keys = list(set(new_alphabet).intersection(set(self.alphabet)))

        other_table = pd.DataFrame.from_dict(new_table, orient = 'index', columns=new_alphabet)
        other_table = other_table.applymap(set_to_tuple)
        self.build_extra_columns(other_table, self.alphabet, common_keys)
        table = pd.DataFrame.from_dict(self.transitions, orient = 'index', columns=self.alphabet)
        table = table.applymap(set_to_tuple)
        self.build_extra_columns(table, new_alphabet, common_keys)

        other_table = other_table.applymap(replace_empty)
        table = table.applymap(replace_empty)

        merged = pd.concat([table, other_table])
        merged = merged.applymap(tuple_to_set)
        self.alphabet = list(merged.columns)
        self.transitions = merged.apply(lambda row: row.tolist(), axis=1).to_dict()

    def edit_meta_alphabet(self):
        list = ["\\+", "\\.", "\\*", "\\(", "\\)"]
        new_alphabet = []
        for element in self.alphabet:
            if "\\" in element and element not in list:
                new_element = element[1]
                new_element = '\\' + new_element
                escape = new_element.encode().decode('unicode_escape')
                new_alphabet.append(escape)
            else:
                new_alphabet.append(element)
        self.alphabet = new_alphabet

    def set_actions(self, actions):
        self.actions = actions

    def begin_simulation(self):
        self.accepted_states = set()
        self.s = self.e_closure(self.initial_states)

    def simulate_symbol(self, symbol):
        symbol = 'ε' if not symbol else symbol
        self._next_transition(symbol)
    
    def is_accepted(self):
        self.accepted_states = self.s.intersection(self.acceptance_states)
        if self.accepted_states:
            return True
        
        return False

    def get_token(self):
        tokens = []
        for state in self.accepted_states:
            for key in self.actions:
                if state in key:
                    tokens.append(self.actions[key])

        min = float('inf')
        max_token = None
        for token in tokens:
            if token[0] < min:
                min = token[0]
                max_token = token[1]
        
        return max_token

    def has_transitions(self):
        for state in self.s:
            transitions = self.transitions[state]
            for resultant_state in transitions:
                if resultant_state != set():
                    return True
        
        return False


    def _next_transition(self, symbol):
        element = symbol
        if element not in self.alphabet:
            self.s = set()
        if element != 'ε':
            self.s = self.e_closure(self.move(self.s, element))

    def read_source_code(self, filename):
        self.source_code = Reader(filename).read()
    
    def initialize_token_recognition(self):
        self.initial = 0
        self.advance = 0
        self.latest_token = None
        self.line = 1
        self.line_pos = -1
        self.errors = []
        self.tokens = []
        self.token_errors = []
    
    def has_next_token(self):
        return self.initial < len(self.source_code)
    
    def get_new_token(self, content, line, position, value):
        content = content.replace('return', '')
        content = content.replace('RETURN', '')
        content = content.replace("'", '')
        content = content.replace('"', '')
        content = content.strip()
        if content == '':
            content = 'IGNORE'
        return TokenLex(content, line, position, value)


    def next_token(self):
        self.advance = self.initial
        self.begin_simulation()
        longest_lexeme = False
        self.latest_token = None
        acu = ""
        count = 0
        has_transitions = True
        count = -1
        line_count = 0
        latest_pos = self.initial
        token = None
        while has_transitions and self.advance < len(self.source_code):
            symbol = self.source_code[self.advance]
            acu += symbol
            self.simulate_symbol(symbol)
            accepted = self.is_accepted()
            has_transitions = self.has_transitions()
            longest_lexeme = accepted
            if longest_lexeme:
                self.latest_token = self.get_token()
                count = 0
                line_count = 0
                latest_pos = self.advance + 1
            else:
                count += 1
                if symbol == '\n':
                    line_count += 1

            self.advance += 1
            self.line_pos += 1
            if symbol == '\n':
                if line_count == 0:
                    self.line += 1
                    self.line_pos = -1

        self.line_pos -= count
        acu = acu[:-1]
        if self.latest_token != None:
            token = self.get_new_token(self.latest_token, self.line, self.line_pos, acu)
        else:
            latest_pos = self.advance
            self.token_errors.append(f"Lexical error on line {self.line} at position {self.line_pos}, element {colored(acu, 'green')}\n")
            token = self.get_new_token('ERROR', self.line, self.line_pos, acu)
        self.initial = latest_pos

        return token