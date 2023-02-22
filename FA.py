from AFVisual import AFVisual

class FA(object):
    def __init__(self, regex = None) -> None:
        self.regex = regex
        self.alphabet = regex.alphabet
        self.count = 1
        self.transitions = {}
        self.initial_states = set()
        self.acceptance_states = set()
    
    def create_AFvisual(self, path):
        self.visual_graph = AFVisual(path)