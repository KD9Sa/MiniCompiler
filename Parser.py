from collections import deque


class Parser:

    def __init__(self, lexical_table):
        self.parser_errors = []
        self.cut_into_statements(lexical_table)

    def cut_into_statements(self, lexical_table):
        list_of_lexemes = self.extract_list_of_lexemes(lexical_table)
        i = 0

        while i < len(lexical_table):
            if lexical_table[i].token == "identifier":
                if ";" not in list_of_lexemes[i:]:
                    self.parser_errors.append("Missing ; at end of statement.")
                    return
                index_of_semicolon = i + list_of_lexemes[i:].index(";")
                if not self.validate_statement(lexical_table[i: index_of_semicolon + 1],
                                               list_of_lexemes[i: index_of_semicolon + 1]):
                    return
                i = index_of_semicolon

            elif lexical_table[i].lexeme == "if":
                if "{" not in list_of_lexemes[i:]:
                    self.parser_errors.append("Missing { at begging of if-statement.")
                    return
                open_curly_brace_index = i + list_of_lexemes[i:].index("{")
                close_curly_brace_index = self.get_bracket_index(list_of_lexemes, open_curly_brace_index, "{", "}")
                if close_curly_brace_index == -1:
                    self.parser_errors.append("Missing } at end of if-statement.")
                    return

                if not self.validate_if_statement(lexical_table[i:close_curly_brace_index+1],
                                                  list_of_lexemes[i:close_curly_brace_index+1]):
                    return

                i = close_curly_brace_index

                if len(list_of_lexemes)-1 > i and list_of_lexemes[i+1] == "else":
                    if "{" not in list_of_lexemes[i:]:
                        self.parser_errors.append("Missing { at begging of else-statement.")
                        return
                    open_curly_brace_index = i + list_of_lexemes[i:].index("{")
                    close_curly_brace_index = self.get_bracket_index(list_of_lexemes, open_curly_brace_index, "{", "}")
                    if close_curly_brace_index == -1:
                        self.parser_errors.append("Missing } at end of else-statement.")
                        return

                    if not self.validate_else_statement(lexical_table[i+1: close_curly_brace_index + 1],
                                                        list_of_lexemes[i+1: close_curly_brace_index + 1]):
                        return

                    i = close_curly_brace_index

            else:
                self.parser_errors.append(f"Illegal start of statement. Expected 'identifier' or 'if-statement' found: "
                                          f"{list_of_lexemes[i]}")
                return

            i += 1

    def validate_statement(self, tokens_table, lexemes_list):
        if lexemes_list[1] != "=":
            self.parser_errors.append("Missing = sign after identifier.")
            return False

        if not self.validate_expression(tokens_table[2: -1], lexemes_list[2: -1]):
            return False

        return True

    def validate_expression(self, tokens_table, lexemes_list):
        if not lexemes_list:
            self.parser_errors.append("Missing an expression.")
            return False

        i = 0
        even_term = 0
        odd_term = 1

        while i < len(tokens_table):
            if lexemes_list[i] == "(" and self.get_bracket_index(lexemes_list, i, "(", ")") == -1:
                self.parser_errors.append("Missing close bracket ')' ")
                return False

            if lexemes_list[i] == "(" and self.get_bracket_index(lexemes_list, i, "(", ")") != -1:
                close_bracket_index = self.get_bracket_index(lexemes_list, i, "(", ")")
                if not self.validate_expression(tokens_table[i+1: close_bracket_index],
                                                lexemes_list[i+1: close_bracket_index]):
                    return False

                i = close_bracket_index + 1
                continue

            if lexemes_list[i] == ")":
                self.parser_errors.append("Missing open bracket '(' ")
                return False

            elif i % 2 == odd_term and tokens_table[i].token != "operator" and lexemes_list[i] != ")":
                self.parser_errors.append(f"{lexemes_list[i]} is not a valid argument in this position.")
                return False

            elif i % 2 == even_term and tokens_table[i].token != "identifier" and tokens_table[i].token != "integer":
                self.parser_errors.append(f"{lexemes_list[i]} is not a valid argument in this position.")
                return False

            i += 1

        return True

    def validate_if_statement(self, tokens_table, lexemes_list):
        if lexemes_list[1] != "(":
            self.parser_errors.append("Missing ( ")
            return False

        open_bracket_index = 1
        close_bracket_index = self.get_bracket_index(lexemes_list, 1, "(", ")")

        if lexemes_list[close_bracket_index + 1] != "{":
            self.parser_errors.append("Missing { at beginning of if-statement.")
            return False

        if not self.validate_conditional_statement(tokens_table[open_bracket_index+1: close_bracket_index],
                                                   lexemes_list[open_bracket_index+1: close_bracket_index]):
            return False

        self.cut_into_statements(tokens_table[close_bracket_index + 2: -1])

        return True

    def validate_else_statement(self, tokens_table, lexemes_list):
        if lexemes_list[1] != "{":
            self.parser_errors.append("Missing { at beginning of if-statement")
            return False

        self.cut_into_statements(tokens_table[2: -1])

        return True

    def validate_conditional_statement(self, tokens_table, lexemes_list):
        cond_operator_found = False
        cond_operator_index = 0

        for i in range(len(tokens_table)):
            if tokens_table[i].token == "double-operator" or tokens_table[i].token == "cond-operator":
                cond_operator_found = True
                cond_operator_index = i
                break

        if not cond_operator_found:
            self.parser_errors.append("Missing conditional operator.")
            return False

        if not self.validate_expression(tokens_table[: cond_operator_index], lexemes_list[: cond_operator_index]):
            return False

        if not self.validate_expression(tokens_table[cond_operator_index+1:], lexemes_list[cond_operator_index+1:]):
            return False

        return True

    def extract_list_of_lexemes(self, tokes_table):
        returned_list = []
        for token in tokes_table:
            returned_list.append(token.lexeme)
        return returned_list

    def get_bracket_index(self, s, i, open_bracket, close_bracket):

        # If input is invalid.
        if s[i] != open_bracket:
            return -1

        # Create a deque to use it as a stack.
        d = deque()

        # Traverse through all elements
        # starting from i.
        for k in range(i, len(s)):

            # Pop a starting bracket
            # for every closing bracket
            if s[k] == close_bracket:
                d.popleft()

            # Push all starting brackets
            elif s[k] == open_bracket:
                d.append(s[i])

            # If deque becomes empty
            if not d:
                return k

        return -1
