from Node import Node

class STNode(Node):
    
    def __init__(self, value) -> None:
        super().__init__(value)
        self.nullable = False
        self.first_pos = set()
        self.last_pos = set()
        self.number = None