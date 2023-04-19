clavos = 'abc'

class Reader(object):

    def __init__(self, path) -> None:
        self.path = path
    
    def read(self):
        file = open(self.path, 'r')
        self.file_content = file.read()
        file.close()
        return self.file_content
class Node(object):

    def __init__(self, value) -> None:
        self.value = value
        self.right_child = None
        self.left_child = None
        
    def set_right_child(self, node):
        self.right_child = node
    
    def set_left_child(self, node):
        self.left_child = node
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


class STNode(Node):
    
    def __init__(self, value) -> None:
        super().__init__(value)
        self.nullable = False
        self.first_pos = set()
        self.last_pos = set()
        self.number = None



class ST(AST):
    def __init__(self, regex) -> None:
        super().__init__()
        self.regex = regex
        self.alphabet = regex.alphabet
        self.stack = list(self.regex.to_postfix() + '\#.')
        self.follow_pos = {}
        self.build_tree()
        self.count = 1
        self.post_order_assignment()
    
    def post_order_assignment(self):
        self.assignment_helper(self.root)

    def compute_follow_pos(self, node):
        if node.value == '*':
            child = node.left_child
            last_pos = child.last_pos
            for element in last_pos:
                for key in self.follow_pos:
                    if element in key:
                        self.follow_pos[key] = self.follow_pos[key].union(child.first_pos)
        else:
            right_child = node.right_child
            left_child = node.left_child
            last_pos = left_child.last_pos
            for element in last_pos:
                for key in self.follow_pos:
                    if element in key:
                        self.follow_pos[key] = self.follow_pos[key].union(right_child.first_pos)
        
    def get_followpos_table(self):
        return self.follow_pos
    
    def assignment_helper(self, node):
        if node.value in '|.':
            self.assignment_helper(node.left_child)
            self.assignment_helper(node.right_child)
            if node.value == '.':
                if node.left_child.nullable:
                    childs_first_pos = node.left_child.first_pos.union(node.right_child.first_pos)
                    node.first_pos = childs_first_pos
                else:
                    node.first_pos = node.left_child.first_pos

                if node.right_child.nullable:
                    childs_last_pos = node.left_child.last_pos.union(node.right_child.last_pos)
                    node.last_pos = childs_last_pos
                else:
                    node.last_pos = node.right_child.last_pos
                node.nullable = node.right_child.nullable and node.left_child.nullable
                self.compute_follow_pos(node)
            else:
                node.first_pos = node.left_child.first_pos.union(node.right_child.first_pos)
                node.last_pos = node.left_child.last_pos.union(node.right_child.last_pos)
                node.nullable = node.right_child.nullable or node.left_child.nullable

        elif node.value == '*':
            self.assignment_helper(node.left_child)
            node.nullable = True
            node.first_pos = node.first_pos.union(node.left_child.first_pos)
            node.last_pos = node.last_pos.union(node.left_child.last_pos)
            self.compute_follow_pos(node)
        
        elif self.is_in_alphabet(node.value) or node.value == '\#':
            node.number = self.count
            self.count += 1
            if node.value == 'ε':
                node.nullable = True
            else:
                node.first_pos.add(node.number)
                node.last_pos.add(node.number)
                self.follow_pos[(node.number, self.replace_meta(node.value))] = set()

    def is_in_alphabet(self, value):
        if value in self.alphabet:
            return True
        operators = "*.+()"
        for operator in operators:
            if operator in value:
                return True
        return False
    
    def replace_meta(self, value):
        operators = "*.+()"
        for operator in operators:
            if operator in value:
                value = value.replace('\\', '')
        return value

    def build_tree(self):
        self.root = self.build_helper()

    def build_helper(self):
        current = self.stack.pop()
        if len(self.stack) >= 1 and current != '\\' and self.stack[-1] == '\\':
            current = self.stack.pop() + current
        node = STNode(current)
        if current == '\#' or current in self.alphabet:
            return node
        elif current in '|.':
            right_child = self.build_helper()
            left_child = self.build_helper()
            node.right_child = right_child
            node.left_child = left_child
        elif current == '*':
            child = self.build_helper()
            node.left_child = child
        elif current == '+':
            child = self.build_helper()
            node.value = '.'
            node.left_child = child
            right_child = STNode('*')
            node.right_child = right_child
            node.right_child.left_child = child
        return node
    
    def get_last_pos(self):
        for key in self.follow_pos:
            if key[1] == '\#':
                return key[0]




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
                    string_between_parenthesis.append("a")
                elif j == 0:
                    stack.append(element)
                    string_between_parenthesis.append("a")
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
        
        # self.change_alphabet()

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
        metas = ['\+', '\.', '\?', '\*', '\(', '\)', '\#']
        for element in self.alphabet:
            if element in metas:
                element = element.replace("\\", "")
            list.append(element)
        return list
        # self.alphabet = list

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

