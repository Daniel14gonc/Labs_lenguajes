from Reader import Reader
from Formatter import YalexFormatter
from regex import Regex
from NFA import NFA
from DFA import DFA
from Tokenizer import Tokenizer
import textwrap

class LexerBuilder(object):
    def __init__(self, path, file) -> None:
        self.path = path
        self.file = file
        self.file_content = []
        self.regexes = []
    
    def read_lexer_file(self):
        self.reader = Reader(self.path)
        self.yalex_content = self.reader.read()
    
    def get_tokens_from_yalex(self):
        self.formatter = YalexFormatter()
        self.yalex_errors = self.formatter.format_yalex_content(self.yalex_content)
        self.tokens = self.formatter.tokens
        self.header = textwrap.dedent(self.formatter.get_header())
        self.trailer = textwrap.dedent(self.formatter.get_trailer())

    def errors_exception(self):
        errors = ""
        if self.regex_errors:
            errors += '\nErrors in regex\n'
            for error in self.regex_errors:
                errors += str(error)
        if self.yalex_errors:
            errors += '\nErrors in YAlex\n'
            for error in self.yalex_errors:
                errors += error
        if errors:
            raise Exception(errors)

    def create_NFAS(self):
        self.NFAs = []
        self.count = 1
        self.regex_errors = set()
        self.actions = []
        priority = 0
        self.actions_tokens = []
        for element in self.tokens:
            regex = element[0]
            action = element[1]
            self.actions_tokens.append(action)
            self.regexes.append(regex)
            try:
                regex = Regex(regex)
                dfa = DFA(regex, self.count)
                dfa.minimize()
                self.count = dfa.count
                self.NFAs.append(dfa)
                final_states = dfa.acceptance_states
                final_states = frozenset(final_states)
                self.actions.append((priority, str(action)))
            except Exception as e:
                self.regex_errors.add(e)
            priority += 1

    def concat_files_needed(self):
        files = ["Reader", "Node", "AST", "FAErrorChecker", "STNode", "ST", "RegexErrorChecker", "AFVisual", "regex", "FAErrorChecker", "FA", "DFA", "NFA", "Tokenizer", "TokenLex"]
        imports = ["from regex import Regex", "from Node import Node", "from AST import AST", "from ST import ST",
                   "from RegexErrorChecker import RegexErrorChecker", "from AFVisual import AFVisual", 
                   "from FA import FA", "from DFA import DFA",
                   "from AST import AST", "from STNode import STNode", "from FAErrorChecker import FAErrorChecker",
                   "from NFA import NFA", "from TokenLex import TokenLex"]
        
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

        list_of_actions = f'actions_tokens = {self.actions}'
        self.functionality.append(list_of_actions)

        nfa_creator = textwrap.dedent("""
        count = 1
        NFAs = []
        priority = 0
        actions = {}
        for regex in regexes:
            regex = Regex(regex)
            dfa = DFA(regex, count)
            dfa.minimize()
            count = dfa.count
            NFAs.append(dfa)
            final_states = dfa.acceptance_states
            final_states = frozenset(final_states)
            actions[final_states] = actions_tokens[priority]
            priority += 1
        """)
        self.functionality.append(nfa_creator)
        tokenizer_concat = textwrap.dedent("""
        tokenizer = Tokenizer()
        for nfa in NFAs:
            tokenizer.concatenate_FA(nfa)
        tokenizer.edit_meta_alphabet()
        """)
        self.functionality.append(tokenizer_concat)

        # read_text = textwrap.dedent("""
        #     def evaluate_file(path):
        #         content = Reader(path).read()
        #         return content
        #     """)
        # self.functionality.append(read_text)

        # token_evaluation = textwrap.dedent("""
        #     def output_tokens(tokens):
        #         for token in tokens:
        #             exec(token)
        #     """)
        # self.functionality.append(token_evaluation) 

        text = """
        import sys

        args = sys.argv

        path = None
        if len(args) > 1: 
            path = args[1]
        else:
            raise Exception("Source code not specified.")
        tokenizer.set_actions(actions)
        tokenizer.read_source_code(path)
        # tokenizer.initialize_token_recognition()
        # while tokenizer.has_next_token():
        #     print(tokenizer.next_token())
        """

        token_evaluator = textwrap.dedent(text)
        self.functionality.append(token_evaluator)



    def write_to_file(self):

        with open(self.file, "wt") as file:
            file.write(self.header + '\n')
            for content in self.file_content:
                # for element in imports:
                #     print("from RegexErrorChecker import RegexErrorChecker" in content)
                #     content = content.replace(element, '')
                file.write(content + '\n')
            for function in self.functionality:
                file.write(function.replace('\t', '') + '\n')
            file.write(self.trailer + '\n')
        
        print("Archivo generado: ", f"{self.file}")
            
    
    # TODO: Arreglar para poder almacenar que tokens van segun estado de aceptacion.
    #       Tomar en cuenta jerarquia.
    def create_tokenizer(self):
        tokenizer = Tokenizer()
        for nfa in self.NFAs:
            tokenizer.concatenate_FA(nfa)
        tokenizer.set_actions(self.actions)
        # print(tokenizer.simulate(''))
        # other = tokenizer.convert_to_DFA()
        # other.minimize()
        # other.output_image()
        # tokenizer.output_image()
        
        # tokenizer.edit_meta_alphabet()
        # string = self.evaluate_file()
        # initial = 0
        # advance = 0
        # latest_token = None
        # line = 0
        # line_pos = 0

        # while initial < len(string):
        #     advance = initial
        #     tokenizer.begin_simulation()
        #     longest_lexeme = False
        #     latest_token = None
        #     while not longest_lexeme and advance < len(string):
        #         symbol = string[advance]
        #         tokenizer.simulate_symbol(symbol)
        #         accepted = tokenizer.is_accepted()
        #         has_transitions = tokenizer.has_transitions()
        #         longest_lexeme = not (accepted or has_transitions)
        #         if not (longest_lexeme and latest_token):
        #             latest_token = tokenizer.get_token()
        #             advance += 1
        #             line_pos += 1
        #             if symbol == '\n':
        #                 line += 1
        #                 line_pos = -1

        #     if latest_token:
        #         exec(latest_token)
        #     else:
        #         print(f"Lexical error on line {line} at position {line_pos}.")
        #     initial = advance
 
    def evaluate_file(self):
        content = Reader('file.txt').read()
        return content
        # print(content)
        