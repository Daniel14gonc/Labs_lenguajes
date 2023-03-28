from AST import AST
from STNode import STNode

class ST(AST):
    def __init__(self, regex) -> None:
        super().__init__()
        self.regex = regex
        self.alphabet = regex.alphabet
        self.stack = list(self.regex.to_postfix() + '# ')
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
        if node.value in '| ':
            self.assignment_helper(node.left_child)
            self.assignment_helper(node.right_child)
            if node.value == ' ':
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

        if node.value == '*':
            self.assignment_helper(node.left_child)
            node.nullable = True
            node.first_pos = node.first_pos.union(node.left_child.first_pos)
            node.last_pos = node.last_pos.union(node.left_child.last_pos)
            self.compute_follow_pos(node)
        if node.value in self.alphabet or node.value == '#':
            node.number = self.count
            self.count += 1
            if node.value == 'ε':
                node.nullable = True
            else:
                node.first_pos.add(node.number)
                node.last_pos.add(node.number)
                self.follow_pos[(node.number, node.value)] = set()

    def build_tree(self):
        self.root = self.build_helper()

    def build_helper(self):
        current = self.stack.pop()
        node = STNode(current)
        if current == '#' or current in self.alphabet:
            return node
        elif current in '| ':
            right_child = self.build_helper()
            left_child = self.build_helper()
            node.right_child = right_child
            node.left_child = left_child
        elif current == '*':
            child = self.build_helper()
            node.left_child = child
        elif current == '+':
            child = self.build_helper()
            node.value = ' '
            node.left_child = child
            right_child = STNode('*')
            node.right_child = right_child
            node.right_child.left_child = child
        return node
    
    def get_last_pos(self):
        for key in self.follow_pos:
            if key[1] == '#':
                return key[0]



