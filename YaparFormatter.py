from YaparErrorChecker import YaparErrorChecker

class YaparFormatter(object):
    
    def __init__(self) -> None:
        self.error_checker = YaparErrorChecker()

    def format_yapar_content(self, yapar_content):
        self.yapar_content = yapar_content
        self.errors = self.error_checker.check_errors(self.yapar_content)
        functions = [self.delete_comments, self.split_file_content, self.create_tokens, self.create_productions]
        for function in functions:
            try:
                function()
            except:
                pass
        # self.delete_comments()
        # self.split_file_content()
        # self.create_tokens()
        # self.create_productions()

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

    def split_file_content(self):
        splitted_content = self.yapar_content.split('%%')
        self.token_content = splitted_content[0].strip()
        self.production_content = splitted_content[1].strip()

    def create_tokens(self):
        self.get_tokens(self.token_content)

    def get_tokens_to_ignore(self):
        return self.ignore
    
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

    def get_body(self, body):
        content = None
        if '|' in body:
            content = body.split('|')
        else:
            content = [body]

        return content