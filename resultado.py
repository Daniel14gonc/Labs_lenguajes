class AST(object):
    
    def set_root(self, node):
        self.root = node

    def postorder(self):
        return self.postorder_helper(self.root).replace('?', 'ε|')
        
    def postorder_helper(self, node):
        res = ""
        if node:
            if node.value in '?*+':
                res += self.postorder_helper(node.left_child)
            elif node.value in '|.':
                res += self.postorder_helper(node.left_child)
                res += self.postorder_helper(node.right_child)
            return res + node.value
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
        # self.check_alpha_numeric()

    def check_parenthesis(self):
        stack = []
        i = 0
        string_between_parenthesis = [""]
        j = 0
        while j < len(self.expression):
            element = self.expression[j]
            if element == '(':
                if j > 0 and self.expression[j - 1] != '\\':
                    stack.append(element)
                    string_between_parenthesis.append("")
                elif j == 0:
                    stack.append(element)
                    string_between_parenthesis.append("")
            elif element == ')':
                if j > 0 and self.expression[j - 1] != "\\":
                    if not stack:
                        error = f"Parenthesis mismatch at index: {i}."
                        self.error_logs.append(error)
                    else:
                        stack.pop()
                        last_string = string_between_parenthesis.pop()
                        if not last_string:
                            error = f"Parenthesis do not have anything between them."
                            self.error_logs.append(error)
                elif j == 0:
                    error = f"Parenthesis mismatch at index: {i}."
                    self.error_logs.append(error)
            else:
                string_between_parenthesis[-1] += element
            
            i += 1
            j += 1

        if stack:
            error = f"Parenthesis mismatch."
            self.error_logs.append(error)

    def check_sequence_operators(self):
        i = 0
        while i < len(self.expression):
            if i + 1 < len(self.expression):
                current = self.expression[i]
                next = self.expression[i + 1]
                if i + 2 < len(self.expression):
                    current += next
                    next = self.expression[i + 2]
                    i += 1
                if current in self.binary and next in self.binary:
                    error = f"Binary operator followed by another binary operator at index: {i}."
                    self.error_logs.append(error)
                if current in self.binary and next in self.unary:
                    error = f"Binary operator followed by unary operator at index: {i}."
                    self.error_logs.append(error)
            i += 1

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
    
    def check_alpha_numeric(self):
        alpha_numeric = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.|*+(), "
        for element in self.expression:
            if element not in alpha_numeric:
                error = f"Value {element} is not alphanumeric."
                self.error_logs.append(error)
import graphviz

class AFVisual(object):

    def __init__(self, path) -> None:
        self.visual_graph = graphviz.Digraph(format='png', graph_attr={'rankdir':'LR'}, name=path)
        self.visual_graph.node('fake', style='invisible')
    
    def set_AF(self, AF):
        self.initial_states = AF.initial_states
        self.acceptance_states = AF.acceptance_states
        self.transitions = AF.transitions
        self.alphabet = AF.alphabet
        

    def build_graph(self):
        first = None
        for element in self.initial_states:
            first = element
        self.bfs(first)

        self.output_graph()

    def bfs(self, first):
        current_nodes = set()
        visited = set()
        queue = []
        queue.append(first)
        visited.add(first)

        while queue:
            state = queue.pop(0)
            self.visit(state, current_nodes)
            
            for transition in self.transitions[state]:
                if transition:
                    for element in transition:
                        if element not in visited:
                            queue.append(element)
                            visited.add(element)

    def visit(self, state, current_nodes):
        current_nodes.add(state)
        if state in self.acceptance_states:
            self.visual_graph.node(str(state), shape="doublecircle")
        if state in self.initial_states:
            self.visual_graph.edge("fake", str(state), style="bold")
            self.visual_graph.node(str(state), root="true")
        else:
            self.visual_graph.node(str(state))

        transitions = self.transitions[state]
        i = 0
        for set in transitions:
            if set:
                for element in set:
                    if element not in current_nodes:
                        self.visual_graph.node(str(element))
                        current_nodes.add(element)
                    
                    self.visual_graph.edge(str(state), str(element), label=str(self.alphabet[i]))
            i += 1       

    def output_graph(self):
        self.visual_graph.render(directory='output', view=False)
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
class FAErrorChecker(object):
    
    def check_alphabet_errors(self, string, alphabet):
        self.errors = []
        for i in range(len(string)):
            if string[i] not in alphabet and string[i] != 'ε':
                error = f"Character {string[i]} does not belong to alphabet at position {i}.\n"
                self.errors.append(error)
        if self.errors:
            raise Exception(self.to_string())

    def to_string(self):
        res = '\n'
        for error in self.errors:
            res += error

        return res
