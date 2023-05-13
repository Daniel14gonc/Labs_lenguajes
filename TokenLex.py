class TokenLex(object):
    def __init__(self, type, line, position) -> None:
        self.type = type
        self.line = line
        self.position = position
    
    def __repr__(self) -> str:
        return self.type