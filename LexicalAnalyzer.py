import re
from Tokens import Tokens


class LexicalAnalyzer:
    tokens = {
        "keyword": ["if", "else"],
        "delimiter": ["(", ")", "{", "}", ";"],
        "operator": ["+", "-", "*", "/"],
        "double-operator": [">=", "<=", "=="],
        "cond-operator": [">", "<"],
        "assign-operator": ["="],
        "character": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S",
                      "T", "U", "V", "W", "X", "Y", "Z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l",
                      "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"],
        "integer": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    }

    # Receives program code that may have symbols next to each other without white spaces
    # Calls add_spaces_to_symbols function on program_code to add white space before and after each symbol
    # Splits the program_code into list of lexemes
    def __init__(self, program_code):
        self.program_code = self.add_spaces_to_symbols(program_code)
        self.lexical_errors = []
        self.lexical_table = self.generate_table(self.program_code)

    # Adds spaces before and after each symbol
    # Example:
    # if(5>x)
    # ( is symbol, > is symbol, ) is symbol
    # The function return the string in the following format:
    # if ( 5 > x )
    def add_spaces_to_symbols(self, code):
        for delimiter in self.tokens["delimiter"]:
            code = code.replace(delimiter, f" {delimiter} ")

        for operator in self.tokens["operator"]:
            code = code.replace(operator, f" {operator} ")

        for double_operator in self.tokens["double-operator"]:
            code = code.replace(double_operator, f" {double_operator} ")

        for cond_operator in self.tokens["cond-operator"]:
            code = code.replace(cond_operator, f" {cond_operator} ")

        for assign_operator in self.tokens["assign-operator"]:
            code = code.replace(assign_operator, f" {assign_operator} ")

        code = self.merge_similar_operators(" ".join(code.split()).split())

        return code

    def merge_similar_operators(self, code_list):
        for i in range(len(code_list)):
            if i < len(code_list) - 1:
                if code_list[i] + code_list[i + 1] in self.tokens["double-operator"]:
                    code_list[i:i+2] = [''.join(code_list[i:i+2])]

        return code_list

    def generate_table(self, program_code):
        returned_table = []
        for lexeme in program_code:
            if lexeme in self.tokens["keyword"]:
                returned_table.append(Tokens(lexeme, "keyword"))
            elif lexeme in self.tokens["delimiter"]:
                returned_table.append(Tokens(lexeme, "delimiter"))
            elif lexeme in self.tokens["operator"]:
                returned_table.append(Tokens(lexeme, "operator"))
            elif lexeme in self.tokens["cond-operator"]:
                returned_table.append(Tokens(lexeme, "cond-operator"))
            elif lexeme in self.tokens["double-operator"]:
                returned_table.append(Tokens(lexeme, "double-operator"))
            elif lexeme in self.tokens["assign-operator"]:
                returned_table.append(Tokens(lexeme, "assign-operator"))
            elif self.is_identifier(lexeme):
                returned_table.append(Tokens(lexeme, "identifier"))
            elif self.is_integer(lexeme):
                returned_table.append(Tokens(lexeme, "integer"))
            else:
                self.lexical_errors.append(f"Unknown symbol: {lexeme}")
        return returned_table

    def is_identifier(self, lexeme):
        pattern = re.compile(r"^[A-Za-z]+[A-Za-z0-9]*$")
        if re.match(pattern, lexeme):
            return True
        return False

    def is_integer(self, lexeme):
        pattern = re.compile(r"^\d*$")
        if re.match(pattern, lexeme):
            return True
        return False
