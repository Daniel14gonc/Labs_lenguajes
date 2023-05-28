class Production(object):
    def __init__(self, head, body) -> None:
        self.head = head
        self.body = body

    def get_attributes(self):
        return self.head, self.body
    
    def __repr__(self) -> str:
        return self.head + " -> " + " ".join(element for element in self.body)


class Grammar(object):
    
    def __init__(self, productions) -> None:
        i = 0
        self.productions = []
        self.first_production = None
        self.heads = set()
        self.grammar_symbols = []
        while i < len(productions):
            head, body = productions[i]
            self.heads.add(head)
            production = Production(head, body)
            if i == 0:
                self.first_production = production
            self.productions.append(production)
            i += 1
        self.create_grammar_symbols()

    def create_grammar_symbols(self):
        for production in self.productions:
            head, body = production.get_attributes()
            self.grammar_symbols.append(head)
            for symbol in body:
                if symbol != 'ε':
                    self.grammar_symbols.append(symbol)

    def split_grammar_elements(self, tokens):
        self.tokens = tokens
        self.non_terminals = set(self.grammar_symbols) - set(self.tokens)

    def index_of(self, production):
        if production in self.productions:
            return self.productions.index(production)
        return None
    
    def get_production_by_index(self, index):
        if index >= len(self.productions) or index < 0:
            return None
        return self.productions[index]

    def augument(self):
        head, _ = self.first_production.get_attributes()
        new_head = head + "'"
        if new_head in self.heads:
            new_head = head + '@'
        self.non_terminals.add(new_head)
        first_prod = Production(new_head, [head])
        self.productions.insert(0, first_prod)
        self.old_first_production = self.first_production
        self.first_production = first_prod
class SetOfItems(object):
    def __init__(self, grammar) -> None:
        self.heart = []
        self.body = set()
        self.productions = set()
        self.grammar = grammar
        self.transition_symbols = set()
        self.number = 0

    def set_heart(self, productions):
        for production in productions:
            self.heart.append(production)
    
    # TODO: revisar añadir producciones visitadas
    def closure(self):
        productions = self.grammar.productions
        closure = [item for item in self.heart]
        self.stack = [item for item in self.heart]
        
        productions_visited = set()

        while self.stack:
            item = self.stack.pop()
            production = item[0]
            dot_pos = item[1]
            body = production.body
            if len(body) > dot_pos + 1:
                next_element = body[dot_pos + 1]
                for production in productions:
                    if production not in productions_visited:
                        head = production.head
                        if head == next_element:
                            if production.body[0] == 'ε':
                                closure.append((production, 0))
                                self.stack.append((production, 0))
                            else:
                                closure.append((production, -1))
                                self.stack.append((production, -1))
                            productions_visited.add(production)
        return closure

    def add_symbol(self, item):
        production = item[0]
        dot_pos = item[1]
        body = production.body
        if len(body) > dot_pos + 1:
            transition_symbol = body[dot_pos + 1]
            self.transition_symbols.add(transition_symbol)
    
    def get_possible_transitions(self):
        for item in self.heart:
            self.add_symbol(item)

        for item in self.body:
            self.add_symbol(item)
        
        return self.transition_symbols
    
    def add_production_goto(self, item, result, symbol):
        production = item[0]
        production_pos = item[1]
        body = production.body
        if len(body) > production_pos + 1:
            if body[production_pos + 1] == symbol:
                result.add((production, production_pos + 1))
        return result
    
    def goto(self, I, symbol):
        result = set()
        for element in I:
            result = self.add_production_goto(element, result, symbol)

        return result
    
    def add_dot(self, body, dot_pos):
        acu = ""
        for i in range(len(body)):
            element = body[i]
            if i == dot_pos:
                acu += "•" + element + " "
            else:
                acu += element + " "
        acu = acu[:-1]
        if dot_pos == len(body):
            acu += "•"
        return acu
    
    def __repr__(self) -> str:
        closure = self.closure()
        body = set(closure) - set(self.heart)
        res = "I" + str(self.number)
        res += "\nHeart\n"

        for item in list(self.heart):
            production = item[0]
            dot_pos = item[1] + 1
            head, body_prod = production.get_attributes()
            acu = head + " => " + self.add_dot(body_prod, dot_pos)
            res += acu + '\n'
        if len(body) > 0:
            res += "\nBody\n"
            for item in list(body):
                production = item[0]
                dot_pos = item[1] + 1
                head, body_prod = production.get_attributes()
                acu = head + " => " + self.add_dot(body_prod, dot_pos)
                res += acu + '\n'
        res = res[:-1]
        
        return res
        


import graphviz

