"""CPU functionality."""

import sys

# operation codes:
HLT  = 0b00000001
LDI  = 0b10000010
PRN  = 0b01000111
MUL  = 0b10100010
PUSH = 0b01000101
POP  = 0b01000110
 # reserved registers
IM = 5
IS = 6
SP = 7
 # flags
FL_LT = 0b100
FL_GT = 0b010
FL_EQ = 0b001
FL_TIMER = 0b00000001
FL_KEYBOARD = 0b00000010

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0]*256
        self.reg = [0]*8
        self.reg[SP] = 0xf4

        self.processCounter = 0
        self.flags = 0
        # self.interrupts = 1;
        self.isPaused = False
        # self.last_timer_int = None
        self.instruction_sets_processCounter = False

        self.branchTree = {
            HLT: self.op_HLT,
            LDI: self.op_LDI,
            PRN: self.op_PRN,
            MUL: self.op_MUL,
            PUSH: self.op_PUSH,
            POP: self.op_POP
        }

    def load(self):
        """Load a program into memory."""

        address = 0

        fp = open(filename, "r")
        for line in fp:
             # split by comment and strip empty spaces
            instruction = line.split("#")[0].strip()
            if instruction == "":
             continue
            value = int(instruction, 2)
            self.ram[address] = value
            address += 1

    def stack_push(self, val):
        self.reg[SP] -= 1
        self.ram_write(self.reg[SP], val)

    def stack_pop(self):
        val = self.ram_read(self.reg[SP])
        self.reg[SP] += 1
        return val

    def ram_read(self, index):
         return self.ram[index]

    def ram_write(self, index, value):
            self.ram[index] = value


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while not self.isPaused:
            ir = self.ram[self.processCounter]
            operand_a = self.ram_read(self.processCounter + 1)
            operand_b = self.ram_read(self.processCounter + 2)

            instruction_size = ( ir >> 6 ) + 1
            self.instruction_sets_processCounter = ( (ir >> 4) &0b1 ) == 1

            if ir in self.branchTree:
                self.branchTree[ir](operand_a, operand_b)
            else:
                raise Exception(f'Unknown Instruction {bin(ir)} at {hex(self.processCounter)}')

            if not self.instruction_sets_processCounter:
                self.processCounter += instruction_size

    def op_HLT(self, operand_a, operand_b):
        self.isPaused = True

    def op_LDI(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b

    def op_PRN(self, operand_a, operand_b):
        print(self.reg[operand_a])
    
    def op_MUL(self, operand_a, operand_b):
        self.alu("MUL", operand_a, operand_b)

    def op_PUSH(self, operand_a, operand_b):
        self.stack_push(self.reg[operand_a])

    def op_POP(self, operand_a, operand_b):
        self.reg[operand_a] = self.stack_pop()
