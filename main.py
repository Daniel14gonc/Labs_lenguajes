from regex import Regex
from AFN import AFN

# regex = Regex('0 ? ( 1 ? ) ? 0 *')
# regex = Regex('a|b*c?d*ef')
# regex = Regex('a|b*')
# regex = Regex('a|b*c')
regex = Regex('ab')
regex.to_posfix()

afn = AFN(regex)