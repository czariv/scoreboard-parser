import argparse
import pandas as pd
import re

# Define opcode constants
OPCODES = {
    'fld': 0,
    'fsd': 1,
    'fadd': 2,
    'fsub': 3,
    'fmul': 4,
    'fdiv': 5
}

# Define register prefix constants
REG_PREFIXES = {
    'x': 'int',
    'f': 'float'
}

registers = {f"x{i}": None for i in range(32)}
registers.update({f"f{i}": None for i in range(32)})

class Instruction:
    def __init__(self, data):
        self.opcode = data.get('opcode')
        self.rs1 = data.get('rs1')
        self.rs1_type = data.get('rs1_type')
        self.rs2 = data.get('rs2')
        self.rs2_type = data.get('rs2_type')
        self.rd = data.get('rd')
        self.rd_type = data.get('rd_type')
        self.imm = data.get('imm')
        self.line = data.get('line')

    def method1(self):
        # Implement your method here
        pass

class Operator:
    def __init__(self, op_name, busy=False, fi=0, fj=0, fk=0, qj=False, qk=False, rj=False, rk=False, exec_time=0):
        self.op = op_name
        self.exec_time = exec_time
        self.ticks = [0 for _ in range(exec_time)]
    
    def reset_values(self):
        self.ticks = [0 for _ in range(self.exec_time)]
    
    def return_type(self):
        return self.op

def parse_file(filename):
    instructions = []
    with open(filename, 'r') as f:
        for line in f:
            fields = line.strip().replace(',', ' ').split()
            opcode = fields[0].lower()
            if opcode not in OPCODES:
                raise ValueError(f'Invalid opcode: {opcode}')
            opcode = OPCODES[opcode]
            rs1, rs2, rd, imm = 0, 0, 0, None  # Set imm to None by default
            rs1_type, rs2_type, rd_type = None, None, None
            if opcode == 0:  # fld format: "instruction rd imm(rs1)"
                rd = int(fields[1][1:])
                rd_type = REG_PREFIXES[fields[1][0].lower()]
                rs1_imm = fields[2].split('(')
                imm = int(rs1_imm[0])
                rs1 = int(rs1_imm[1][1:-1])
                rs1_type = REG_PREFIXES[rs1_imm[1][0:1].lower()]
            elif opcode == 1:  # fsd format: "instruction rs2 imm(rs1)"
                rs2 = int(fields[1][1:])
                rs2_type = REG_PREFIXES[fields[1][0].lower()]
                rs1_imm = fields[2].split('(')
                imm = int(rs1_imm[0])
                rs1 = int(rs1_imm[1][1:-1])
                rs1_type = REG_PREFIXES[rs1_imm[1][0:1].lower()]
            else:  # Other instructions format: "instruction rd rs1 rs2"
                rd = int(fields[1][1:])
                rd_type = REG_PREFIXES[fields[1][0].lower()]
                rs1 = int(fields[2][1:])
                rs1_type = REG_PREFIXES[fields[2][0].lower()]
                if len(fields) > 3:
                    rs2 = int(fields[3][1:])
                    rs2_type = REG_PREFIXES[fields[3][0].lower()]
                else:
                    rs2 = 0
                    rs2_type = None
            instructions.append({
                'opcode': opcode,
                'rs1': rs1,
                'rs1_type': rs1_type,
                'rs2': rs2,
                'rs2_type': rs2_type,
                'rd': rd,
                'rd_type': rd_type,
                'imm': imm,
                'line': line.strip("\n")
            })
    return instructions

def parse_txt_to_table(txt):
    operators = []
    for line in txt.split('\n'):
        if line.strip():
            operator, num_operators, execution_time = line.split()
            num_operators = int(num_operators)
            for i in range(num_operators):
                operator_instance = Operator(operator, exec_time=int(execution_time))
                operators.append(operator_instance)
    return operators

def parse_assembly_file(filename):
    with open(filename, 'r') as file:
        instructions = [line.strip() for line in file.readlines() if line.strip()]
    
    table_data = []
    
    for instruction in instructions:
        table_data.append({
            "Instruction/Cycle": instruction,
            "Issue": 0,
            "Read": 0,
            "Execute": 0,
            "Write": 0
        })
        
    return pd.DataFrame(table_data).set_index("Instruction/Cycle")

