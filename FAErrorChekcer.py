class FAErrorChecker(object):
    
    def check_alphabet_errors(self, string, alphabet):
        self.errors = []
        for i in range(len(string)):
            if string[i] not in alphabet and string[i] != 'ε':
                error = f"Character {string[i]} does not belong to alphabet at position {i}.\n"
                self.errors.append(error)
        if self.errors:
            raise Exception(self.to_string())

    def to_string(self):
        res = '\n'
        for error in self.errors:
            res += error

        return res