class LRAutomaton(object):
    def __init__(self, grammar) -> None:
        self.states = set()
        self.transitions = {}
        self.start_state = None
        self.grammar = grammar
        self.grammar_symbols = list(grammar.grammar_symbols)
        self.state_counter = 0
        self.items = {}

    def get_state_id(self, state):
        return self.items[state].number
    
    def create_state(self, state, item):
        state = frozenset(state)
        self.states.add(state)
        self.transitions[state] = ['' for _ in range(len(self.grammar_symbols))]
        self.items[state] = item
        item.number = self.state_counter
        self.state_counter += 1

    def create_transition(self, state, new_state, symbol):
        state = frozenset(state)
        new_state = frozenset(new_state)
        # state_id = self.states[state]
        # new_state_id = self.states[new_state]
        symbol_index = self.get_symbol_index(symbol)
        self.transitions[state][symbol_index] = new_state

    def get_symbol_index(self, symbol):
        if symbol in self.grammar_symbols:
            return self.grammar_symbols.index(symbol)
        return None

    # TODO: tengo que tener un diccionario con los indices asociados a los items para luego usar en la pila (ejemplo de Carlos).
    def build(self):
        items = SetOfItems(self.grammar)
        first_production = self.grammar.first_production

        items.set_heart([(first_production, -1)])
        state = items.heart.copy()
        self.create_state(state, items)

        self.first_state = state

        self.pending_states = [state]

        while self.pending_states:
            state = self.pending_states.pop(0)
            items = self.items[frozenset(state)]
            closure = items.closure().copy()
            for symbol in self.grammar_symbols:
                new_state = items.goto(closure, symbol).copy()
                temp = frozenset(new_state)
                if len(new_state) > 0:
                    if temp not in self.transitions:
                        items = SetOfItems(self.grammar)
                        items.heart = new_state
                        self.create_state(new_state, items)
                        self.pending_states.append(new_state)
                    self.create_transition(state, new_state, symbol)

    def get_items(self):
        response = []
        for key in self.items:
            item = self.items[key]
            state_id = self.get_state_id(key)
            response.append((state_id, item.closure()))

        return response
    
    def visualize(self):
        self.visual_graph = graphviz.Digraph(format='png', graph_attr={'rankdir':'LR'}, name="LRAutomaton")
        self.visual_graph.node('fake', style='invisible')
        initial_prod = self.grammar.first_production
        initial_prod = [(initial_prod, -1)]
        self.initial_prod = frozenset(initial_prod)
        initial_item = self.items[self.initial_prod]
        self.bfs(initial_item.heart)
        self.output_graph()

    def bfs(self, first):
        first = frozenset(first)
        current_nodes = set()
        visited = set()
        queue = []
        queue.append(first)
        visited.add(first)

        while queue:
            state = queue.pop(0)
            self.visit(state, current_nodes)
            
            for transition in self.transitions[state]:
                if transition and transition != '':
                    if transition not in visited:
                        queue.append(transition)
                        visited.add(transition)

    def visit(self, state, current_nodes):
        current_nodes.add(state)
        item = self.items[state]
        if state == self.initial_prod:
            self.visual_graph.edge("fake", str(item), style="bold")
            self.visual_graph.node(str(item), root="true", shape="rectangle")
        else:
            self.visual_graph.node(str(item), shape="rectangle")

        transitions = self.transitions[state]
        i = 0
        for set in transitions:
            if set:
                item_receiver = self.items[set]
                if set not in current_nodes:
                    self.visual_graph.node(str(item_receiver), shape="rectangle")
                    current_nodes.add(set)
                
                self.visual_graph.edge(str(item), str(item_receiver), label=str(self.grammar_symbols[i]))
            i += 1       

    def output_graph(self):
        self.visual_graph.render(directory='output', view=False)

    def get_acceptance_transition(self):
        old_initial_head = self.grammar.old_first_production.head
        index = self.get_symbol_index(old_initial_head)
        target_state = self.transitions[frozenset(self.first_state)][index]
        return self.items[target_state].number

    def get_transitions_with_grammar_symbols(self, symbols):
        resultant_transitions = {}
        i = 0
        for symbol in symbols:
            index = self.get_symbol_index(symbol)
            if index != None:
                for state in self.transitions:
                    transition = self.transitions[state][index]
                    if transition != '':
                        origin_set_id = self.items[state].number
                        target_set_id = self.items[transition].number
                        if origin_set_id not in resultant_transitions:
                            resultant_transitions[origin_set_id] = ['' for _ in symbols]
                        
                        resultant_transitions[origin_set_id][i] = target_set_id
            i += 1
        
        return resultant_transitions

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
        
        return "La cadena no ha sido aceptada al parsearla."

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




        
productions = [('expression', ['expression', 'PLUS', 'term']), ('expression', ['term']), ('term', ['term', 'TIMES', 'factor']), ('term', ['factor']), ('factor', ['LPAREN', 'expression', 'RPAREN']), ('factor', ['ID'])]
tokens = ['ID', 'PLUS', 'TIMES', 'LPAREN', 'RPAREN']
ignore_tokens = ['WS']
grammar = Grammar(productions)
grammar.split_grammar_elements(tokens)
slr = SLR(grammar)
slr.build_LR_automaton()
slr.build()
slr.ignore_tokens = ignore_tokens
slr.initialize_parse()
