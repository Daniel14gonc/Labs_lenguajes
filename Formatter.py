import re
from YalexErrorChecker import YalexErrorChecker

 # TODO para formateado: ver reglas de yalex para escape, EOF, espacios en blanco, etc.
class YalexFormatter(object):
    def __init__(self) -> None:
        self.header_result = ''
        self.regex = {}
        self.simple_pattern = r"\[(\w)\s*-\s*(\w)\]"
        self.compound_pattern = r"\[(\w)\s*-\s*(\w)\s*(\w)\s*-\s*(\w)\]"
        self.list_pattern = r"\[[^\[\]]*\]"
        self.simple_regex_pattern = r"^let\s+\w+\s+=\s+(.*?)$"
        self.token_line_regex = r"\[([^]]*)\]"
        self.error_checker = YalexErrorChecker()
        self.tokens = []

    def format_yalex_content(self, yalex_content):
        self.file_content = yalex_content
        self.errors = self.error_checker.check_errors(self.file_content)
        # try:
        #     self.build_header()
        # except:
        #     pass

        # try:
        #     self.clean_comments()
        # except:
        #     pass

        # try:
        #     self.replace_quotation_mark()
        # except:
        #     pass

        # try:
        #     self.build_regex()
        # except:
        #     pass

        # try:
        #     self.build_tokens()
        # except:
        #     pass

        self.build_header()
        self.clean_comments()
        self.replace_quotation_mark()
        self.build_regex()
        self.build_tokens()
        return set(self.errors)

    def replace_quotation_mark(self):
        self.file_content = self.file_content.replace('"', " ' ")
        self.file_content = self.file_content.replace("'", " ' ")
        

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
                if re.match(self.simple_regex_pattern, line):
                    self.add_common_regex(line)

    def replace_delimiters(self, expression):
        new_list = []
        for element in expression:
            element = element.replace('\n', '')
            element = element.strip()
            new_list.append(element)
        return new_list
    
    def replace_existing_regex(self, expressions):
        new_list = []
        for element in expressions:
            regex = element[0]
            if regex in self.regex:
                replacement = self.regex[regex]
                element[0] = replacement
            new_list.append(element)
        return new_list
    
    def convert_regexes_to_tuples(self, expressions):
        new_list = []
        # print(expressions)
        for element in expressions:
            splitted = element.split('\t', maxsplit=1)
            first_part = splitted[0]
            print(first_part)
            # if "'" not in first_part and '"' not in first_part and first_part not in self.regex:
            #     self.errors.append(f'Error: previous regex definition "{first_part}" does not exist.\n')
            if first_part not in self.regex:
                first_part = self.space_operators(first_part)
                first_part = self.common_regex(first_part.split(" "))
            second_part = splitted[1].replace('\t', '')
            second_part = second_part.replace('{' , '')
            second_part = second_part.replace('}', '')
            second_part = second_part.strip()
            element = [first_part, second_part]
            new_list.append(element)
        return new_list
    
    def add_meta_character_string(self, expression):
        expression = expression.replace('.', '\.')
        expression = expression.replace('+', '\+')
        expression = expression.replace('*', '\*')
        expression = expression.replace('"', '')
        expression = expression.replace("'", "")
        expression = expression.replace("(", "\(")
        expression = expression.replace(")", "\)")
        expression = expression.replace("?", "\?")

        return expression

    def add_meta_character_token(self, expressions):
        new_list = []
        for element in expressions:
            expression = element[0]
            if "'" in expression or '"' in expression:
                element[0] = self.add_meta_character_string(expression)
            new_list.append(element)
        return new_list
    
    def split_token_lines(self, content):
        lines = content.splitlines()
        i = 0
        result = []
        while i < len(lines):
            element = lines[i]
            if element:
                if element.strip()[0] == '|':
                    element = element.split('|', maxsplit=1)
                    element = element[1]
                    result.append(element)
                elif element != "" and element != " " and element != "\t" and element != "\n":
                    result.append(element)
            i+=1
        return result

    def build_tokens(self):
        content = self.file_content.split('rule tokens =')
        content = self.trim_quotation_marks(content[1])
        content = self.split_token_lines(content)
        content = self.replace_delimiters(content)
        content = self.convert_regexes_to_tuples(content)
        content = self.add_meta_character_token(content)
        content = self.replace_existing_regex(content)
        self.tokens = content

    def check_is_blank(self, content):
        for element in content:
            if element != " ":
                return False
            
        return True
    
    def replace_blank(self, content):
        count = 0
        pass

    def trim_quotation_marks(self, line):
        matches = re.findall(r"'([^']+)'", line)
        for element in matches:
            text = element
            replacement = text
            if not self.check_is_blank(text):
                replacement = text.strip()
            else:
                replacement = re.sub(r'\s+', 'ε', text)
            line = line.replace("'" + text + "'", "'" + replacement + "'")
        return line
    
    def build_common_regex(self, line):
        body = ''
        for i in range(len(line)):
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
                    element = element.replace('(', '\(')
                    element = element.replace(')', '\)')
                    element = element.replace('?', '\?')
                    body += element
            elif not self.check_operators(element) and len(element) > 1:
                if element not in self.regex:
                    self.errors.append(f'Error: previous regex definition "{element}" does not exist.\n')
                    body += element
                else:
                    replacement = self.regex[element]
                    body += replacement 
            else:
                body += element
        return body
    
    def add_common_regex(self, line):
        line = self.space_operators(line)
        line = self.trim_quotation_marks(line)
        line = line.replace('" "', '"ε"')
        line = line.replace("' '", "'ε'")
        line = line.split(" ")
        body = self.common_regex(line[3:])
        self.regex[line[1]] = body


    def common_regex(self, line):
        body = self.build_common_regex(line)
        body = body.replace('ε', ' ')
        body = self.replace_common_patterns(body)
        body = body.strip()
        return body
    
    def check_operators(self, element):
        operators = '*+|?'
        for operator in operators:
            if operator in element:
                return True
        return False
    
    def space_operators(self, line):
        operators = '*+|?()'
        cont = 0
        result = ""
        for element in line:
            if element == "'" or element == '"':
                cont += 1
            if element in operators:
                if cont % 2 == 0:
                    result += ' ' + element + ' '
                else:
                    result += element
            else:
                result += element
        
        return result
    
    def get_range_of_strings(self, initial, final):
        result = ''
        if ord(initial) > ord(final) and final.lower() in self.letters:
            result += self.get_range_of_strings(initial, 'z') + '|'
            result += self.get_range_of_strings(chr(ord(initial.upper()) -1), final)
        else:
            for i in range(ord(initial) + 1, ord(final)):
                between_letter = chr(i)
                result += between_letter + '|'
            result += final
        return result
    
    def get_range_of_numbers(self, initial, final):
        result = ''
        for i in range(int(initial) + 1, int(final)):
            result += str(i) + '|'
        result += final
        return result

    
    def replace_range(self, initial, final):
        result = str(initial) + '|'
        if initial.lower() in self.numbers and final.lower() in self.letters:
            result += self.get_range_of_numbers(initial, '9') + '|'
            initial_letter = 'A' if final in self.upper_letters else 'a'
            result += initial_letter + '|'
            result += self.get_range_of_strings(initial_letter, final)
        elif initial.lower() in self.letters:
            final_letter = 'Z' if initial in self.upper_letters else 'z'
            if final in self.numbers:
                result += self.get_range_of_strings(initial, final_letter) + '|'
                result += '0' + '|' + self.get_range_of_numbers('0', final)
            else:
                result += self.get_range_of_strings(initial, final)
        elif initial in self.numbers:
                result += self.get_range_of_numbers(initial, final)
        return result
    
    def simple_range(self, regex):
        initial = self.search_simple_regex_result.group(1)
        final = self.search_simple_regex_result.group(2)
        result = self.replace_range(initial, final)
        result = '(' + result + ')'
        regex = regex.replace('['+initial+'-'+final+']', result)
        return regex
    
    def compound_range(self, regex):
        first_initial = self.search_compound_regex_result.group(1)
        first_final = self.search_compound_regex_result.group(2)

        last_initial = self.search_compound_regex_result.group(3)
        last_final = self.search_compound_regex_result.group(4)

        first_range = self.replace_range(first_initial, first_final)
        second_range = self.replace_range(last_initial, last_final)

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
    
    def simple_list(self, list):
        #print(list)
        pass
    
    def replace_common_patterns(self, regex):
        self.letters = 'abcdefghijklmnopqrstuvwxyz'
        self.upper_letters = self.letters.upper()
        self.numbers = '0123456789'
        self.search_simple_regex_result = re.search(self.simple_pattern, regex)
        self.search_compound_regex_result = re.search(self.compound_pattern, regex)
        self.search_list = re.search(self.list_pattern, regex)
        if self.search_simple_regex_result and not self.search_compound_regex_result:
            regex = self.simple_range(regex)
        elif self.search_compound_regex_result:
            regex = self.compound_range(regex)
        elif self.search_list:
            self.simple_list(regex)

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