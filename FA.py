from AFVisual import AFVisual

class FA(object):
    def __init__(self, regex = None) -> None:
        if regex:
            self.regex = regex
            self.alphabet = regex.alphabet
        self.count = 1
        self.transitions = {}
        self.initial_states = set()
        self.acceptance_states = set()
        self.external_transitions = None
    
    def create_AFvisual(self, path):
        self.visual_graph = AFVisual(path)

    def get_symbol_index(self, symbol):
        for i in range(len(self.alphabet)):
            if self.alphabet[i] == symbol:
                return i
            
    def move(self, states, symbol):
        result = set()
        for state in states:
            index = self.get_symbol_index(symbol)
            transitions = self.external_transitions[state]
            states_reached = transitions[index]
            for element in states_reached:
                result.add(element)
        return result


    def e_closure(self, states):
        stack = []
        for state in states:
            stack.append(state)
        
        result = states

        while stack:
            t = stack.pop()
            transitions = self.external_transitions[t]
            index = self.get_symbol_index('ε')
            states_reached = transitions[index]
            for element in states_reached:
                if element not in result:
                    result.add(element)
                    stack.append(element)

        return result

    def output_image(self, path=None):
        if not path:
            path = "FA"
        self.create_AFvisual(path)
        self.visual_graph.set_AF(self)
        self.visual_graph.build_graph()