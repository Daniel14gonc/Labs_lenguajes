from LexerBuilder import LexerBuilder

class LexerDirector(object):
    def __init__(self, path = None) -> None:
        self.path = path if path else 'lexer.yal'
        self.builder = LexerBuilder(self.path)

    def construct_lexer(self):
        self.builder.read_lexer_file()
        self.builder.get_tokens_from_yalex()
        self.builder.create_NFAS()
        self.builder.create_tokenizer()
        self.builder.concat_files_needed()
        self.builder.concat_functionality()
        self.builder.write_to_file()