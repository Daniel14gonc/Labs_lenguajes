class Reader(object):

    def __init__(self, path) -> None:
        self.path = path
    
    def read(self):
        file = open(self.path, 'r')
        self.file_content = file.read()
        file.close()
        return self.file_content