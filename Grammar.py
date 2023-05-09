from Production import Production

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