from AFVisual import AFVisual
import pandas as pd
import dataframe_image as dfi

class FA(object):
    def __init__(self, regex = None) -> None:
        if regex:
            self.regex = regex
            self.alphabet = regex.alphabet
        self.count = 1
        self.transitions = {}
        self.initial_states = set()
        self.acceptance_states = set()
        self.external_transitions = None
    
    def create_AFvisual(self, path):
        self.visual_graph = AFVisual(path)

    def get_symbol_index(self, symbol):
        for i in range(len(self.alphabet)):
            if self.alphabet[i] == symbol:
                return i
            
    def move(self, states, symbol):
        result = set()
        transitions = self.external_transitions.copy() if self.external_transitions else self.transitions.copy()
        for state in states:
            index = self.get_symbol_index(symbol)
            transition = transitions[state]
            states_reached = transition[index]
            for element in states_reached:
                result.add(element)
        return result


    def e_closure(self, states):
        transitions = self.external_transitions.copy() if self.external_transitions else self.transitions.copy()
        stack = []
        for state in states:
            stack.append(state)
        
        result = states.copy()
        while stack:
            t = stack.pop()
            transition = transitions[t]
            index = self.get_symbol_index('ε')
            states_reached = transition[index]
            for element in states_reached:
                if element not in result:
                    result.add(element)
                    stack.append(element)
        return result

    def output_image(self, path=None):
        if not path:
            path = "FA"
       
        self.create_AFvisual(path)
        self.visual_graph.set_AF(self)
        self.visual_graph.build_graph()

    def set_external_transitions(self, transitions):
        self.external_transitions = transitions

    def create_table(self, path):
        df = pd.DataFrame.from_dict(self.transitions, orient = 'index', columns=self.alphabet)
        dfi.export(df, 'tables/' + path + '.png')
from FA import FA
from DFA import DFA
from FAErrorChecker import FAErrorChecker

class NFA(FA):

    def __init__(self, regex = None, count = 1) -> None:
        super().__init__(regex)
        self.count = count
        self.metas = ['\+', '\.', '\?', '\*', '\(', '\)']
        self.root = self.regex.get_root()
        self.build_afn()
        self.error_checker = FAErrorChecker()

    
    def build_afn(self):
        first, last = self.build_helper(self.root)
        self.initial_states.add(first)
        self.acceptance_states.add(last)

    def build_helper(self, node):
        if node:
            if node.value == '*':
                child = self.build_helper(node.left_child)
                return self.create_kleene(child)
            elif node.value == '+':
                child = self.build_helper(node.left_child)
                return self.create_positive_closure(child)
            elif node.value in '|.':
                left = self.build_helper(node.left_child)
                right = self.build_helper(node.right_child)
                if node.value == '|':
                    return self.create_or(left, right)
                else:
                    return self.create_concatenation(left, right)
            else:
                return self.create_unit(node)
    
    def create_positive_closure(self, child):
        first = self.count
        self.count += 1
        last = self.count
        self.count += 1

        self.build_matrix_entry(first)
        self.build_matrix_entry(last)

        self.create_transition(first, child[0], 'ε')
        self.create_transition(child[1], child[0], 'ε')
        self.create_transition(child[1], last, 'ε')

        return first, last


    def create_kleene(self, child):
        first = self.count
        self.count += 1
        last = self.count
        self.count += 1

        self.build_matrix_entry(first)
        self.build_matrix_entry(last)

        self.create_transition(first, child[0], 'ε')
        self.create_transition(first, last, 'ε')
        self.create_transition(child[1], child[0], 'ε')
        self.create_transition(child[1], last, 'ε')
        
        return first, last
    
    def create_or(self, left, right):
        first = self.count
        self.count += 1
        last = self.count
        self.count += 1

        self.build_matrix_entry(first)
        self.build_matrix_entry(last)

        self.create_transition(first, left[0], 'ε')
        self.create_transition(first, right[0], 'ε')
        self.create_transition(left[1], last, 'ε')
        self.create_transition(right[1], last, 'ε')

        return first, last

    def create_concatenation(self, left, right):
        self.replace_transitions(right[0], left[1])

        return left[0], right[1]
    
    def replace_transitions(self, old_state, new_state):
        new_state_transitions = self.transitions[new_state]
        
        for i in range(len(self.transitions[old_state])):
            new_state_transitions[i] = new_state_transitions[i].union(self.transitions[old_state][i])
        
        self.transitions.pop(old_state)

    def create_unit(self, node):
        symbol = node.value
        symbol = symbol.replace("\\", "") if symbol in self.metas else symbol
        first = self.count
        self.count += 1
        last = self.count
        self.count += 1

        self.build_matrix_entry(first)
        self.build_matrix_entry(last)
        self.create_transition(first, last, symbol)

        return first, last

    def convert_to_DFA(self):
        dfa = DFA()
        dfa.build_from_NFA(self)
        
        return dfa
    
    def create_transition(self, initial_states, acceptance_states, symbol):
        symbol = symbol.replace("\\", "") if symbol in self.metas else symbol
        symbol_index = self.get_symbol_index(symbol)
        self.transitions[initial_states][symbol_index].add(acceptance_states)

    def build_matrix_entry(self, state):
        entry = [set() for element in self.alphabet]
        self.transitions[state] = entry

    def simulate(self, string):
        # self.error_checker.check_alphabet_errors(string, self.alphabet)
        s = self.e_closure(self.initial_states)
        string = 'ε' if not string else string
        i = 0
        print(string)
        print(self.alphabet)
        while i < len(string):
            element = string[i]
            if element == '\\':
                element += string[i + 1]
                i += 1
            if element not in self.alphabet:
                return False
            if element != 'ε':
                s = self.e_closure(self.move(s, element))

            i += 1

        if s.intersection(self.acceptance_states):
            return True
        return False 

