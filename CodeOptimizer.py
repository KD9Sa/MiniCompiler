class CodeOptimizer:

    def __init__(self, lexical_table):
        self.lexemes_list = self.extract_list_of_lexemes(lexical_table)
        self.optimize()

    def optimize(self):
        self.lexemes_list = " ".join(self.lexemes_list).replace("0 +", "").split()
        self.lexemes_list = " ".join(self.lexemes_list).replace("0 -", "").split()
        self.lexemes_list = " ".join(self.lexemes_list).replace("+ 0", "").split()
        self.lexemes_list = " ".join(self.lexemes_list).replace("- 0", "").split()

    def extract_list_of_lexemes(self, tokes_table):
        returned_list = []
        for token in tokes_table:
            returned_list.append(token.lexeme)
        return returned_list
