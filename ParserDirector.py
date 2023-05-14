from ParserBuilder import ParserBuilder

class ParserDirector(object):
    
    def __init__(self, yapar, yalex) -> None:
        self.parser_builder = ParserBuilder(yapar, yalex)

    def construct_parser(self):
        self.parser_builder.get_token_names()
        self.parser_builder.read_yapar_file()
        self.parser_builder.format_yapar()
        # self.parser_builder.check_errors()
        self.parser_builder.convert_productions()
        self.parser_builder.create_SLR()
        self.parser_builder.build_LR_automaton()
        self.parser_builder.build_SLR()
        self.parser_builder.parse()