from ST import ST


class DFA(FA):

    def __init__(self, regex = None, count = 1) -> None:
        super().__init__(regex)
        self.dead_state = None
        self.temp_transitions = None
        if regex:
            self.build_direct(count)

        self.error_checker = FAErrorChecker()

    def build_direct(self, counter):
        self.count = counter
        tree = ST(self.regex)
        self.alphabet = self.regex.change_alphabet().copy()
        table = tree.get_followpos_table()
        first_state = frozenset(tree.root.first_pos)
        self.create_special_alphabet()
        states = {first_state: self.count}
        unmarked_states = [first_state]
        self.build_matrix_entry(self.count)
        self.count += 1
        pos_augmented = tree.get_last_pos()
        self.initial_states.add(states[first_state])
        if pos_augmented in first_state:
            self.acceptance_states.add(states[first_state])

        while unmarked_states:
            S = unmarked_states.pop()
            for symbol in self.special_alphabet:
                U = set()
                for state in S:
                    if (state, symbol) in table:
                        U = U.union(table[(state, symbol)])
                            
                U = frozenset(U)
                if U not in states:
                    states[U] = self.count
                    if not U:
                        self.dead_state = self.count
                    self.build_matrix_entry(self.count)
                    unmarked_states.append(U)
                    self.count += 1
                self.create_transition(states[S], states[U], symbol)
                if pos_augmented in U:
                    self.acceptance_states.add(states[U])

        self.alphabet = self.special_alphabet
        self.temp_transitions = self.transitions
        self.delete_dead_state()
        self.set_external_transitions(self.transitions)

    def build_from_NFA(self, NFA):
        self.regex = NFA.regex
        self.alphabet = NFA.alphabet
        self.external_transitions = NFA.transitions
        self.create_special_alphabet()
        count_states = 1
        D_states = {}
        first_state = frozenset(self.e_closure(NFA.initial_states))
        D_states[first_state] = count_states
        self.build_matrix_entry(D_states[first_state])
        unmarked_states = [first_state]
        count_states += 1

        self.initial_states = {D_states[first_state]}
        

        while unmarked_states:
            T = unmarked_states.pop()
            self.check_special_state(T, NFA, D_states[T])
            for symbol in self.special_alphabet:
                U = frozenset(self.e_closure(self.move(T, symbol)))
                if U not in D_states:
                    D_states[U] = count_states
                    if not U:
                        self.dead_state = count_states
                    unmarked_states.append(U)
                    count_states += 1
            
                if D_states[U] not in self.transitions:
                    self.build_matrix_entry(D_states[U])
                self.create_transition(D_states[T], D_states[U], symbol) 
        self.alphabet = self.special_alphabet
        self.temp_transitions = self.transitions
        self.delete_dead_state()
        self.set_external_transitions(self.transitions)

    def check_special_state(self, state, NFA, representation):
        for element in state:
            if element in NFA.acceptance_states:
                self.acceptance_states.add(representation)
    
    def create_special_alphabet(self):
        self.special_alphabet = [element for element in self.alphabet]
        self.special_alphabet.remove('ε')

    def get_symbol_index_special(self, symbol):
         for i in range(len(self.special_alphabet)):
            if self.special_alphabet[i] == symbol:
                return i

    def create_transition(self, initial_states, acceptance_states, symbol):
        symbol_index = self.get_symbol_index_special(symbol)
        self.transitions[initial_states][symbol_index].add(acceptance_states)

    def build_matrix_entry(self, state):
        entry = [set() for element in self.special_alphabet]
        self.transitions[state] = entry

    def delete_dead_state(self):
        transitions = self.transitions.copy()
        for transition in self.transitions:
            if transition == self.dead_state:
                transitions.pop(transition)
            else:
                new_element = []
                for element in self.transitions[transition]:
                    if self.dead_state in element:
                        new_element.append(set())
                    else:
                        new_element.append(element)
                transitions[transition] = new_element
        
        self.transitions = transitions
    
    def get_initial_partition(self):
        states = self.get_states(self.temp_transitions)
        acceptance = frozenset({state for state in states if state in self.acceptance_states})
        non_acceptance = frozenset(states - acceptance)
        partition = {acceptance, non_acceptance}
        return partition

    def get_group(self, element, groups, symbol):
        index = self.get_symbol_index_special(symbol)
        transition = list(self.temp_transitions[element][index])[0]
        for group in groups:
            if transition in group:
                return list(group)
            
    def check_equal(self, tag):
        last = tag[0]
        for element in tag:
            if element != last:
                return False
            last = element
        
        return True

    def create_partition(self, group, group_tag):
        group_dict_helper = {}
        for i in range(len(group_tag)):
            tag = tuple(group_tag[i])
            element = group[i]
            if tag in group_dict_helper:
                group_dict_helper[tag].add(element)
            else:
                group_dict_helper[tag] = {element}

        new_partition = set()
        for key in group_dict_helper:
            new_partition.add(frozenset(group_dict_helper[key]))

        return new_partition

    def create_new_partition(self, group, partition):
        groups = list(partition)
        group_list = list(group)
        for symbol in self.alphabet:
            group_tag = []
            for element in group_list:
                group_tag.append(self.get_group(element, groups, symbol))
            if not self.check_equal(group_tag):
                return self.create_partition(group_list, group_tag)
           
        return {group}
                
    def representatives(self, partition):
        table = {}
        representatives = []
        initial = list(self.initial_states)[0]
        for element in partition:
            if element:
                representative = None
                if self.dead_state in element:
                    representative = self.dead_state
                if initial in element:
                    representative = initial
                else:
                    representative = list(element)[0]
                table[element] = representative
                representatives.append(representative)

        return representatives, table

    def get_transition_representative(self, element, table):
        element = list(element)[0]
        for key in table:
            if element in key:
                return table[key]

    def build_new_transitions(self, partition):
        representatives, table = self.representatives(partition)
        transitions = {}
        for element in representatives:
            if element not in transitions:
                transitions[element] = [set() for element in self.alphabet]
            for symbol in self.alphabet:
                index = self.get_symbol_index(symbol)
                state = self.temp_transitions[element][index]
                transition_representative = self.get_transition_representative(state, table)
                transitions[element][index].add(transition_representative)

        self.transitions = transitions


    def minimize(self):
        partition = self.get_initial_partition()
        final_partition = self.hopcroft(partition)
        self.build_new_transitions(final_partition)
        self.delete_dead_state()
        self.set_external_transitions(self.transitions)


    def hopcroft(self, partition):
        partition_new = list(partition.copy())
        for group in partition:
            if group:
                new_group = self.create_new_partition(group, partition)
                partition_new.remove(group)
                for element in new_group:
                    partition_new.append(element)
        
        partition_new = set(partition_new)
        
        if partition_new == partition:
            return partition
        else:
            return self.hopcroft(partition_new)
    
    def get_states_with_symbol(self, states, symbol):
        index = self.get_symbol_index(symbol)
        result = set()
        for element in states:
            for state in self.transitions:
                if element in self.transitions[state][index]:
                    result.add(state)
        
        return result

    def get_states(self, transitions):
        return {state for state in transitions}
    
    def simulate(self, string):
        # self.error_checker.check_alphabet_errors(string, self.alphabet)
        s = self.initial_states
        string = 'ε' if not string else string
        for element in string:
            if element not in self.alphabet:
                return False
            if element != 'ε':
                s = self.move(s, element)
            
        if s.intersection(self.acceptance_states):
            return True
        return False 




