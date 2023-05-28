class TokenLex(object):
    def __init__(self, type, line, position, value) -> None:
        self.type = type
        self.line = line
        self.position = position
        self.value = value
    
    def __repr__(self) -> str:
        return self.type + ": " + self.value