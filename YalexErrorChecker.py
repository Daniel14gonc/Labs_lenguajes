import re

class YalexErrorChecker(object):

    def __init__(self) -> None:
        self.errors = []
        self.simple_regex_pattern = r"^let\s+\w+\s+=\s+(.*?)$"
        self.token_regex = r"^\|\s*[\S\s]+\s*\{\s*[\S\s]*\}\s*$"
        self.initial_token_regex = r"^\s*[\S\s]+\s*\{\s*[\S\s]*\}\s*$"

    def check_errors(self, content):
        self.file_content = content
        self.check_unbalanced_parenthesis()
        self.check_unbalanced_comments()
        self.check_unbalanced_brackets()
        self.check_unbalanced_quotation_marks()
        self.check_common_regex()
        self.check_rule_declaration()

        return self.errors

    def check_unbalanced_parenthesis(self):
        stack = []
        content = self.file_content.split("\n")
        i = 1
        is_inside_marks = False
        for line in content:
            j = 0
            while j < len(line):
                element = line[j]
                if element == "'" or element == '"':
                    is_inside_marks = not is_inside_marks
                elif element == '(':
                    if not is_inside_marks:
                        if j + 1 < len(line) and line[j + 1] != '*':
                            stack.append(element)
                elif element == ')' and line[j - 1] != '*':
                    if not is_inside_marks:
                        if stack:
                            stack.pop()
                        else:
                            self.errors.append(f"Error at line {i}: parenthesis mismatch.\n")
                j += 1
            i += 1
        if stack:
            self.errors.append("Error: parenthesis mismatch.\n")

        
    def check_unbalanced_comments(self):
        stack = []
        content = self.file_content.split("\n")
        marks = 0
        i = 1
        for line in content:
            j = 0
            while j < len(line):
                element = line[j]
                if element == '"' or element == "'":
                    marks += 1
                if marks % 2 == 0:
                    if element == '(':
                        if j + 1 < len(line) and line[j + 1] == '*':
                            stack.append(element)
                    elif element == ')' and line[j - 1] == '*':
                        if stack:
                            stack.pop()
                        else:
                            self.errors.append(f"Error at line {i}: comment not closed.\n")
                j += 1
            i += 1
        if stack:
            self.errors.append("Error: comments not closed properly.\n")

    def check_unbalanced_brackets(self):
        stack_curly_brackets = []
        stack_square_brackets = []
        content = self.file_content.split("\n")
        i = 1
        for line in content:
            for element in line:
                if element == '[':
                    stack_square_brackets.append(element)
                if element == '{':
                    stack_curly_brackets.append(element)
                if element == ']':
                    if stack_square_brackets:
                        stack_square_brackets.pop()
                    else:
                        self.errors.append(f"Error at line {i}: square brackets mismatch.\n")
                if element == '}':
                    if stack_curly_brackets:
                        stack_curly_brackets.pop()
                    else:
                        self.errors.append(f"Error at line {i}: curly brackets mismatch.\n")
        if stack_square_brackets:
            self.errors.append("Error: square brackets mismatch.\n")
        if stack_curly_brackets:
            self.errors.append("Error: curly brackets mismatch.\n")

    def check_unbalanced_quotation_marks(self):
        single_marks = 0
        double_marks = 0
        content = self.file_content.split("\n")
        i = 1
        for line in content:
            for element in line:
                if element == "'":
                    single_marks += 1
                if element == '"':
                    double_marks += 1
        if single_marks % 2 != 0:
            self.errors.append("Error: unbalanced simple quotation marks.\n")
        if double_marks % 2 != 0:
            self.errors.append("Error: unbalanced double quotation marks.\n")

    def clean_comments(self, content):
        patron = re.compile(r'\(\*.*?\*\)', re.DOTALL)
        content = re.sub(patron, '', content)
        return content

    def check_common_regex(self):
        content = self.clean_comments(self.file_content)
        content = content.split("\n")
        i = 1
        for line in content:
            if 'let' in line and not re.match(self.simple_regex_pattern, line.strip()):
                self.errors.append(f"Error: Invalid declaration of common regex at line {i}.\n")
            i += 1

    def check_white_spaces(self, string):
        counter = 0
        for element in string:
            if element == ' ' or element == '\t':
                counter += 1
        return counter == len(string)
    
    def check_newline_only(self, string):
        other_symbol = False
        for element in string:
            if element != '\n':
                other_symbol = True
        return not other_symbol

    def check_rule_declaration(self):
        content = self.clean_comments(self.file_content)
        content = content.split('rule')
        if len(content) < 2:
            self.errors.append("Error: Either you defined bad the rule or there are unbalanced comments.\n")
        else:
            tokens_body = content[1]
            codigo_bloque = tokens_body.split("tokens =")[-1].split("{\n")[-1].split("}")[0]
            temp = '{\n' + codigo_bloque + '}'
            tokens_body = tokens_body.replace(temp, '')
            tokens_body = tokens_body.split('=', maxsplit=1)
            if self.check_white_spaces(tokens_body[0]):
                self.errors.append("Error: There is no identifier in rule declaration.\n")

            if self.check_white_spaces(tokens_body[1]) or self.check_newline_only(tokens_body[1]) or not tokens_body[1]:
                self.errors.append("Error: There is no body in rule declaration.\n")

            i = 1
            initial = True
            acu = ''
            for element in tokens_body[1]:
                acu += element
                if element == '}':
                    if not initial:
                        if not re.match(self.token_regex, acu.strip()):
                            self.errors.append(f"Error in token declaration number: {i}")
                    else:
                        if not re.match(self.initial_token_regex, acu.strip()):
                            self.errors.append(f"Error in token declaration number: {i}")
                    initial = False
                    acu = ''
                    i += 1



            # declarations = tokens_body[1].split('\n')
            # for declaration in declarations:
            #     if not self.check_white_spaces(declaration):
            #         if i == 0 and not re.match(self.initial_token_regex, declaration.strip()):
            #             self.errors.append(f"Error in token declaration: {declaration}")
            #         elif i != 0 and not re.match(self.token_regex, declaration.strip()):
            #             self.errors.append(f"Error in token declaration: {declaration}")
            #         i += 1
