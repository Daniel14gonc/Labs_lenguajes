class RegexErrorChecker(object):
    def __init__(self, expression) -> None:
        self.error_logs = []
        self.binary = '.|'
        self.unary = '?*+'
        self.original_expression = expression
    
    def check_errors(self, expression, alphabet):
        self.expression = expression
        self.alphabet = alphabet
        self.check_parenthesis()
        self.check_sequence_operators()
        self.check_ends_expression()

    def check_parenthesis(self):
        stack = []
        i = 0
        string_between_parenthesis = [""]
        for element in self.expression:
            if element == '(':
                stack.append(element)
                string_between_parenthesis.append("")
            elif element == ')':
                if not stack:
                    error = f"Parenthesis mismatch at index: {i}."
                    self.error_logs.append(error)
                else:
                    stack.pop()
                    last_string = string_between_parenthesis.pop()
                    if not last_string:
                        error = f"Parenthesis do not have anything between them."
                        self.error_logs.append(error)
            elif element in self.alphabet:
                string_between_parenthesis[-1] += element
            i += 1

    def check_sequence_operators(self):
        for i in range(len(self.expression)):
            if i + 1 < len(self.expression):
                current = self.expression[i]
                next = self.expression[i + 1]
                if current in self.binary and next in self.binary:
                    error = f"Binary operator followed by another binary operator at index: {i}."
                    self.error_logs.append(error)
                if current in self.binary and next in self.unary:
                    error = f"Binary operator followed by unary operator at index: {i}."
                    self.error_logs.append(error)

    def check_ends_expression(self):
        if self.expression[0] in (self.binary + self.unary):
            error = r"Operator at beginning of expression."
            self.error_logs.append(error)

    def add_error(self, error):
        self.error_logs.append(error)
    
    def get_size(self):
        return len(self.error_logs)
    
    def get_error_logs(self):
        return self.error_logs
    
    def get_error_result(self):
        exception = f"In expression {self.original_expression} \n"
        exception += ''.join(f'{error}\n' for error in self.error_logs)
        
        return exception