from Formatter import YalexFormatter
from Reader import Reader
from Grammar import Grammar
from YaparFormatter import YaparFormatter
from SLR import SLR
import pickle

class ParserBuilder(object):
    
    def __init__(self, yapar, yalex, file) -> None:
        self.yalex_reader = Reader(yalex)
        self.yapar_reader = Reader(yapar)
        self.yalex_formatter = YalexFormatter()
        self.file = file

    def get_token_names(self):
        yalex_content = self.yalex_reader.read()
        self.yalex_errors = self.yalex_formatter.format_yalex_content(yalex_content)
        self.token_names = self.yalex_formatter.get_token_names()

    def read_yapar_file(self):
        self.yapar_content = self.yapar_reader.read()
    
    def format_yapar(self):
        self.yapar_formatter = YaparFormatter()
        self.yapar_formatter.format_yapar_content(self.yapar_content)

    def convert_productions(self):
        self.productions = self.yapar_formatter.productions
    
    def check_errors(self):
        errors = ''
        if len(self.yalex_errors) > 0:
            errors += '\nYalex errors:\n'
            for error in self.yalex_errors:
                errors += error
        
        self.yapar_errors = self.yapar_formatter.errors
        if len(self.yapar_errors) > 0:
            errors += '\nYapar errors:\n'
            for error in self.yapar_errors:
                errors += error
        
        self.tokens = self.yapar_formatter.tokens
        token_errors = self.compare_tokens()
        if len(token_errors) > 0:
            errors += token_errors
        
        if len(errors) > 0:
            raise Exception(errors)
        
    
    def compare_tokens(self):
        yalex_tokens = set(self.token_names)
        ignore_tokens = set(self.yapar_formatter.get_tokens_to_ignore())
        yapar_tokens = set(self.tokens).union(ignore_tokens)
        
        difference_yalex = yalex_tokens - yapar_tokens
        difference_yapar = yapar_tokens - yalex_tokens
        error = ''
        if len(difference_yalex) > 0 or len(difference_yapar) > 0:
            error += '\nErrors in tokens from Yalex and Yapar:\n'
        
        if len(difference_yalex) > 0:
            error += f'Error: Yalex tokens {str(difference_yalex)} not present in Yapar.\n'
        
        if len(difference_yapar) > 0:
            error += f'Error: Yapar tokens {str(difference_yapar)} not present in Yalex.\n'

        return error
    
    def first_and_follow(self):
        self.slr.calculate_first_and_follow()
    
    def build_grammar(self):
        grammar = Grammar(self.productions)
        tokens = self.yapar_formatter.tokens
        grammar.split_grammar_elements(tokens)
        return grammar
    
    def create_SLR(self):
        grammar = self.build_grammar()
        self.slr = SLR(grammar)

    def build_LR_automaton(self):
        self.slr.build_LR_automaton()
    
    def build_SLR(self):
        self.slr.build()

    def parse(self):
        self.slr.initialize_parse()
        self.slr.parse()

    def concat_files_needed(self):
        files = ["Production", "Grammar", "SetOfItems", "LRAutomaton", "SLR"]
        imports = ["from LRAutomaton import LRAutomaton", "from YaparErrorChecker import YaparErrorChecker", "from YalexErrorChecker import YalexErrorChecker", "from SetOfItems import SetOfItems", "from Production import Production"]
        self.file_content = []
        
        for file in files:
            with open(file + ".py", "rt") as archivo:
                contenido = archivo.read()
                for element in imports:
                    contenido = contenido.replace(element, '')
                self.file_content.append(contenido)
    
    def add_functionality(self):
        productions = f"productions = {self.productions}"
        self.file_content.append(productions)

        tokens = f"tokens = {self.yapar_formatter.tokens}"
        self.file_content.append(tokens)

        ignore_tokens = f"ignore_tokens = {self.yapar_formatter.ignore}"
        self.file_content.append(ignore_tokens)

        self.file_content.append("grammar = Grammar(productions)")
        self.file_content.append("grammar.split_grammar_elements(tokens)")
        self.file_content.append("slr = SLR(grammar)")
        self.file_content.append("slr.build_LR_automaton()")
        self.file_content.append("slr.build()")
        self.file_content.append("slr.ignore_tokens = ignore_tokens")
        self.file_content.append("slr.initialize_parse()")

    def write_to_file(self):
        with open(self.file, "wt") as file:
            for content in self.file_content:
                file.write(content + '\n')
        
        print("Archivo generado: ", f"{self.file}")