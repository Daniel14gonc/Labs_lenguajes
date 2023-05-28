from lexer_java import tokenizer
from parser_java import slr

input_file = input("Ingrese el nombre del archivo de codigo fuente> ")
tokenizer.read_source_code(input_file)
tokenizer.initialize_token_recognition()
print(slr.parse(tokenizer))
