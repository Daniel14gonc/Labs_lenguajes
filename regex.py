import re
from Node import Node
from AST import AST
from RegexErrorChecker import RegexErrorChecker

class Regex(object):
    def __init__(self, expression) -> None:
        self.alphabet = ['ε']
        self.operators = {' ', '|', '*', '+', '?'}
        self.binarios = {'|'}
        self.error_checker = RegexErrorChecker(expression)
        self.expression = expression

        
        # if not expression:
        #     error = "Expression empty"
        #     self.error_checker.add_error(error)
        #     raise Exception(self.error_checker.get_error_result())
        
        # whitespace = r"\s+"
        # self.expression = re.sub(whitespace, "", self.expression)
        self.AST = AST()
        self.create_alphabet()
        self.add_concatenation_symbol()
        self.idempotency()
        self.error_checker.check_errors(self.expression, self.alphabet)
        self.build_AST()

        if self.error_checker.get_size() > 0:
            raise Exception(self.error_checker.get_error_result())
        
        self.change_alphabet()

    def create_alphabet(self):
        i = 0
        while i < len(self.expression):
            element = self.expression[i]
            if element == " ":
                self.alphabet.append(" ")
            if element == '\\':
                next = self.expression[i + 1]
                self.alphabet.append(element + next)
                i += 1
            elif element not in self.operators and element not in '()':
                self.alphabet.append(element)
            i += 1

        self.alphabet = list(set(self.alphabet))

        # for element in self.expression:

        #     if element not in self.operators and element not in '()':
        #         self.alphabet.append(element)
        # self.alphabet = list(set(self.alphabet))

    def add_concatenation_symbol(self):
        new_expression = ""
        i = 0
        while i < len(self.expression):
            add_symbol = True
            if i + 1 < len(self.expression):
                next = self.expression[i + 1]
                current = self.expression[i]
                if i + 2 < len(self.expression):
                    if current == '\\' and next != "\\":
                        current += next
                        next = self.expression[i + 2]
                        add_symbol = True
                        i += 1
                else:
                    if current == '\\' and next != "\\":
                        current += next
                        add_symbol = False
                        i += 1
                new_expression += current
                if (current != "(" and next != ")") and next not in self.operators and current not in self.binarios and add_symbol:
                    new_expression += '.'
            else:
                new_expression += self.expression[i]
            i += 1

        self.expression = new_expression

    def idempotency(self):
        self.idempotency_helper('*')
        self.idempotency_helper('+')

    def check_meta_characters(self):
        new_list = []
        i = 0
        while i < len(self.expression):
            element = self.expression[i]
            if element == '\\' and i + 1 < len(self.expression) and self.expression[i + 1] != '\\':
                new_list.append(element + self.expression[i + 1])
                i += 1
            else:
                new_list.append(element)
            i += 1
        return new_list

    def idempotency_helper(self, symbol):
        last = ''
        expression_list = self.check_meta_characters()
        i = 0
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

    def change_alphabet(self):
        list = []
        metas = ['\+', '\.', '\?', '\*', '\(', '\)']
        for element in self.alphabet:
            if element in metas:
                element = element.replace("\\", "")
            list.append(element)
            
        self.alphabet = list

    def build_AST(self):
        output_stack = []
        output = ""
        operator_stack = []
        operators = "*+|?."
        i = 0
        while i < len(self.expression):
            element = self.expression[i]
            if element == '\\':
                element += self.expression[i + 1]
                i += 1
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
            i += 1
            
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