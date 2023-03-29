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
        # print(self.regex)
        

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

    def common_regex(self, line):
        line = self.space_operators(line)
        line = line.replace('" "', '"ε"')
        line = line.replace("' '", "'ε'")
        line = line.split(" ")
        body = ''
        for i in range(3, len(line)):
            element = line[i]
            if "'" in element or '"' in element:
                if 'space' == element:
                    body += ' '
                else:
                    element = element.replace('"', '')
                    element = element.replace("'", "")
                    element = element.replace('+', '\+')
                    element = element.replace('.', '\.')
                    element = element.replace('*', '\*')
                    body += element
            elif not self.check_operators(element) and len(element) > 1:
                replacement = self.regex[element]
                body += replacement 
            else:
                body += element
        # body = body.replace('ε', 'ε')
        body = self.replace_common_patterns(body)
        # if body != " ":
        body = body.strip()
        self.regex[line[1]] = body
    
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
    
    def replace_range(self, initial, final):
        result = str(initial) + '|'
        if initial.lower() in self.letters:
            for i in range(ord(initial) + 1, ord(final)):
                between_letter = chr(i)
                result += between_letter + '|'
            result += final
        elif initial in self.numbers:
            for i in range(int(initial) + 1 , int(final)):
                result += str(i) + '|'
            result += str(final)

        return result
    
    def simple_range(self, regex):
        splitted = regex.split('-')
        initial = splitted[0].replace('[', '')
        initial = initial.strip()
        initial = initial[0]
        final = splitted[1].replace(']', '')
        final = final.strip()
        final = final[0]
        result = self.replace_range(initial, final)
        result = '(' + result + ')'
        regex = regex.replace('['+initial+'-'+final+']', result)
        return regex
    
    def compound_range(self, regex):
        splitted = regex.split(' ')
        first = splitted[0].replace('[', '')
        last = splitted[1].replace(']', '')

        splitted_first = first.split('-')
        splitted_last = last.split('-')
        first_range = self.replace_range(splitted_first[0][0], splitted_first[1][0])
        second_range = self.replace_range(splitted_last[0][0], splitted_last[1][0])
        result = '(' + first_range + '|' + second_range + ')'
        replaced = ''
        i = 0
        closed = False
        while not closed:
            if regex[i] == ']':
                closed = True
            replaced += regex[i]
            i += 1
        regex = regex.replace(replaced, result)
        return regex

    def appeareances(self, string, symbol):
        counter = 0
        for element in string:
            if element == symbol:
                counter += 1

        return counter
    
    def replace_common_patterns(self, regex):
        self.letters = 'abcdefghijklmnopqrstuvwxyz'
        self.numbers = '0123456789'
        hyphen = '-'
        if '[' in regex and ']' in regex and '-' in regex:
            if self.appeareances(regex, hyphen) > 1 and self.appeareances(regex, '[') == 1:
                regex = self.compound_range(regex)
            elif self.appeareances(regex, '[') == 1:
                regex = self.simple_range(regex)
        return regex
        

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