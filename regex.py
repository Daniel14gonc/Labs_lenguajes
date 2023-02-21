import re
from Node import Node
from AST import AST
from RegexErrorChecker import RegexErrorChecker

class Regex(object):
    def __init__(self, expression) -> None:
        self.alphabet = ['ε']
        self.operators = {'.', '|', '*', '+', '?'}
        self.binarios = {'|'}
        self.error_checker = RegexErrorChecker(expression)
        self.expression = expression

        if '.' in expression:
            error = "Error in expression. Cannot enter '.' as concatenation operator."
            self.error_checker.add_error(error)
            raise Exception(self.error_checker.get_error_result())
        if not expression:
            error = "Expression empty"
            self.error_checker.add_error(error)
            raise Exception(self.error_checker.get_error_result())
        
        whitespace = r"\s+"
        self.expression = re.sub(whitespace, "", self.expression)
        self.AST = AST()
        self.create_alphabet()
        self.add_concatenation_symbol()
        self.idempotency()
        self.error_checker.check_errors(self.expression, self.alphabet)
        self.build_AST()

        if self.error_checker.get_size() > 0:
            raise Exception(self.error_checker.get_error_result())

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

    def idempotency(self):
        self.idempotency_helper('*')
        self.idempotency_helper('+')

    def idempotency_helper(self, symbol):
        last = ''
        expression_list = list(self.expression)
        for i in range(len(expression_list)):
            if expression_list[i] == symbol and last == symbol:
                last = symbol
                expression_list[i] = ''
            else: 
                last = expression_list[i]

        self.expression = ''.join(expression_list)

    def build_tree(self, operator, stack):
        new_node = Node(operator)
        has_error = False
        if operator in '*+?':
            if not stack:
                error = f"Unary operator {operator} is not applied to any symbol."
                self.error_checker.add_error(error)
                has_error = True
            else:
                o1 = stack.pop()
                '''
                if operator == '+':
                    new_node.value = '.'
                    new_node.set_left_child(o1)
                    kleene_node = Node('*')
                    kleene_node.set_left_child(o1)
                    new_node.set_right_child(kleene_node)'''
                if operator == '?':
                    new_node.value = '|'
                    new_node.set_left_child(o1)
                    epsilon_node = Node('ε')
                    new_node.set_right_child(epsilon_node)
                else:
                    new_node.set_left_child(o1)
        elif operator in '|.':
            if not stack or len(stack) == 1:
                error = f"Binary operator {operator} does not have the operators required."
                self.error_checker.add_error(error)
                has_error = True
                if len(stack) == 1:
                    stack.pop()
            else:
                o2 = stack.pop()
                o1 = stack.pop()
                new_node.set_left_child(o1)
                new_node.set_right_child(o2)
        
        if not has_error:
            stack.append(new_node)
        return stack

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
                if operator_stack :
                    operator_stack.pop()
            elif element in operators:
                while operator_stack and operator_stack[-1] != '(' and self.precedence(element) <= self.precedence(operator_stack[-1]):
                    pop_element = operator_stack.pop()
                    output_stack = self.build_tree(pop_element, output_stack)
                    output += pop_element
                
                operator_stack.append(element)
            
        while operator_stack:
            pop_element = operator_stack.pop()
            output_stack = self.build_tree(pop_element, output_stack)
            output += pop_element

        if output_stack:
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