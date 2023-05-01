from SetOfItems import SetOfItems

class LRAutomaton(object):
    def __init__(self, grammar) -> None:
        self.states = []
        self.transitions = {}
        self.start_state = None
        self.grammar = grammar
        self.grammar_symbols = list(grammar.grammar_symbols)
        self.states = {}
        self.state_counter = 0
        self.items = {}
    
    def create_state(self, state, item):
        state = frozenset(state)
        self.states[state] = self.state_counter
        self.transitions[state] = ['' for _ in range(len(self.grammar_symbols))]
        self.items[state] = item
        self.state_counter += 1

    def create_transition(self, state, new_state, symbol):
        state = frozenset(state)
        new_state = frozenset(new_state)
        state_id = self.states[state]
        new_state_id = self.states[new_state]
        symbol_index = self.get_symbol_index(symbol)
        self.transitions[state][symbol_index] = new_state

    def get_symbol_index(self, symbol):
        return self.grammar_symbols.index(symbol)

    # TODO: Revisar la creacion de nuevos estados que no lo esta haciendo bien por lo de goto.
    def build(self):
        items = SetOfItems(self.grammar)
        first_production = self.grammar.first_production

        items.set_heart([(first_production, -1)])
        state = items.heart.copy()
        self.create_state(state, items)

        self.pending_states = [state]

        while self.pending_states:
            state = self.pending_states.pop()
            closure = items.closure().copy()
            for symbol in self.grammar_symbols:
                new_state = items.goto(symbol, closure).copy()
                temp = frozenset(new_state)
                if len(new_state) > 0:
                    if temp not in self.states:
                        items = SetOfItems(self.grammar)
                        items.heart = new_state
                        self.create_state(new_state, items)
                        self.pending_states.append(new_state)
                    self.create_transition(state, new_state, symbol)
        
        print(self.grammar_symbols, '\n\n', self.transitions)
