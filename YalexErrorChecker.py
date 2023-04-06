import re

class YalexErrorChecker(object):

    def __init__(self) -> None:
        self.errors = []
        self.simple_regex_pattern = r"^let\s+\w+\s+=\s+(.*?)$"

    def check_errors(self, content):
        self.file_content = content
        self.check_unbalanced_parenthesis()
        self.check_unbalanced_comments()
        self.check_unbalanced_brackets()
        self.check_unbalanced_quotation_marks()
        self.check_common_regex()

        return self.errors

    def check_unbalanced_parenthesis(self):
        stack = []
        content = self.file_content.split("\n")
        i = 1
        for line in content:
            j = 0
            while j < len(line):
                element = line[j]
                if element == '(':
                    if j + 1 < len(line) and line[j + 1] != '*':
                        stack.append(element)
                elif element == ')' and line[j - 1] != '*':
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
        i = 1
        for line in content:
            j = 0
            while j < len(line):
                element = line[j]
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

    def check_common_regex(self):
        content = self.file_content.split("\n")
        i = 0
        for line in content:
            if 'let' in line and not re.match(self.simple_regex_pattern, line):
                self.errors.append(f"Error: Invalid declaration of common regex at line {i}.\n")
            i += 1

    # TODO: Chequear error en declaracion de rule. Es decir que diga rule =, en lugar de rule token =.
    #       Tambien que nunca se ponga rule y se declaren tokens.
    #       Tambien que no haya | entre declaracion de tokens.