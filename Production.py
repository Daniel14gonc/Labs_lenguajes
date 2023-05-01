class Production(object):
    def __init__(self, head, body) -> None:
        self.head = head
        self.body = body

    def get_attributes(self):
        return self.head, self.body
    
    def __repr__(self) -> str:
        return self.head + " -> " + " ".join(element for element in self.body)