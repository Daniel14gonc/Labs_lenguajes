from LRAutomaton import LRAutomaton

class SLR(object):
    
    def __init__(self, grammar) -> None:
        self.grammar = grammar
        self.terminals = self.grammar.tokens
        self.non_terminals = self.grammar.non_terminals
        self.first_set = {}
        self.follow_set = {}

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

        print('Primero:', self.first_set)

    def calculate_follow(self):
        first_production = self.grammar.first_production
        head = first_production.head
        self.follow_set[head] = {'$'}
        productions = self.grammar.productions
        for production in productions:
            head = production.head
            self.follow(head)
        print('\nSiguiente:', self.follow_set)

    def build_LR_automaton(self):
        self.grammar.augument()
        self.automaton = LRAutomaton(self.grammar)
        self.automaton.build()
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

    # TODO: Pensar en donde ponerlo para que se enloope xd
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
                        # print(body[i + 1:], body, first)
                        self.follow_set[element] = self.follow_set[element].union(first)

                    if self.check_third_follow_rule(body, i):
                        follow = self.follow_set[A]
                        self.follow_set[element] = self.follow_set[element].union(follow)
                i += 1