from NFA import NFA
from regex import Regex
import pandas as pd

# Función para convertir sets a listas
def set_to_tuple(val):
    if isinstance(val, set):
        return tuple(val)
    else:
        return val
    
def tuple_to_set(val):
    if isinstance(val, tuple):
        return set(val)
    else:
        return val

def replace_empty(val):
    if val == '':
        return tuple()
    else:
        return val

class Tokenizer(NFA):
    
    def __init__(self, regex=None, count=1) -> None:
        temp_regex = Regex('a')
        super().__init__(temp_regex, 0)
        self.transitions = {}
        self.initial_states.add(0)
        self.alphabet = ['ε']
        self.build_matrix_entry(0)
        self.acceptance_states = set()
        self.tokens = {}

    def concatenate_FA(self, FA):
        other_alphabet = FA.alphabet.copy()
        other_transitions = FA.transitions.copy()
        other_acceptance_states = FA.acceptance_states.copy()
        self.acceptance_states = self.acceptance_states.union(other_acceptance_states)
        other_initial_states = FA.initial_states
        self.create_initial_transition(other_initial_states)
        self.merge_transitions(other_transitions, other_alphabet)

    def create_initial_transition(self, initial_states):
        initial = list(initial_states)[0]
        self.create_transition(0, initial, 'ε')

    def build_extra_columns(self, df, other_alphabet, common_keys):
        missing_keys = set(other_alphabet) - set(common_keys)
        if missing_keys:
            for key in missing_keys:
                df[key] = ''

    def merge_transitions(self, new_table, new_alphabet):
        common_keys = list(set(new_alphabet).intersection(set(self.alphabet)))

        other_table = pd.DataFrame.from_dict(new_table, orient = 'index', columns=new_alphabet)
        other_table = other_table.applymap(set_to_tuple)
        self.build_extra_columns(other_table, self.alphabet, common_keys)
        table = pd.DataFrame.from_dict(self.transitions, orient = 'index', columns=self.alphabet)
        table = table.applymap(set_to_tuple)
        self.build_extra_columns(table, new_alphabet, common_keys)

        other_table = other_table.applymap(replace_empty)
        table = table.applymap(replace_empty)

        merged = pd.concat([table, other_table])
        merged = merged.applymap(tuple_to_set)
        self.alphabet = list(merged.columns)
        self.transitions = merged.apply(lambda row: row.tolist(), axis=1).to_dict()
regexes = ['(a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z),((a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z)|(0|1|2|3|4|5|6|7|8|9))*','-?(0|1|2|3|4|5|6|7|8|9)++++','\++','\*','a|b','(\(|-?(0|1|2|3|4|5|6|7|8|9)++++)*']

count = 1
NFAs = []
for regex in regexes:
    regex = Regex(regex)
    nfa = NFA(regex, count)
    count = nfa.count
    NFAs.append(nfa)


count = 1
NFAs = []
for regex in regexes:
    regex = Regex(regex)
    nfa = NFA(regex, count)
    count = nfa.count
    NFAs.append(nfa)


tokenizer = Tokenizer()
for nfa in NFAs:
    tokenizer.concatenate_FA(nfa)
tokenizer.output_image()

