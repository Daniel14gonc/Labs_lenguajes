from LexerBuilder import LexerBuilder

class LexerDirector(object):
    def __init__(self, path = None, file = None) -> None:
        self.path = path if path else 'lexer.yal'
        self.file = file if file else 'resultado.py'
        self.builder = LexerBuilder(self.path, self.file)

    def construct_lexer(self):
        self.builder.read_lexer_file()
        self.builder.get_tokens_from_yalex()
        self.builder.create_NFAS()
        self.builder.errors_exception()
        self.builder.create_tokenizer()
        self.builder.concat_files_needed()
        self.builder.concat_functionality()
        self.builder.write_to_file()