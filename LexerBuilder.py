from Reader import YalexReader
from Formatter import YalexFormatter
from regex import Regex
from NFA import NFA
from Tokenizer import Tokenizer
import textwrap

class LexerBuilder(object):
    def __init__(self, path) -> None:
        self.path = path
        self.file_content = []
        self.regexes = []
    
    def read_lexer_file(self):
        self.reader = YalexReader(self.path)
        self.yalex_content = self.reader.read()
    
    def get_tokens_from_yalex(self):
        formatter = YalexFormatter()
        self.yalex_errors = formatter.format_yalex_content(self.yalex_content)
        self.tokens = formatter.tokens

    def errors_exception(self):
        errors = ""
        if self.regex_errors:
            for error in self.regex_errors:
                errors += str(error)
        if self.yalex_errors:
            for error in self.yalex_errors:
                errors += error
        if errors:
            raise Exception(errors)

    def create_NFAS(self):
        self.NFAs = []
        self.count = 1
        self.regex_errors = set()
        for element in self.tokens:
            regex = element[0]
            action = element[1]
            self.regexes.append(regex)
            try:
                regex = Regex(regex)
                nfa = NFA(regex, self.count)
                
                self.count = nfa.count
                self.NFAs.append(nfa)
            except Exception as e:
                self.regex_errors.add(e)


    def concat_files_needed(self):
        files = ["Node", "AST", "FAErrorChecker", "STNode", "ST", "RegexErrorChecker", "AFVisual", "regex", "FAErrorChecker", "FA", "DFA", "NFA", "Tokenizer"]
        imports = ["from regex import Regex", "from Node import Node", "from AST import AST", 
                   "from RegexErrorChecker import RegexErrorChecker", "from AFVisual import AFVisual", 
                   "from FA import FA", "from DFA import DFA",
                   "from AST import AST", "from STNode import STNode", "from FAErrorChecker import FAErrorChecker"]
        for file in files:
            with open(file + ".py", "rt") as archivo:
                contenido = archivo.read()
                for element in imports:
                    contenido = contenido.replace(element, '')
                self.file_content.append(contenido)

    def concat_functionality(self):
        self.functionality = []
        list_of_regex = 'regexes = ['
        for i in range(len(self.regexes) - 1):
            list_of_regex += f"'{self.regexes[i]}'" + ','
        list_of_regex += f"'{self.regexes[-1]}'" + ']'
        self.functionality.append(list_of_regex)
        nfa_creator = textwrap.dedent("""
        count = 1
        NFAs = []
        for regex in regexes:
            regex = Regex(regex)
            nfa = NFA(regex, count)
            count = nfa.count
            NFAs.append(nfa)
        """)
        self.functionality.append(nfa_creator)
        tokenizer_concat = textwrap.dedent("""
        tokenizer = Tokenizer()
        for nfa in NFAs:
            tokenizer.concatenate_FA(nfa)
        tokenizer.output_image()
        """)
        self.functionality.append(nfa_creator)
        self.functionality.append(tokenizer_concat)

    def write_to_file(self):

        with open("resultado.py", "wt") as file:
            for content in self.file_content:
                file.write(content + '\n')
            for function in self.functionality:
                file.write(function.replace('\t', '') + '\n')
            
    
    # TODO: Arreglar para poder almacenar que tokens van segun estado de aceptacion.
    #       Tomar en cuenta jerarquia.
    def create_tokenizer(self):
        tokenizer = Tokenizer()
        for nfa in self.NFAs:
            tokenizer.concatenate_FA(nfa)
        # print(tokenizer.simulate(''))
        # other = tokenizer.convert_to_DFA()
        # other.minimize()
        # other.output_image()
        # tokenizer.output_image()