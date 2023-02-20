class AF(object):
    def __init__(self, regex = None) -> None:
        self.regex = regex
        self.alphabet = regex.alphabet
        self.count = 1
        self.transitions = {}
        self.initial = set()
        self.final = set()