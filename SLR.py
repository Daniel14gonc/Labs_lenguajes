from LRAutomaton import LRAutomaton
import pandas as pd
from termcolor import colored

class SLR(object):
    
    def __init__(self, grammar) -> None:
        self.grammar = grammar
        self.terminals = list(self.grammar.tokens)
        self.non_terminals = list(self.grammar.non_terminals)
        self.first_set = {}
        self.follow_set = {}
        self.actions_table = {}
        self.goto_table = {}
        self.ignore_tokens = []

    def calculate_first_and_follow(self):
        self.calculate_first()
        self.calculate_follow()

    def calculate_first(self):
        productions = self.grammar.productions
        for terminal in self.terminals:
            self.first(terminal)

        for production in productions:
            head = production.head
            if head not in self.first_set:
                self.first(head)

        # print('Primero:', self.first_set)

    def calculate_follow(self):
        first_production = self.grammar.first_production
        head = first_production.head
        self.follow_set[head] = {'$'}
        productions = self.grammar.productions
        for production in productions:
            head = production.head
            self.follow(head)
        # print('\nSiguiente:', self.follow_set, '\n')

    def build_LR_automaton(self):
        self.grammar.augument()
        self.automaton = LRAutomaton(self.grammar)
        self.automaton.build()
        self.transitions = self.automaton.transitions
        self.automaton.visualize()

    def add_first_symbol(self, X, symbol):
        if X not in self.first_set:
            self.first_set[X] = {symbol}
        else:
            self.first_set[X].add(symbol)
    

    def check_epsilon(self, X):
        productions = self.grammar.productions
        for production in productions:
            head, body = production.get_attributes()
            first_element = body[0]
            if head == X and len(body) == 1 and first_element == 'ε':
                return True
            
        return False
    
    def get_productions_by_head(self, X):
        productions_result = []
        productions = self.grammar.productions
        for production in productions:
            head = production.head
            if head == X:
                productions_result.append(production)
        
        return productions_result
    
    def add_first_set(self, X, other_first):
        self.first_set[X] = self.first_set[X].union(other_first)

    def first(self, X):
        if X not in self.first_set:
            self.first_set[X] = set()
        if X in self.terminals or X == 'ε':
            self.add_first_symbol(X, X)
        else:
            productions_by_head = self.get_productions_by_head(X)
            for production in productions_by_head:
                body = production.body
                i = 0
                previous_production_epsilon = True
                while i < len(body) and previous_production_epsilon:
                    element = body[i]
                    if element != X:
                        if element not in self.first_set:
                            self.first(element)
                        other_first = self.first_set[element]
                        self.add_first_set(X, other_first)
                    previous_production_epsilon = self.check_epsilon(element)
                    i += 1
                
                if previous_production_epsilon:
                    self.add_first_symbol(X, 'ε')
                    

            if self.check_epsilon(X):
                self.add_first_symbol(X, 'ε')

    def first_string(self, X_list):
        first = set()
        previous_first_epsilon = True
        i = 0
        while i < len(X_list) and previous_first_epsilon:
            element = X_list[i]
            first_of_element = self.first_set[element].copy()
            previous_first_epsilon = 'ε' in first_of_element
            if previous_first_epsilon:
                first_of_element.remove('ε')
            first = first.union(first_of_element)
            i += 1
        if previous_first_epsilon:
            first.add('ε')
        return first
    
    def check_third_follow_rule(self, body, i):
        if i + 1 < len(body):
            first = self.first_string(body[i + 1:])
            return 'ε' in first
        return True
    
    def follow(self, A):
        productions_by_head = self.get_productions_by_head(A)
        non_terminals = self.grammar.non_terminals
        for production in productions_by_head:
            head, body = production.get_attributes()
            i = 0
            while i < len(body):
                element = body[i]
                if element in non_terminals:
                    if element not in self.follow_set:
                        self.follow_set[element] = set()
                        self.follow(element)
                    if i < len(body) + 1:
                        first = self.first_string(body[i + 1:]).copy()
                        if 'ε' in first:
                            first.remove('ε')
                        self.follow_set[element] = self.follow_set[element].union(first)

                    if self.check_third_follow_rule(body, i):
                        follow = self.follow_set[A].copy()
                        follow = follow - {'ε'}
                        self.follow_set[element] = self.follow_set[element].union(follow)
                i += 1

    def add_acceptance_transition(self):
        self.acceptance_set_id = self.automaton.get_acceptance_transition()
        self.terminals_with_dollar = self.terminals.copy()
        self.terminals_with_dollar.append('$')
        self.add_entry(self.acceptance_set_id)
        self.actions_table[self.acceptance_set_id][-1] = 'acc'

    def add_entry(self, set_id):
        if set_id not in self.actions_table:
            self.actions_table[set_id] = ['' for _ in self.terminals_with_dollar]
        
        if set_id not in self.goto_table:
            self.goto_table[set_id] = ['' for _ in self.non_terminals]

        
    def add_shifts(self):
        transitions = self.automaton.get_transitions_with_grammar_symbols(self.terminals)
        for set_id in transitions:
            self.add_entry(set_id)
            shifts = transitions[set_id]
            i = 0
            for shift in shifts:
                if shift != '':
                    self.actions_table[set_id][i] = ('s', shift)
                i += 1

    def add_reduce(self):
        items = self.automaton.get_items()
        for item in items:
            state_id, state = item
            self.add_entry(state_id)
            for element in state:
                production = element[0]
                head = production.head
                dot_pointer = element[1]
                body_len = len(production.body)
                if body_len == dot_pointer + 1:
                    follow_for_head = self.follow_set[head]
                    production_index = self.grammar.index_of(production)
                    # print(head, follow_for_head, state_id)
                    for terminal in follow_for_head:
                        symbol_index = self.terminals_with_dollar.index(terminal)
                        if self.actions_table[state_id][symbol_index] != 'acc':
                            if self.actions_table[state_id][symbol_index] != '':
                                if self.actions_table[state_id][symbol_index][0] == 's':
                                    raise Exception('Error: Grammar has shift-reduction conflict.')
                                elif self.actions_table[state_id][symbol_index][0] == 'r':
                                    raise Exception('Error: Grammar has reduction-reduction conflict.')
                            self.actions_table[state_id][symbol_index] = ('r', production_index)

    def build_actions_table(self):
        self.add_acceptance_transition()
        self.add_shifts()
        self.add_reduce()
        # sorted_dict = dict(sorted(self.actions_table.items()))
        # df = pd.DataFrame.from_dict(sorted_dict, orient='index', columns=self.terminals_with_dollar)
        # print(df)

    def build_goto_table(self):
        transitions = self.automaton.get_transitions_with_grammar_symbols(self.non_terminals)
        for set_id in transitions:
            self.add_entry(set_id)
            gotos = transitions[set_id]
            i = 0
            for goto in gotos:
                if goto != '':
                    self.goto_table[set_id][i] = goto
                i += 1
        
        # sorted_dict = dict(sorted(self.goto_table.items()))
        # df = pd.DataFrame.from_dict(sorted_dict, orient='index', columns=self.non_terminals)
        # print(df)
    
    def build(self):
        self.calculate_first_and_follow()
        self.build_actions_table()
        self.build_goto_table()

    def initialize_parse(self):
        self.stack = []
        self.stack.append(0)
        self.symbol_stack = []
        self.latest_token = None
        self.errors = []
        self.error_empty_string = False

    def set_latest_token(self, token):
        self.latest_token = token
    
    def need_next_token(self):
        return self.latest_token == None
    
    def get_terminal_index(self, symbol):
        if symbol not in self.terminals_with_dollar:
            return None
        return self.terminals_with_dollar.index(symbol)
    
    def get_non_terminal_index(self, symbol):
        if symbol not in self.non_terminals:
            return None
        return self.non_terminals.index(symbol)
    
    def parse(self, lexer=None):
        self.accepted = False
        while lexer.has_next_token():
            if self.need_next_token():
                self.latest_token = lexer.next_token()
            self.parse_next()
        while len(self.stack) > 1 and not self.accepted and not self.error_empty_string:
            if self.latest_token == None:
                self.latest_token = '$'
            self.parse_next()
        
        lexer_errors = lexer.token_errors
        error_msg = ''
        if lexer_errors:
            error_msg += '\nLexical errors:\n'
            for error in lexer_errors:
                error_msg += error

        if self.errors:
            error_msg += '\nSyntax errors:\n'
            for error in self.errors:
                error_msg += error
        if error_msg != '':
            raise Exception(error_msg)
        
        if self.accepted:
            return colored("La cadena ha sido aceptada al parsearla.", "green")
        
        return colored("La cadena no ha sido aceptada al parsearla.", "red")

    def parse_next(self):
        symbol = self.latest_token.type if self.latest_token != '$' else self.latest_token
        if symbol != 'IGNORE' and symbol not in self.ignore_tokens:
            index = self.get_terminal_index(symbol)
            if index == None:
                if self.latest_token.type != 'ERROR':
                    self.errors.append(f'Error on token {colored(self.latest_token, "blue")} on line {self.latest_token.line} at position {self.latest_token.position}\n')
                self.latest_token = None
                return
            peek = self.stack[-1]
            action_entry = self.actions_table[peek][index]
            if action_entry == '':
                if self.latest_token != '$':
                    self.errors.append(f'Error on token {colored(self.latest_token, "blue")} on line {self.latest_token.line} at position {self.latest_token.position}\n')
                else:
                    self.errors.append(f'Error at end of file. Expression missing\n')
                    self.error_empty_string = True
                self.latest_token = None
                return
            self.execute_action(action_entry)
        else:
            self.latest_token = None

    def get_body_size(self, body):
        count = 0
        for element in body:
            if element != 'ε':
                count += 1

        return count
        
    def execute_action(self, action_entry):
        if len(action_entry) == 2:
            action, state = action_entry
            if action == 's':
                self.stack.append(state)
                symbol = '$'
                if self.latest_token != '$':
                    symbol = self.latest_token.type
                self.symbol_stack.append(symbol)
                self.latest_token = None
            elif action == 'r':
                production = self.grammar.get_production_by_index(state)
                head, body = production.get_attributes()
                elements_to_pop = self.get_body_size(body)
                if elements_to_pop > len(self.stack):
                    if self.latest_token != '$':
                        self.errors.append(f'Error on token {colored(self.latest_token, "blue")} on line {self.latest_token.line} at position {self.latest_token.position}\n')
                    else:
                        self.errors.append(f'Error at end of file. Expression missing\n')
                        self.error_empty_string = True
                    self.latest_token = None
                    return
                for _ in range(elements_to_pop):
                    self.symbol_stack.pop()
                    self.stack.pop()
                peek = self.stack[-1]
                head_index = self.get_non_terminal_index(head)
                new_state = self.goto_table[peek][head_index]
                self.symbol_stack.append(head)
                self.stack.append(new_state)
        elif action_entry == 'acc':
            self.accepted = True




        