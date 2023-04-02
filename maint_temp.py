import re

simple_pattern = r"\[\'(\w)\'\s*-\s*\'(\w)\'\]"
compound_pattern = r"\[\'(\w)\'\s*-\s*\'(\w)\'\s*\'(\w)\'\s*-\s*\'(\w)\'\]"
pattern = patron = r"^let\s+\w+\s+=\s+(.*?)$"
otro = r"\'[^']*'"

text = "'aaaaaaa"

m = re.search(otro, text)