import re

class YalexReader(object):

    def __init__(self, path) -> None:
        self.path = path
        self.header_result = ''
        self.regex = {}
    
    def read(self):
        file = open(self.path, 'r')
        self.file_content = file.read()
        file.close()
        self.build_header()
        self.clean_comments()
        self.build_regex()
        self.replace_common_patterns()
        

    def clean_comments(self):
        patron = re.compile(r'\(\*.*?\*\)', re.DOTALL)
        self.file_content = re.sub(patron, '', self.file_content)

    def build_regex(self):
        patron = re.compile(r'\{.*?\}', re.DOTALL)
        content =  re.sub(patron, '', self.file_content)
        content = content.split("\n")
        for line in content:
            line = line.strip()
            if line:
                if "let" in line:
                    self.common_regex(line)
    
    def check_operators(self, element):
        operators = '*+|?'
        for operator in operators:
            if operator in element:
                return True
        return False
    
    def space_operators(self, line):
        operators = '*+|?'
        for operator in operators:
            line = line.replace(operator, ' ' + operator + ' ')
        return line
    
    def replace_common_patterns(self):
        numbers = '(0|1|2|3|4|5|6|7|8|9)'
        letters = 'a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z'
        letters_upper = letters.upper()
        paren_lower_letters = '(' + letters + ')'
        paren_upper_letters = '(' + letters_upper + ')'
        upper_lower_letters = '(' + letters + '|' + letters_upper + ')'

        for key in self.regex:
            regex = self.regex[key]
            regex = regex.replace('[A-Z a-z]', upper_lower_letters)
            regex = regex.replace('[0-9]', numbers)
            regex = regex.replace('[a-z]', paren_lower_letters)
            regex = regex.replace('[A-Z]', paren_upper_letters)
            self.regex[key] = regex

    def common_regex(self, line):
        line = self.space_operators(line)
        line = line.replace('" "', '"space"')
        line = line.replace("' '", "'space'")
        line = line.split(" ")
        body = ''
        for i in range(3, len(line)):
            element = line[i]
            if "'" in element or '"' in element:
                if 'space' in element:
                    body += ' '
                else:
                    element = element.replace('"', '')
                    element = element.replace("'", "")
                    body += element
            elif not self.check_operators(element) and len(element) > 1:
                replacement = self.regex[element]
                body += replacement 
            else:
                body += element
        self.regex[line[1]] = body
        

    def build_header(self):
        content = self.file_content.split('\n')
        if self.check_header():
            i = 0
            finished = False
            while not finished:
                line = content[i].strip()
                for element in line:
                    if element != '{' and element != '}':
                        self.header_result += element
                    if element == '}':
                        finished = True
                        self.header_result = self.header_result.strip()
                        break
                self.header_result += '\n'
                i += 1

    def check_header(self):
        has_header = True
        i = 0
        content = self.file_content.split('\n')
        while has_header:
            line = content[i].strip()
            if line:
                if line == "{" or "{" in line:
                    return True
            if 'let' in line or 'rule' in line:
                return False
            i += 1

    def get_header(self):
        pass

    def get_regex(self):
        pass

    def get_trailer(self):
        pass