def read_config_file(filename):
    with open(filename, 'r') as file:
        return file.read()
    
def reset_op(op):
    print(op)
    
def scoreboard(inst, op, table):
    issue_list = []
    read_list = []
    ex_list = []
    write_list = []
    free_ex = {'int': [], 'mult': [], 'add': [], 'div': []}
    waiting_read = {}
    reset_list = []
    att = None
    iteration = 0
    while op:
        att = op.pop(0)
        opt = att.return_type()
        free_ex[opt].append(att)

    while inst or issue_list or read_list or ex_list or ex_list or write_list:
        iteration += 1

        while reset_list:
            to_reset = reset_list.pop(0)
            temp = 'x' + str(to_reset.rd) if to_reset.rd_type == 'int' else 'f' + str(to_reset.rd)
            registers[temp] = False
            to_reset.operator.reset_values()
            free_ex[to_reset.operator.op].append(to_reset.operator)

        if write_list:
            while write_list:
                i = write_list.pop(0)
                temp = 'x' + str(i.rd) if i.rd_type == 'int' else 'f' + str(i.rd)
                reset_list.append(i)
                table.loc[i.line, 'Write'] = iteration

        if ex_list:
            save = []
            for i in ex_list:
                i.operator.ticks.pop()
                if not(i.operator.ticks):
                    save.append(i)
                    table.loc[i.line, 'Execute'] = iteration
            for i in save:
                ex_list.remove(i)
                write_list.append(i)
        if read_list:
            save = []
            for i in read_list:
                temp1 = 'x' + str(i.rs1) if i.rs1_type == 'int' else 'f' + str(i.rs1)
                temp2 = 'x' + str(i.rs2) if i.rs2_type == 'int' else 'f' + str(i.rs2)
                if (registers[temp1] and registers[temp1]!=i) or (registers[temp2] and registers[temp2]!=i):
                    waiting_read[temp1] = True
                    waiting_read[temp2] = True
                else:
                    waiting_read[temp1] = False
                    waiting_read[temp2] = False
                    save.append(i)
                    table.loc[i.line, 'Read'] = iteration
            for i in save:
                read_list.remove(i)
                ex_list.append(i)
        if not(issue_list) and inst:
            att = Instruction(inst.pop(0))
            issue_list.append(att)
        if issue_list:
            temp = 'x' + str(att.rd) if att.rd_type == 'int' else 'f' + str(att.rd)
            if temp in waiting_read.keys():
                if waiting_read[temp]:
                    continue
            if registers[temp]:
                continue
            if att.opcode in [0,1] and free_ex['int']:
                att.operator = free_ex['int'].pop()
            elif att.opcode in [2,3] and att.rd_type == 'float' and free_ex['add']:
                att.operator = free_ex['add'].pop()
            elif att.opcode in [2,3] and att.rd_type == 'int' and free_ex['int']:
                att.operator = free_ex['int'].pop()
            elif att.opcode in [4] and free_ex['mult']:
                att.operator = free_ex['mult'].pop()
            elif att.opcode in [5] and free_ex['div']:
                att.operator = free_ex['div'].pop()
            else:
                continue
            issue_list.remove(att)
            read_list.append(att)
            table.loc[att.line, 'Issue'] = iteration
            if att.rd == 0:
                continue
            registers[temp] = att

def function1(filename, table):
    table.to_csv(filename)

def function2(table):
    print(table)

def main(filename=None):
    example = 'examples/example2.s'
    config_filename = 'configs/config2.txt'
    instructions = parse_file(example)
    table = parse_assembly_file(example)
    txt_data = read_config_file(config_filename)

    op = parse_txt_to_table(txt_data)

    scoreboard(instructions, op, table)

    if filename:
        function1(filename, table)
    else:
        function2(table)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Exemplo de script com parâmetro opcional filename.")
    parser.add_argument("--filename", help="Nome do arquivo a ser salvo.")
    args = parser.parse_args()

    if args.filename:
        main(args.filename)
    else:
        main()
