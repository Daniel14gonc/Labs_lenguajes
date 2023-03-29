from Reader import YalexReader
from regex import Regex
from NFA import NFA
from Tokenizer import Tokenizer

class LexerBuilder(object):
    def __init__(self, path) -> None:
        self.path = path
    
    def read_lexer_file(self):
        self.reader = YalexReader(self.path)
        self.reader.read()
        self.regex = self.reader.regex

    def create_NFAS(self):
        self.NFAs = []
        self.count = 1
        for key in self.regex:
            regex = Regex(self.regex[key])
            nfa = NFA(regex, self.count)
            
            self.count = nfa.count
            self.NFAs.append(nfa)

    
    # TODO: Arreglar para poder almacenar que tokens van segun estado de aceptacion.
    #       Tomar en cuenta jerarquia.
    def create_tokenizer(self):
        tokenizer = Tokenizer()
        for nfa in self.NFAs:
            tokenizer.concatenate_FA(nfa)