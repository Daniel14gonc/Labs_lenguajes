import re

class Regex(object):
    def __init__(self, expression) -> None:
        self.alphabet = set()
        self.operadores = {'.', '|', '*', '+'}
        self.binarios = {'|'}
        self.expression = expression
        self.expression = self.expression.replace('?', '|ε')
        whitespace = r"\s+"
        self.expression = re.sub(whitespace, "", self.expression)
        self.create_alphabet()
        self.add_concatenation_symbol()
        print(self.expression)
    
    def create_alphabet(self):
        for element in self.expression:
            if element not in '()|ε*+':
                self.alphabet.add(element)

    def add_concatenation_symbol(self):
        new_expression = ""
        
        for i in range(len(self.expression)):
            if i + 1 < len(self.expression):
                next = self.expression[i + 1]
                current = self.expression[i]
                new_expression += current
                if (current != "(" and next != ")") and next not in self.operadores and current not in self.binarios:
                    new_expression += '.'
            else:
                new_expression += self.expression[i]
        self.expression = new_expression
    
    def to_posfix(self):

        pass