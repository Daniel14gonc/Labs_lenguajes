import graphviz

class AFVisual(object):

    def __init__(self) -> None:
        self.visual_graph = graphviz.Digraph(format='png', graph_attr={'rankdir':'LR'})
        self.visual_graph.node('fake', style='invisible')
    
    def set_AF(self, AF):
        self.initial_states = AF.initial_states
        self.acceptance_states = AF.acceptance_states
        self.transitions = AF.transitions
        self.alphabet = AF.alphabet
        

    def build_graph(self):
        first = None
        for element in self.initial_states:
            first = element
        
        self.bfs(first)

        self.output_graph()

    def bfs(self, first):
        current_nodes = set()
        visited = set()
        queue = []
        queue.append(first)
        visited.add(first)

        while queue:
            state = queue.pop(0)
            self.visit(state, current_nodes)
            
            for transition in self.transitions[state]:
                if transition:
                    for element in transition:
                        if element not in visited:
                            queue.append(element)
                            visited.add(element)

    def visit(self, state, current_nodes):
        current_nodes.add(state)
        if state in self.acceptance_states:
            self.visual_graph.node(str(state), shape="doublecircle")
        elif state in self.initial_states:
            self.visual_graph.edge("fake", str(state), style="bold")
            self.visual_graph.node(str(state), root="true")
        else:
            self.visual_graph.node(str(state))

        transitions = self.transitions[state]
        i = 0
        for set in transitions:
            if set:
                for element in set:
                    if element not in current_nodes:
                        self.visual_graph.node(str(element))
                        current_nodes.add(element)
                    
                    self.visual_graph.edge(str(state), str(element), label=str(self.alphabet[i]))
            i += 1       

    def output_graph(self):
        self.visual_graph.render(directory='output', view=True)