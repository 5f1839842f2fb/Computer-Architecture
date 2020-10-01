"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.r = [0] * 8
        self.memory = [0] * 256
        self.PC = 0
        self.FL = [0] * 3 # 8 bits but we only have 3 flags so this is to save future typing and confusion
        pass

    def load(self, file):
        """Load a program into memory."""

        program = []
        address = 0
        contents = None

        with open(file) as f:
            contents = f.read()
        contents = contents.splitlines()
        for line in contents:
            if len(line) == 0:
                pass
            elif line[0] != "#":
                trimmed = line[:8] # saves the first 8 characters of the line
                program += [trimmed]
        # print(program)
        for instruction in program:
            self.memory[address] = int(instruction, 2)
            address += 1
        print(self.memory)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.r[reg_a] += self.r[reg_b]
        #elif op == "SUB": etc
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

    def ram_read(self, MAR):
        return self.memory[MAR]
    
    def ram_write(self, MAR, MDR):
        self.memory[MAR] = MDR

    def run(self):
        """Run the CPU."""
        running = True
        IR = None
        # print(self.memory)
        
        while running:
            IR = self.memory[self.PC]
            if IR == 0b10000010: # LDI
                self.PC += 1
                register = self.memory[self.PC]
                self.PC += 1
                self.r[register] = self.memory[self.PC]
                self.PC += 1
            elif IR == 0b01000111: # PRN
                self.PC += 1
                register = self.memory[self.PC]
                print(self.r[register])
                self.PC += 1
            elif IR == 0b00000001: # HLT
                sys.exit()