class NFA(FA):

    def __init__(self, regex = None, count = 1) -> None:
        super().__init__(regex)
        self.count = count
        self.metas = ['\+', '\.', '\?', '\*', '\(', '\)']
        self.root = self.regex.get_root()
        self.build_afn()
        self.error_checker = FAErrorChecker()

    
    def build_afn(self):
        self.alphabet = self.regex.change_alphabet().copy()
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
        s = self.e_closure(self.initial_states)
        string = 'ε' if not string else string
        i = 0
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

import pandas as pd
import re

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

    def edit_meta_alphabet(self):
        list = ["\\+", "\\.", "\\*", "\\(", "\\)"]
        new_alphabet = []
        for element in self.alphabet:
            if "\\" in element and element not in list:
                new_element = element[1]
                new_element = '\\' + new_element
                escape = new_element.encode().decode('unicode_escape')
                new_alphabet.append(escape)
            else:
                new_alphabet.append(element)
        self.alphabet = new_alphabet

    def set_actions(self, actions):
        self.actions = actions

    def begin_simulation(self):
        self.accepted_states = set()
        self.s = self.e_closure(self.initial_states)

    def simulate_symbol(self, symbol):
        symbol = 'ε' if not symbol else symbol
        self._next_transition(symbol)
    
    def is_accepted(self):
        self.accepted_states = self.s.intersection(self.acceptance_states)
        if self.accepted_states:
            return True
        
        return False

    def get_token(self):
        tokens = []
        for state in self.accepted_states:
            for key in self.actions:
                if state in key:
                    tokens.append(self.actions[key])

        min = float('inf')
        max_token = None
        for token in tokens:
            if token[0] < min:
                min = token[0]
                max_token = token[1]
        
        return max_token

    def has_transitions(self):
        for state in self.s:
            transitions = self.transitions[state]
            for resultant_state in transitions:
                if resultant_state != set():
                    return True
        
        return False


    def _next_transition(self, symbol):
        element = symbol
        if element not in self.alphabet:
            self.s = set()
        if element != 'ε':
            self.s = self.e_closure(self.move(self.s, element))
