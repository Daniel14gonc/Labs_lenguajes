class SetOfItems(object):
    def __init__(self, grammar) -> None:
        self.heart = set()
        self.body = set()
        self.productions = set()
        self.grammar = grammar
        self.transition_symbols = set()
        self.number = 0

    def set_heart(self, productions):
        for production in productions:
            self.heart.add(production)
    
    # TODO: revisar añadir producciones visitadas
    def closure(self):
        productions = self.grammar.productions
        closure = {item for item in self.heart}
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
        body = closure - self.heart
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
        
