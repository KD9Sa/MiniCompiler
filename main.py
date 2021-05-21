from LexicalAnalyzer import LexicalAnalyzer
from Parser import Parser
from CodeGenerator import CodeGenerator
from Assembler import Assembler
from CodeOptimizer import CodeOptimizer

with open("Program Code.txt", "r") as file:
    program_code = file.read()

lexical = LexicalAnalyzer(program_code)
# print(lexical.program_code)


with open("Output.txt", "w") as file:
    file.write("Lexical Analyzer:\n---------------\n")
    if lexical.lexical_errors:
        file.write(f"\tErrors found: \n")
        for error in lexical.lexical_errors:
            file.write(f"\t\t{error}\n")

    if not lexical.lexical_errors:
        file.write("No Lexical Errors Found.\n\n")
        file.write("Tokens:\n")
        for obj in lexical.lexical_table:
            file.write(f"Lexeme: {obj.lexeme}\t\tType: {obj.token}\n")

        file.write(f"\nParser:\n---------------\n")
        parser = Parser(lexical.lexical_table)
        if parser.parser_errors:
            file.write(f"\tErrors found: \n")
            for error in parser.parser_errors:
                file.write(f"\t\t{error}\n")

        if not parser.parser_errors:
            file.write("No Parser Errors Found.\n")

            file.write(f"\nCode Optimizer:\n---------------\n")
            code_optimizer = CodeOptimizer(lexical.lexical_table)
            for item in code_optimizer.lexemes_list:
                if item == ";" or item == "{" or item == "}":
                    file.write(f"{item}\n")
                else:
                    file.write(f"{item} ")

            file.write(f"\nCode Generator:\n---------------\n")
            code_generator = CodeGenerator(code_optimizer.lexemes_list)
            assembler = Assembler(code_generator.assembly_code)
            file.write("{:<15} {:<15} {:<15} {:<15}".format("Location", "Variable", "Op Code", "Identifier",
                                                            "Object Code"))
            file.write("\n")
            for item in assembler.assembly_lines:
                file.write(
                    "{:<15} {:<15} {:<15} {:<15}".format(item.location, item.variable, item.op_code,
                                                         item.identifier, item.object_code))
                file.write("\n")
