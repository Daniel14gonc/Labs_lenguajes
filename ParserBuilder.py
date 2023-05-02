from Formatter import YalexFormatter
from Reader import Reader
from Grammar import Grammar
from LRAutomaton import LRAutomaton
from YaparFormatter import YaparFormatter
from SLR import SLR

class ParserBuilder(object):
    
    def __init__(self, yapar, yalex) -> None:
        self.yalex_reader = Reader(yalex)
        self.yapar_reader = Reader(yapar)
        self.yalex_formatter = YalexFormatter()

    def get_token_names(self):
        yalex_content = self.yalex_reader.read()
        self.yalex_formatter.format_yalex_content(yalex_content)
        self.token_names = self.yalex_formatter.get_token_names()

    def read_yapar_file(self):
        self.yapar_content = self.yapar_reader.read()

    def convert_productions(self):
        self.yapar_formatter = YaparFormatter()
        self.yapar_formatter.format_yapar_content(self.yapar_content)
        self.productions = self.yapar_formatter.productions

    def create_LR_automaton(self):
        grammar = self.build_grammar()
        grammar.augument()
        automaton = LRAutomaton(grammar)
        automaton.build()
        automaton.visualize()
    
    def compare_tokens(self):
        yalex_tokens = set(self.token_names)
        yapar_tokens = set(self.tokens)
        return yalex_tokens == yapar_tokens
    
    def build_grammar(self):
        grammar = Grammar(self.productions)
        tokens = self.yapar_formatter.tokens
        grammar.split_grammar_elements(tokens)
        return grammar
    
    def build_SLR(self):
        grammar = self.build_grammar()
        self.slr = SLR(grammar)

    def build_LR_automaton(self):
        self.slr.build_LR_automaton()