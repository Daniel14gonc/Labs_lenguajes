lexer = input('Ingrese el nombre de su lexer> ')
parser = input('Ingrese el nombre de su parser> ')
executable = input ('Ingrese el nombre de su ejecutable> ')

if '.py' not in executable:
    executable += '.py'

lexer = lexer.replace('.py', '')
parser = parser.replace('.py', '')

content = []
content.append(f'from {lexer} import tokenizer')
content.append(f'from {parser} import slr\n')

content.append('input_file = input("Ingrese el nombre del archivo de codigo fuente> ")')

content.append(f'tokenizer.read_source_code(input_file)')
content.append('tokenizer.initialize_token_recognition()')
content.append('print(slr.parse(tokenizer))')

with open(executable, "wt") as file:
    for content in content:
        file.write(content + '\n')
        
print("Archivo generado: ", executable)