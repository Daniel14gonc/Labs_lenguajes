import re
from Node import Node

class Regex(object):
    def __init__(self, expression) -> None:
        self.alphabet = ['ε']
        self.operadores = {'.', '|', '*', '+', '?'}
        self.binarios = {'|'}
        self.expression = expression
        # self.expression = self.expression.replace('?', '|ε')
        whitespace = r"\s+"
        self.expression = re.sub(whitespace, "", self.expression)
        self.create_alphabet()
        self.add_concatenation_symbol()
    
    def create_alphabet(self):
        for element in self.expression:
            if element not in self.operadores and element not in '()':
                self.alphabet.append(element)

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

    def to_posfix(self):
        output_stack = []
        output = ""
        operator_stack = []
        operators = ".*+|"
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
                while operator_stack and operator_stack[-1] != '(' and self.precedence(element) <= self.precedence(operator_stack[-1]):
                    pop_element = operator_stack.pop()
                    output_stack = self.build_tree(pop_element, output_stack)
                    output += pop_element
                operator_stack.append(element)

        while operator_stack:
            pop_element = operator_stack.pop()
            output_stack = self.build_tree(pop_element, output_stack)
            output += pop_element

        # print(output.replace('?', 'ε|'))
        self.root = output_stack.pop()
        # print(self.postorder())

    def postorder(self):
        return self.postorder_helper(self.root)
        

    def postorder_helper(self, node):
        res = ""
        if node:
            if node.value in '?*+':
                res += self.postorder_helper(node.left_child)
            elif node.value in '|.':
                res += self.postorder_helper(node.left_child)
                res += self.postorder_helper(node.right_child)
            return res + node.value
        


    def precedence(self, element):
        if element in '()':
            return 4
        if element in '*+?':
            return 3
        if element == '.':
            return 2
        if element in '|':
            return 1