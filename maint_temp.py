from Formatter import YalexFormatter
from Reader import YalexReader

reader = YalexReader("lexer.yal")

content = reader.read()


form = YalexFormatter()
form.format_yalex_content(content)