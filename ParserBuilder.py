from Formatter import YalexFormatter
from Reader import Reader
from Grammar import Grammar
from LRAutomaton import LRAutomaton

class ParserBuilder(object):
    
    def __init__(self, yapar, yalex) -> None:
        self.yalex_reader = Reader(yalex)
        self.yapar_reader = Reader(yapar)
        self.yalex_formatter = YalexFormatter()
        self.yapar_formatter = Reader(yapar)

    def get_token_names(self):
        yalex_content = self.yalex_reader.read()
        self.yalex_formatter.format_yalex_content(yalex_content)
        self.token_names = self.yalex_formatter.get_token_names()


    def read_yapar_file(self):
        self.yapar_content = self.yapar_reader.read()

    def delete_comments(self):
        acu = ''
        i = 0
        inside_comment = False
        while i < len(self.yapar_content):
            element = self.yapar_content[i]
            if i + 1 < len(self.yapar_content):
                next_element = self.yapar_content[i + 1]
                compound = element + next_element
                if compound == '/*':
                    inside_comment = True
                    i += 2
                elif compound == '*/':
                    inside_comment = False
                    i += 2
                elif not inside_comment:
                    acu += element
                    i += 1
                else:
                    i += 1
            else:
                acu += element
                i += 1

        self.yapar_content = acu.strip()

    
    def convert_productions(self):
        self.delete_comments()
        self.split_file_content()
        self.create_tokens()
        self.create_productions()

    def create_LR_automaton(self):
        grammar = self.build_grammar()
        grammar.augument()
        automaton = LRAutomaton(grammar)
        automaton.build()
        automaton.visualize()

    
    def split_file_content(self):
        splitted_content = self.yapar_content.split('%%')
        self.token_content = splitted_content[0].strip()
        self.production_content = splitted_content[1].strip()

    def create_tokens(self):
        self.get_tokens(self.token_content)

    def compare_tokens(self):
        yalex_tokens = set(self.token_names)
        yapar_tokens = set(self.tokens)
        return yalex_tokens == yapar_tokens


    def get_tokens(self, token_section):
        self.tokens = []
        self.ignore = []
        in_token = False
        in_ignore = False
        token_section_by_lines = token_section.splitlines()
        for line in token_section_by_lines:
            content = line.split(' ')
            for element in content:
                if element != '':
                    if element == '%token':
                        in_token = True
                        in_ignore = False
                    elif element == 'IGNORE':
                        in_ignore = True
                        in_token = False
                    else:
                        if in_token:
                            self.tokens.append(element.strip())
                        if in_ignore:
                            self.ignore.append(element.strip())

        for token in self.tokens:
            if token in self.ignore:
                self.tokens.remove(token)
    
    def get_body(self, body):
        content = None
        if '|' in body:
            content = body.split('|')
        else:
            content = [body]

        return content


    def create_productions(self):
        finished_production = False
        self.productions = []
        first_production = None
        acu = ''
        for element in self.production_content:
            if element != '\n':
                if element == ';':
                    finished_production = True
                if finished_production:
                    acu = acu.split(':')
                    head = acu[0].strip()
                    body = acu[1].strip()
                    body = self.get_body(body)
                    for element in body:
                        body_list = element.split(' ')
                        body_list = [item.strip() for item in body_list if item != '']
                        self.productions.append((head, body_list))
                    acu = ''
                else:
                    acu += element 
                finished_production = False
    
    def build_grammar(self):
        return Grammar(self.productions)