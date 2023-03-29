from NFA import NFA
from regex import Regex
import pandas as pd

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