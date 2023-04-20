import re
from YalexErrorChecker import YalexErrorChecker
import textwrap

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

    def get_token_name(self):
        content = self.file_content.split("rule")[1]
        token_name = content.split("=")[0]
        self.token_name = token_name

    def format_yalex_content(self, yalex_content):
        self.file_content = yalex_content
        self.get_token_name()
        self.errors = self.error_checker.check_errors(self.file_content)
        formatter_funcs = [self.clean_comments, self.build_header, self.build_trailer, 
                           self.replace_quotation_mark, self.build_regex, self.build_tokens]
        for func in formatter_funcs:
            try:
                func()
            except:
                pass

        # self.build_header()
        # self.clean_comments()
        # self.replace_quotation_mark()
        # self.build_regex()
        # self.build_tokens()
        seen = set()  # conjunto para almacenar los elementos únicos
        unique = []   # lista para almacenar los elementos únicos en orden
        for item in self.errors:
            if item not in seen:
                seen.add(item)
                unique.append(item)
        return set(unique)

    def replace_quotation_mark(self):
        acu = ''
        single_quotation = 0
        double_quotation = 0
        for element in self.file_content:
            if element == '"' and single_quotation % 2 == 0:
                acu += ' " '
                double_quotation += 1
            elif element == "'" and double_quotation % 2 == 0:
                acu += " ' "
                single_quotation += 1
            else:
                acu += element
        self.file_content = acu
        

    def clean_comments(self):
        patron = re.compile(r'\(\*.*?\*\)', re.DOTALL)
        self.file_content = re.sub(patron, '', self.file_content)

    def build_regex(self):
        patron = re.compile(r'\{.*?\}', re.DOTALL)
        content =  re.sub(patron, '', self.file_content)
        content = content.split('rule')[0].strip()
        acu = ''
        i = 0
        for element in content:
            if element != '\n':
                acu += element
            if len(acu) > 3:
                temp = acu[len(acu) - 4:]
                if temp == 'let ' or temp == 'let=' or i + 1 == len(content):
                    if i + 1 == len(content):
                        regex = acu
                    else:
                        regex = acu[:-4]
                    acu = 'let '
                    if re.match(self.simple_regex_pattern, regex):
                        regex = regex if self.check_is_blank(regex) else regex.strip()
                        self.add_common_regex(regex)
            i += 1
        # content = content.split("\n")
        
        # for line in content:
        #     line = line.strip()
        #     if line:
        #         if re.match(self.simple_regex_pattern, line.strip()):
        #             self.add_common_regex(line.strip())

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
    
    def get_splitted_expression(self, expression):
        acu = ''
        inside_code = False
        tokens = []
        action = ''
        quotes = 0
        double = 0
        for element in expression:
            if element == "'" and double % 2 == 0:
                quotes += 1
            if element == '"' and quotes % 2 == 0:
                double += 1
            if element == '{':
                inside_code = True
            elif element == '}' and quotes % 2 == 0 and double % 2 == 0:
                inside_code = False
                tokens.append(acu.strip())
                tokens.append(action)
                acu = ''
                action = ''
            elif inside_code:
                action += element
            else:
                acu += element
        return tokens
    
    
    def convert_regexes_to_tuples(self, expressions):
        new_list = []
        for element in expressions:
            # self.get_splitted_expression(element)
            splitted = self.get_splitted_expression(element)
            first_part = splitted[0]
            # if "'" not in first_part and '"' not in first_part and first_part not in self.regex:
            #     self.errors.append(f'Error: previous regex definition "{first_part}" does not exist.\n')
            if first_part not in self.regex and first_part.upper() != 'EOF':
                first_part = self.space_operators(first_part)
                first_part = self.common_regex(first_part.split(" "))
            second_part = splitted[1]
            second_part = textwrap.dedent(second_part)
            # second_part = second_part.replace('\t', '')
            second_part = second_part.replace('{' , '')
            second_part = second_part.replace('}', '')
            second_part = second_part.strip() if not self.check_is_blank(second_part) else second_part
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
            if "'" == expression[0]:
                element[0] = self.add_meta_character_string(expression)
            new_list.append(element)
        return new_list
    
    def split_token_lines(self, content):
        acu = ''
        tokens = []
        single_quotes = 0
        double_quotes = 0
        for character in content:
            acu += character
            if character == "'" and double_quotes % 2 == 0:
                single_quotes += 1
            if character == '"' and single_quotes % 2 == 0:
                double_quotes += 1 
            if character == '}' and (single_quotes % 2 == 0 and double_quotes % 2 == 0):
                acu = acu.strip()
                if acu[0] == '|':
                    acu = acu[1:]
                tokens.append(acu.strip())
                acu = ''
        return tokens

    def build_tokens(self):
        content = self.file_content.split("rule" + self.token_name + "=")
        content = self.trim_quotation_marks(content[1])
        content = self.split_token_lines(content)
        # content = self.replace_delimiters(content)
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
        stack_single = []
        stack_double = []
        double = 0
        single = 0
        acu = ''
        res = ''

        for element in line:
            if element == "'" and double % 2 == 0:
                single += 1
                if stack_single:
                    stack_single.pop()
                    if not self.check_is_blank(acu):
                        acu = '\\"' if acu.strip() == '"' else acu
                        res += "'" + acu.strip() + "'"
                    else:
                        res += "'ε'"
                    acu = ''
                else:
                    stack_single.append("'")
            elif element == '"' and single % 2 == 0:
                double += 1
                if stack_double:
                    stack_double.pop()
                    if not self.check_is_blank(acu):
                        acu = "\\'" if acu.strip() == "'" else acu
                        res += '"' + acu.strip() + '"'
                    else:
                        res += '"ε"'
                    acu = ''
                else:
                    stack_double.append('"')
            elif stack_double or stack_single:
                acu += element
            else:
                res += element
        return res
        # matches = re.findall(r"'([^']+)'", line)
        # for element in matches:
        #     text = element
        #     replacement = text
        #     if not self.check_is_blank(text):
        #         replacement = text.strip()
        #     else:
        #         replacement = re.sub(r'\s+', 'ε', text)
        #     line = line.replace("'" + text + "'", "'" + replacement + "'")
        # return line
    
    def build_common_regex(self, line):
        body = ''
        for i in range(len(line)):
            element = line[i]
            if "'" in element or '"' in element:
                if 'space' == element:
                    body += ' '
                else:
                    if "'" == element[0]:
                        element = element.replace("'", "")
                    elif '"' == element[0]:
                        element = element.replace('"', "")
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
        body = self.replace_common_patterns(body)
        body = body.replace(' ', 'ε')
        body = body.strip() if not self.check_is_blank(body) else body
        body = body.replace('ε', ' ')
        return body
    
    def check_operators(self, element):
        operators = '*+|?'
        for operator in operators:
            if operator in element:
                return True
        return False
    
    def space_operators(self, line):
        operators = '*+|?()'
        single = 0
        result = ""
        double = 0
        for element in line:
            if element == "'" and double % 2 == 0:
                single += 1
            
            if element == '"' and single % 2 == 0:
                double += 1
            if element in operators:
                if single % 2 == 0 and double % 2 == 0:
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
        count = 0
        while i < len(regex):
            element = regex[i]
            if regex[i] in '[]':
                replaced += element
                count += 1
            if count % 2 != 0 and regex[i] not in '[]':
                replaced += element
            i += 1
            
        regex = regex.replace(replaced, result)
        return regex

    def appeareances(self, string, symbol):
        counter = 0
        for element in string:
            if element == symbol:
                counter += 1

        return counter
    
    # TODO: arreglar el formateo de una lista
    def simple_list(self, list):
        i = 0
        res = '('
        while i < len(list):
            element = list[i]
            if element not in "[]":
                if element == '\\':
                    res += '\\' + list[i + 1] + '|'
                    i += 1
                else:
                    res += element + '|'
            i += 1
        res = res[:len(res) - 1] + ')'
        return res
    
    # TODO: obtener lo que haya antes y despues de [] como el ejemplo de hex de ej3.yal
    def replace_common_patterns(self, regex):
        self.letters = 'abcdefghijklmnopqrstuvwxyz'
        self.upper_letters = self.letters.upper()
        self.numbers = '0123456789'
        regex = regex.replace('ε', ' ')
        self.search_simple_regex_result = re.search(self.simple_pattern, regex)
        self.search_compound_regex_result = re.search(self.compound_pattern, regex)
        self.search_list = re.search(self.list_pattern, regex)
        if self.search_simple_regex_result and not self.search_compound_regex_result:
            regex = self.simple_range(regex)
        elif self.search_compound_regex_result:
            regex = self.compound_range(regex)
        elif self.search_list:
            regex = self.simple_list(regex)

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


    def build_trailer(self):
        if self.check_trailer():
            codigo_bloque = self.file_content.split("tokens =")[-1].split("{\n")[-1].split("}")[0]
            self.trailer_result = codigo_bloque
            temp = '{\n' + codigo_bloque + '}'
            self.file_content = self.file_content.replace(temp, '')
        else:
            self.trailer_result = ''

    def check_trailer(self):
        content = self.file_content.split("rule" + self.token_name + "=")[1]
        i = 0
        acu = ''
        is_rule = False
        quotes = 0
        rules = True
        j = 0
        while j < len(content) and rules:
            element = content[j]
            acu += element
            if element and not self.check_is_blank(element):
                if element == '"' or element == "'":
                    quotes += 1
                if i == 0:
                    is_rule = True
                    i += 1
                else:
                    if element == '|':
                        is_rule = True
                    if element == '}' and is_rule and quotes % 2 == 0:
                        is_rule = False
                    if element == '{' and not is_rule:
                        acu = acu[:-1]
                        rules = False   
            j += 1 
        content = content.replace(acu, '')
        return '{' in content

    def get_header(self):
        return self.header_result

    def get_regex(self):
        pass

    def get_trailer(self):
        return self.trailer_result