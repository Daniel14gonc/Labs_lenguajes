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
            elif node.value in '| ':
                res += self.postorder_helper(node.left_child)
                res += self.postorder_helper(node.right_child)
            return res + node.value