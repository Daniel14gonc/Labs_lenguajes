class SetOfItems(object):
    def __init__(self, grammar) -> None:
        self.heart = set()
        self.body = set()
        self.productions = set()
        self.grammar = grammar
        self.transition_symbols = set()

    def set_heart(self, productions):
        for production in productions:
            self.heart.add(production)

    def closure(self):
        productions = self.grammar.productions
        closure = {item for item in self.heart}
        self.stack = [item for item in self.heart]

        productions_visited = {item[0] for item in self.heart}

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
                            closure.add((production, -1))
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
    
    def goto(self, symbol, I):
        result = set()
        for element in I:
            result = self.add_production_goto(element, result, symbol)

        return result

    # TODO: revisar goto que no lo esta haciendo bien

    '''
        {frozenset({(expression' -> expression, -1)}): ['', '', frozenset({(expression' -> expression, 0), (expression -> expression PLUS term, 0)}), frozenset({(factor -> ID, 0)}), frozenset({(term -> factor, 0)}), frozenset({(expression -> term, 0), (term -> term TIMES factor, 0)}), '', frozenset({(factor -> LPAREN expression RPAREN, 0)})], frozenset({(expression' -> expression, 0), (expression -> expression PLUS term, 0)}): ['', '', '', '', '', '', '', ''], frozenset({(factor -> ID, 0)}): ['', '', '', '', '', '', '', ''], frozenset({(term -> factor, 0)}): ['', '', '', '', '', '', '', ''], frozenset({(expression -> term, 0), (term -> term TIMES factor, 0)}): ['', '', '', '', '', '', '', ''], frozenset({(factor -> LPAREN expression RPAREN, 0)}): ['', '', frozenset({(factor -> LPAREN expression RPAREN, 1), (expression -> expression PLUS term, 0)}), frozenset({(factor -> ID, 0)}), frozenset({(term -> factor, 0)}), frozenset({(expression -> term, 0), (term -> term TIMES factor, 0)}), '', ''], frozenset({(factor -> LPAREN expression RPAREN, 1), (expression -> expression PLUS term, 0)}): [frozenset({(expression -> expression PLUS term, 1)}), frozenset({(factor -> LPAREN expression RPAREN, 2)}), '', '', '', '', '', ''], frozenset({(expression -> expression PLUS term, 1)}): ['', '', '', '', '', '', '', ''], frozenset({(factor -> LPAREN expression RPAREN, 2)}): ['', '', '', '', '', '', '', '']}
    '''
        