regexes = ['( |\t|\n)+','(0|1|2|3|4|5|6|7|8|9)+','(0|1|2|3|4|5|6|7|8|9)+(\.(0|1|2|3|4|5|6|7|8|9)+)','\+','\*','\(','\)','-','/','=','eof','if','then','else','while','for','(a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z)((a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z)|(0|1|2|3|4|5|6|7|8|9))*','"(0|1|2|3|4|5|6|7|8|9)+']
actions_tokens = [(0, 'print(clavos)'), (1, "print( 'INTEGER' )"), (2, "print( 'FLOAT' )"), (3, "print( 'PLUS' )"), (4, "print( 'POR' )"), (5, "print( 'LPAREN' )"), (6, "print( 'RPAREN' )"), (7, "print( 'MINUS' )"), (8, "print( 'DIV' )"), (9, "print( 'EQUALS' )"), (10, "print( 'EOF' )"), (11, "print( 'IF' )"), (12, "print( 'THEN' )"), (13, "print( 'ELSE' )"), (14, "print( 'WHILE' )"), (15, "print( 'FOR' )"), (16, "print( 'IDENTIFICADOR' )"), (17, "print( 'HEX' )")]

count = 1
NFAs = []
priority = 0
actions = {}
for regex in regexes:
    regex = Regex(regex)
    dfa = DFA(regex, count)
    dfa.minimize()
    count = dfa.count
    NFAs.append(dfa)
    final_states = dfa.acceptance_states
    final_states = frozenset(final_states)
    actions[final_states] = actions_tokens[priority]
    priority += 1


tokenizer = Tokenizer()
for nfa in NFAs:
    tokenizer.concatenate_FA(nfa)
tokenizer.edit_meta_alphabet()


def evaluate_file(path):
    content = Reader(path).read()
    return content


def output_tokens(tokens):
    for token in tokens:
        exec(token)


import sys

args = sys.argv

path = None
if len(args) > 1: 
    path = args[1]
else:
    raise Exception("Source code not specified.")
tokenizer.set_actions(actions)
source = evaluate_file(path)
initial = 0
advance = 0
latest_token = None
line = 0
line_pos = -1
errors = []
tokens = []

while initial < len(source):
    advance = initial
    tokenizer.begin_simulation()
    longest_lexeme = False
    latest_token = None
    while not longest_lexeme and advance < len(source):
        symbol = source[advance]
        tokenizer.simulate_symbol(symbol)
        accepted = tokenizer.is_accepted()
        has_transitions = tokenizer.has_transitions()
        longest_lexeme = not (accepted or has_transitions)
        if not (longest_lexeme and latest_token):
            latest_token = tokenizer.get_token()
            advance += 1
            line_pos += 1
            if symbol == '\n':
                line += 1
                line_pos = -1

    if latest_token:
        tokens.append(latest_token)
    else:
        errors.append(f"Lexical error on line {line} at position {line_pos}.\n")
    initial = advance

if errors:
    error_output = "\nLexical errors:\n"
    for error in errors:
        error_output += error
    raise Exception(error_output)

output_tokens(tokens)

import re

