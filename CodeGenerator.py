import re
from collections import deque
from LexicalAnalyzer import LexicalAnalyzer


class CodeGenerator:

    def __init__(self, lexemes_list):
        self.lexemes_list = lexemes_list
        self.assembly_code = ""
        self.general_variables = []
        self.number_variables = set([])
        self.identifiers = set([])
        self.cut_into_statements(self.lexemes_list)
        self.print_variables()
        self.remove_extras()

    def cut_into_statements(self, lexemes_list):
        i = 0

        while i < len(lexemes_list):

            if lexemes_list[i] == "if":
                open_curly_brace_index = i + lexemes_list[i:].index("{")
                close_curly_brace_index = self.get_bracket_index(lexemes_list, open_curly_brace_index, "{", "}")
                self.generate_if_code(lexemes_list[i: close_curly_brace_index+1])
                i = close_curly_brace_index

                if len(lexemes_list)-1 > i and lexemes_list[i+1] == "else":
                    open_curly_brace_index = i + lexemes_list[i:].index("{")
                    close_curly_brace_index = self.get_bracket_index(lexemes_list, open_curly_brace_index, "{", "}")
                    self.generate_else_code(lexemes_list[i+1: close_curly_brace_index + 1])
                    i = close_curly_brace_index
                i += 1

            elif self.is_identifier(lexemes_list[i]):
                index_of_semicolon = i + lexemes_list[i:].index(";")
                gen_var = self.generate_expression_code(lexemes_list[i+2: index_of_semicolon])
                self.assembly_code += f"LDA {gen_var}\n"
                self.assembly_code += f"STA {lexemes_list[i]}\n"
                self.identifiers.add(lexemes_list[i])
                i = index_of_semicolon + 1

    def generate_expression_code(self, lexemes_list):
        if len(lexemes_list) == 1:
            if self.is_identifier(lexemes_list[0]):
                self.identifiers.add(lexemes_list[0])
                return lexemes_list[0]

            if self.is_integer(lexemes_list[0]):
                num_var = self.create_num_variable(lexemes_list[0])
                self.number_variables.add(num_var)
                return num_var

            if lexemes_list[0] in self.general_variables:
                return lexemes_list[0]

        while "(" in lexemes_list:
            open_bracket_index = lexemes_list.index("(")
            close_bracket_index = self.get_bracket_index(lexemes_list, open_bracket_index, "(", ")")
            lexemes_list[open_bracket_index: close_bracket_index+1] =\
                [self.generate_expression_code(lexemes_list[open_bracket_index+1: close_bracket_index])]

        while "*" in lexemes_list and "/" in lexemes_list:
            mul_index = lexemes_list.index("*")
            div_index = lexemes_list.index("/")
            operator_index = mul_index if mul_index < div_index else div_index
            first_element = lexemes_list[operator_index - 1]
            self.assembly_code += f"LDA {self.lexeme_variable(first_element)}\n"
            count = 1
            for lexeme in lexemes_list[operator_index:]:
                if lexeme == "+" or lexeme == "-":
                    break

                if lexeme == "*":
                    self.assembly_code += "MUL "
                    count += 1

                if lexeme == "/":
                    self.assembly_code += "DIV "
                    count += 1

                if self.is_identifier(lexeme):
                    self.assembly_code += f"{lexeme}\n"
                    count += 1

                if self.is_integer(lexeme):
                    self.assembly_code += f"{self.create_num_variable(lexeme)}\n"
                    count += 1

                if lexeme in self.general_variables:
                    self.assembly_code += f"{lexeme}\n"
                    count += 1

            gen_var = self.create_general_variable()
            self.assembly_code += f"STA {gen_var}\n"
            lexemes_list[operator_index-1: operator_index-1+count] = [gen_var]

        while "*" in lexemes_list:
            mul_index = lexemes_list.index("*")
            first_element = lexemes_list[mul_index - 1]
            self.assembly_code += f"LDA {self.lexeme_variable(first_element)}\n"
            count = 1
            for lexeme in lexemes_list[mul_index:]:
                if lexeme == "+" or lexeme == "-":
                    break

                if lexeme == "*":
                    self.assembly_code += "MUL "
                    count += 1

                if self.is_identifier(lexeme):
                    self.assembly_code += f"{lexeme}\n"
                    count += 1

                if self.is_integer(lexeme):
                    self.assembly_code += f"{self.create_num_variable(lexeme)}\n"
                    count += 1

                if lexeme in self.general_variables:
                    self.assembly_code += f"{lexeme}\n"
                    count += 1

            gen_var = self.create_general_variable()
            self.assembly_code += f"STA {gen_var}\n"
            lexemes_list[mul_index-1: mul_index-1+count] = [gen_var]

        while "/" in lexemes_list:
            div_index = lexemes_list.index("/")
            first_element = lexemes_list[div_index - 1]
            self.assembly_code += f"LDA {self.lexeme_variable(first_element)}\n"
            count = 1
            for lexeme in lexemes_list[div_index:]:
                if lexeme == "+" or lexeme == "-":
                    break

                if lexeme == "/":
                    self.assembly_code += "DIV "
                    count += 1

                if self.is_identifier(lexeme):
                    self.assembly_code += f"{lexeme}\n"
                    count += 1

                if self.is_integer(lexeme):
                    self.assembly_code += f"{self.create_num_variable(lexeme)}\n"
                    count += 1

                if lexeme in self.general_variables:
                    self.assembly_code += f"{lexeme}\n"
                    count += 1

            gen_var = self.create_general_variable()
            self.assembly_code += f"STA {gen_var}\n"
            lexemes_list[div_index-1: div_index-1+count] = [gen_var]

        while "+" in lexemes_list or "-" in lexemes_list:
            first_element = lexemes_list[0]
            self.assembly_code += f"LDA {self.lexeme_variable(first_element)}\n"
            for lexeme in lexemes_list[1:]:

                if lexeme == "+":
                    self.assembly_code += "ADD "

                if lexeme == "-":
                    self.assembly_code += "SUB "

                if self.is_identifier(lexeme):
                    self.assembly_code += f"{lexeme}\n"

                if self.is_integer(lexeme):
                    self.assembly_code += f"{self.create_num_variable(lexeme)}\n"

                if lexeme in self.general_variables:
                    self.assembly_code += f"{lexeme}\n"

            gen_var = self.create_general_variable()
            self.assembly_code += f"STA {gen_var}\n"
            lexemes_list[:] = [gen_var]

        if len(lexemes_list) == 1 and lexemes_list[0] in self.general_variables:
            return lexemes_list[0]
        else:
            self.assembly_code += "Something wrong happened"

    def generate_if_code(self, lexemes_list):
        close_bracket_index = self.get_bracket_index(lexemes_list, 1, "(", ")")
        self.generate_conditional_code(lexemes_list[2: close_bracket_index])
        self.cut_into_statements(lexemes_list[close_bracket_index+2: -1])
        self.assembly_code += "FALSE "

    def generate_else_code(self, lexemes_list):
        self.cut_into_statements(lexemes_list[2: -1])

    def generate_conditional_code(self, lexemes_list):
        cond_op_index = 0
        cond_op = ""
        for i in range(len(lexemes_list)):
            if lexemes_list[i] in LexicalAnalyzer.tokens["double-operator"] or lexemes_list[i] in \
                    LexicalAnalyzer.tokens["cond-operator"]:
                cond_op_index = i
                cond_op = lexemes_list[i]
                break

        first_exp = self.generate_expression_code(lexemes_list[: cond_op_index])
        second_exp = self.generate_expression_code(lexemes_list[cond_op_index+1:])

        self.assembly_code += f"LDA {first_exp}\n"
        self.assembly_code += f"COMP {second_exp}\n"

        if cond_op == ">":
            self.assembly_code += "JGT TRUE\n"
            self.assembly_code += "JLT FALSE\n"
            self.assembly_code += "JEQ FALSE\n"
            self.assembly_code += "TRUE "

        elif cond_op == ">=":
            self.assembly_code += "JGT TRUE\n"
            self.assembly_code += "JEQ TRUE\n"
            self.assembly_code += "JLT FALSE\n"
            self.assembly_code += "TRUE "

        elif cond_op == "<":
            self.assembly_code += "JLT TRUE\n"
            self.assembly_code += "JGT FALSE\n"
            self.assembly_code += "JEQ FALSE\n"
            self.assembly_code += "TRUE "

        elif cond_op == "<=":
            self.assembly_code += "JLT TRUE\n"
            self.assembly_code += "JEQ TRUE\n"
            self.assembly_code += "JGT FALSE\n"
            self.assembly_code += "TRUE "

        elif cond_op == "==":
            self.assembly_code += "JEQ TRUE\n"
            self.assembly_code += "JGT FALSE\n"
            self.assembly_code += "JLT FALSE\n"
            self.assembly_code += "TRUE "

    def extract_list_of_lexemes(self, tokes_table):
        returned_list = []
        for token in tokes_table:
            returned_list.append(token.lexeme)
        return returned_list

    def get_bracket_index(self, s, i, open, close):

        # If input is invalid.
        if s[i] != open:
            return -1

        # Create a deque to use it as a stack.
        d = deque()

        # Traverse through all elements
        # starting from i.
        for k in range(i, len(s)):

            # Pop a starting bracket
            # for every closing bracket
            if s[k] == close:
                d.popleft()

            # Push all starting brackets
            elif s[k] == open:
                d.append(s[i])

            # If deque becomes empty
            if not d:
                return k

        return -1

    def lexeme_variable(self, lexeme):
        if self.is_identifier(lexeme):
            return lexeme

        if self.is_integer(lexeme):
            return self.create_num_variable(lexeme)

        if lexeme in self.general_variables:
            return lexeme

    def create_general_variable(self):
        gen_var = f"VAR_{len(self.general_variables)+1}"
        self.general_variables.append(gen_var)
        return gen_var

    def create_num_variable(self, number):
        num_var = f"NUM_{number}"
        self.number_variables.add(num_var)
        return num_var

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

    def print_variables(self):
        for identifier in self.identifiers:
            self.assembly_code += f"{identifier} RESW 1\n"

        for general_variable in self.general_variables:
            self.assembly_code += f"{general_variable} RESW 1\n"

        for number_variable in self.number_variables:
            self.assembly_code += f"{number_variable} WORD {number_variable[4:]}\n"

    def remove_extras(self):
        lines_list = self.assembly_code.splitlines()

        for line in lines_list:
            if len(line.split()) >= 4:
                self.assembly_code = self.assembly_code.replace(line, f"{line.split()[-4]}\n{' '.join(line.split()[-3:])}")
