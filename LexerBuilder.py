from Reader import YalexReader
from Formatter import YalexFormatter
from regex import Regex
from NFA import NFA
from Tokenizer import Tokenizer

class LexerBuilder(object):
    def __init__(self, path) -> None:
        self.path = path
    
    def read_lexer_file(self):
        self.reader = YalexReader(self.path)
        self.yalex_content = self.reader.read()
    
    def get_tokens_from_yalex(self):
        formatter = YalexFormatter()
        formatter.format_yalex_content(self.yalex_content)
        self.tokens = formatter.tokens

    def create_NFAS(self):
        self.NFAs = []
        self.count = 1
        for element in self.tokens:
            regex = element[0]
            action = element[1]
            print(regex)
            regex = Regex(regex)
            nfa = NFA(regex, self.count)
            
            self.count = nfa.count
            self.NFAs.append(nfa)

    
    # TODO: Arreglar para poder almacenar que tokens van segun estado de aceptacion.
    #       Tomar en cuenta jerarquia.
    def create_tokenizer(self):
        tokenizer = Tokenizer()
        for nfa in self.NFAs:
            tokenizer.concatenate_FA(nfa)
        # other = tokenizer.convert_to_DFA()
        # other.minimize()
        # other.output_image()
        # tokenizer.output_image()