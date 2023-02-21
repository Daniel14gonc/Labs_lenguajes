from regex import Regex
from AFN import AFN

# regex = Regex('0 ? ( 1 ? ) ? 0 *')
# regex = Regex('a|b*c?d*ef')
# regex = Regex('a|b*')
# regex = Regex('a|b*c')
# regex = Regex('a+')
# regex = Regex('a|x*a*|e')
# regex = Regex(')(()++a')
regex = Regex('(a|b)*abb')
print(regex.to_postfix())

afn = AFN(regex)
afn.output_image()