from SetOfItems import SetOfItems
import graphviz

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
        item.number = self.state_counter
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

    def build(self):
        items = SetOfItems(self.grammar)
        first_production = self.grammar.first_production

        items.set_heart([(first_production, -1)])
        state = items.heart.copy()
        self.create_state(state, items)

        self.pending_states = [state]

        while self.pending_states:
            state = self.pending_states.pop()
            items = self.items[frozenset(state)]
            closure = items.closure().copy()
            for symbol in self.grammar_symbols:
                new_state = items.goto(closure, symbol).copy()
                temp = frozenset(new_state)
                if len(new_state) > 0:
                    if temp not in self.states:
                        items = SetOfItems(self.grammar)
                        items.heart = new_state
                        self.create_state(new_state, items)
                        self.pending_states.append(new_state)
                    self.create_transition(state, new_state, symbol)

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
