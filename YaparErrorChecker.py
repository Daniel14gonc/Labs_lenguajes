class YaparErrorChecker(object):
    
    def __init__(self):
        self.errors = []
        self.tokens = None

    def check_errors(self, content):
        self.file_content = content
        self.check_comments()
        self.check_productions()
        self.check_tokens()
        self.check_spelling()

        return self.errors

    def check_comments(self):
        comments = 0
        i = 0
        while i < len(self.file_content):
            element = self.file_content[i]
            next = None
            if i + 1 < len(self.file_content):
                next = self.file_content[i + 1]
            
            if next:
                if element + next == '/*' or element + next == '*/':
                    comments += 1
            i += 1

        if comments % 2 != 0:
            self.errors.append("Error in Yapar: Comments unbalanced.\n")
        
    def check_productions(self):
        content_splitted = self.file_content.split('%%')
        if len(content_splitted) != 2:
            self.errors.append("Error in Yapar: Tokens and Productions not separated by '%%'.\n")
            return

        productions = content_splitted[1].strip().split(';')
        if len(productions) == 0:
            self.errors.append("Error in Yapar: Productions not defined or not separated by ';'.\n")
        i = 1
        productions = productions[:-1]
        for element in productions:
            if element != '' or element != ' ':
                count = element.count(':')
                if count > 1 or count == 0:
                    self.errors.append(f'Error in Yapar: Production {i} is defined incorrectly.\n')
            
                i += 1

    def delete_comments(self):
        acu = ''
        i = 0
        inside_comment = False
        while i < len(self.file_content):
            element = self.file_content[i]
            if i + 1 < len(self.file_content):
                next_element = self.file_content[i + 1]
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

        self.file_content = acu.strip()

    def check_tokens(self):
        self.delete_comments()
        content_splitted = self.file_content.split('%%')
        error = False
        token_section = None
        if len(content_splitted) == 2:
            token_section = content_splitted[0].strip()
            splitted_token_section_by_lines = token_section.splitlines()
            i = 1
            for line in splitted_token_section_by_lines:
                if line != '' and line != ' ' and 'IGNORE' not in line and '%token' not in line:
                    self.errors.append(f"Error in Yapar: Line {i} of token declaration does not contain the '%token' keyword.\n")
                    error = True
                i += 1
        else:
            error = True
        
        if not error:
            self.get_tokens(token_section)

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


    def check_spelling(self):
        if self.tokens:
            for token in self.tokens:
                if not token.isupper():
                    self.errors.append(f"Error in Yapar: Token {token} should contain only uppercase letters.\n")
        
            content_splitted = self.file_content.split('%%')
            if len(content_splitted) != 2:
                return

            productions = content_splitted[1].strip().split(';')
            if len(productions) == 0:
                return
            i = 1
            productions = productions[:-1]
            for production in productions:
                temp = production.split(' ')
                for element in temp:
                    element = element.strip()
                    if element != '' and element != ' ' and len(element) != 0:
                        if element == '\n':
                            i += 1
                        elif element != '|' and element != ':' and element != ';' and element not in self.tokens:
                            if not element.strip().islower():
                                self.errors.append(f'Error in Yapar: Non terminal {element} must have only lowercase letters at line {i}.\n')
