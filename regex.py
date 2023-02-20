import re
from Node import Node
from AST import AST

class Regex(object):
    def __init__(self, expression) -> None:
        self.alphabet = ['ε']
        self.operators = {'.', '|', '*', '+', '?'}
        self.binarios = {'|'}
        self.expression = expression
        # self.expression = self.expression.replace('?', '|ε')
        whitespace = r"\s+"
        self.expression = re.sub(whitespace, "", self.expression)
        self.AST = AST()
        self.create_alphabet()
        self.add_concatenation_symbol()
        self.check_expression()
        self.build_AST()
    
    def create_alphabet(self):
        for element in self.expression:
            if element not in self.operators and element not in '()':
                self.alphabet.append(element)

    def add_concatenation_symbol(self):
        new_expression = ""
        
        for i in range(len(self.expression)):
            if i + 1 < len(self.expression):
                next = self.expression[i + 1]
                current = self.expression[i]
                new_expression += current
                if (current != "(" and next != ")") and next not in self.operators and current not in self.binarios:
                    new_expression += '.'
            else:
                new_expression += self.expression[i]
        self.expression = new_expression
    
    def check_expression(self):
        binary_operators = '.|'
        unary_operators = '?*+'

        for i in range(len(self.expression)):
            if i + 1 < len(self.expression):
                current = self.expression[i]
                next = self.expression[i + 1]
                if current in binary_operators and next in binary_operators:
                    exception = f"Two binary operators cannot be sequential. At: {current + next}, string index {i}"
                    raise Exception(exception)
                if (current in binary_operators and next in unary_operators):
                    exception = f"Binary operator cannot be followed by unary operator. At: {current + next}, string index {i}"
                    raise Exception(exception)

    def build_tree(self, operand, stack):
        new_node = Node(operand)
        if operand in '*+?':
            o1 = stack.pop()
            if operand == '+':
                new_node.value = '.'
                new_node.set_left_child(o1)
                kleene_node = Node('*')
                kleene_node.set_left_child(o1)
                new_node.set_right_child(kleene_node)
            elif operand == '?':
                new_node.value = '|'
                new_node.set_left_child(o1)
                epsilon_node = Node('ε')
                new_node.set_right_child(epsilon_node)
            else:
                new_node.set_left_child(o1)
        else:
            o2 = stack.pop()
            o1 = stack.pop()
            new_node.set_left_child(o1)
            new_node.set_right_child(o2)
        
        stack.append(new_node)
        return stack

    def otro(self):
        output_stack = []
        output = ""
        operator_stack = []
        operators = ".*+|?"
        for element in self.expression:
            if element in self.alphabet:
                output_stack.append(Node(element))
                output += element
            elif element == '(':
                operator_stack.append(element)
            elif element == ')':
                while operator_stack and operator_stack[-1] != '(':
                    pop_element = operator_stack.pop()
                    output_stack = self.build_tree(pop_element, output_stack)
                    output += pop_element
                if operator_stack and operator_stack[-1] == '(':
                    operator_stack.pop()
                else:
                    raise Exception('Parenthesis not closed in regular expression.')
            elif element in operators:
                while operator_stack and operator_stack[-1] != '(' and self.precedence(element) <= self.precedence(operator_stack[-1]):
                    pop_element = operator_stack.pop()
                    output_stack = self.build_tree(pop_element, output_stack)
                    output += pop_element
                operator_stack.append(element)
            else:
                raise Exception('Symbol not in alphabet or operators')

        while operator_stack:
            pop_element = operator_stack.pop()
            output_stack = self.build_tree(pop_element, output_stack)
            output += pop_element

        if not output_stack:
            raise Exception('Regular expression not valid.')

        return output.replace('?', 'ε|')

    def get_AST(self):
        return self.AST

    def build_AST(self):
        output_stack = []
        output = ""
        operator_stack = []
        operators = ".*+|?"
        for element in self.expression:
            if element in self.alphabet:
                output_stack.append(Node(element))
                output += element
            elif element == '(':
                operator_stack.append(element)
            elif element == ')':
                while operator_stack and operator_stack[-1] != '(':
                    pop_element = operator_stack.pop()
                    output_stack = self.build_tree(pop_element, output_stack)
                    output += pop_element
                if operator_stack and operator_stack[-1] == '(':
                    operator_stack.pop()
                else:
                    raise Exception('Parenthesis not closed in regular expression.')
            elif element in operators:
                while operator_stack and operator_stack[-1] != '(' and self.precedence(element) <= self.precedence(operator_stack[-1]):
                    pop_element = operator_stack.pop()
                    output_stack = self.build_tree(pop_element, output_stack)
                    output += pop_element
                operator_stack.append(element)
            else:
                raise Exception('Symbol not in alphabet or operators')

        while operator_stack:
            pop_element = operator_stack.pop()
            output_stack = self.build_tree(pop_element, output_stack)
            output += pop_element

        if not output_stack:
            raise Exception('Regular expression not valid.')\
        
        root = output_stack.pop()
        self.AST.set_root(root)


    def to_postfix(self):
        return self.AST.postorder()
        
    def get_root(self):
        return self.AST.root

    def precedence(self, element):
        if element in '()':
            return 4
        if element in '*+?':
            return 3
        if element == '.':
            return 2
        if element in '|':
            return 1