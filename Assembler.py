from AssemblyLines import AssemblyLines


class Assembler:

    op_code_values = {
        "ADD": "18", "COMP": "28", "DIV": "24", "JEQ": "30", "JGT": "34", "JLT": "38", "LDA": "00", "MUL": "20",
        "STA": "0C", "SUB": "1C"
    }

    def __init__(self, assembly_code):
        self.assembly_lines = self.split_into_lines_list(assembly_code)
        self.generate_locations()
        self.generate_object_codes()

    def split_into_lines_list(self, assembly_code):
        lines_list = []
        assembly_lines = []

        for line in assembly_code.splitlines():
            lines_list.append(line.split())

        for line in lines_list:
            if len(line) == 1:
                assembly_lines.append(AssemblyLines(variable=line[0]))
            if len(line) == 2:
                assembly_lines.append(AssemblyLines(op_code=line[0], identifier=line[1]))
            if len(line) == 3:
                assembly_lines.append(AssemblyLines(variable=line[0], op_code=line[1], identifier=line[2]))

        return assembly_lines

    def generate_locations(self):
        if not self.assembly_lines:
            return

        start = "0000"
        self.assembly_lines[0].location = start
        for i in range(1, len(self.assembly_lines)):
            self.assembly_lines[i].location = hex(int(start, 16) + int("0003", 16))[2:].zfill(4)
            start = hex(int(start, 16) + int("0003", 16))

    def generate_object_codes(self):
        for i in range(len(self.assembly_lines)):
            if self.assembly_lines[i].op_code in self.op_code_values:
                self.assembly_lines[i].object_code = f"{self.op_code_values[self.assembly_lines[i].op_code]}" \
                    f"{self.get_variable_location(self.assembly_lines[i:], self.assembly_lines[i].identifier)}"

    def get_variable_location(self, assembly_lines, identifier):
        for i in range(len(assembly_lines)):
            if assembly_lines[i].variable == identifier:
                return assembly_lines[i].location
