from LRAutomaton import LRAutomaton

class SLR(object):
    
    def __init__(self, grammar) -> None:
        self.grammar = grammar
        self.terminals = self.grammar.tokens
        self.non_terminals = self.grammar.non_terminals
        self.first_set = {}
        self.next_set = {}

        self.calculate_first()
        print(self.first_set)
        
    def calculate_first(self):
        productions = self.grammar.productions
        for production in productions:
            head = production.head
            if head not in self.first_set:
                self.first(head)

    def build_LR_automaton(self):
        self.grammar.augument()
        self.automaton = LRAutomaton(self.grammar)
        self.automaton.build()
        self.automaton.visualize()

        self.first('expression')

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
        if X in self.terminals:
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

                for element in body:
                    if element not in self.first_set:
                        self.first(element)
                    

            if self.check_epsilon(X):
                self.add_first_symbol(X, 'ε')
    def next(self):
        pass