from AF import AF

class AFN(AF):

    def __init__(self, regex=None) -> None:
        super().__init__(regex)
        self.root = self.regex.root
        self.build_afn()

    
    def build_afn(self):
        self.build_helper(self.root)
    
    def get_symbol_index(self, symbol):
        for i in range(len(self.alphabet)):
            if self.alphabet[i] == symbol:
                return i

    def build_helper(self, node):
        res = ""
        if node:
            print(node.value)
            if node.value == '*':
                res += self.build_helper(node.left_child)
            elif node.value == '+':
                res += self.build_helper(node.left_child)
            elif node.value == '?':
                res += self.build_helper(node.left_child)
            elif node.value in '|.':
                left = self.build_helper(node.left_child)
                right = self.build_helper(node.right_child)
                self.create_concatenation(node, left, right)
            else:
                return self.create_unit(node)
        
    def create_concatenation(self, node, left, right):
        symbol = 'ε'
        self.create_transition(left[1], right[0], symbol)
        return left[0], right[1]

    def create_unit(self, node):
        symbol = node.value
        first = self.count
        self.count += 1
        last = self.count
        self.count += 1

        self.build_matrix_entry(first)
        self.build_matrix_entry(last)
        self.create_transition(first, last, symbol)

        return first, last
    
    def create_transition(self, initial, final, symbol):
        symbol_index = self.get_symbol_index(symbol)
        self.transitions[initial][symbol_index].add(final)

    def build_matrix_entry(self, state):
        entry = [set() for element in self.alphabet]
        self.transitions[state] = entry