"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.r = [0] * 8
        self.r[7] = 0xF4 # stack pointer, starts at index 244 in memory
        self.memory = [0] * 256
        self.PC = 0
        self.FL = [0] * 3 # 8 bits but we only have 3 flags so this is to save future typing and confusion
        self.instructions = {}
        self.instructions[0b10000010] = self.LDI
        self.instructions[0b01000111] = self.PRN
        self.instructions[0b00000001] = self.HLT
        self.instructions[0b10100010] = self.MUL
        self.instructions[0b10100000] = self.ADD
        self.instructions[0b01000101] = self.PUSH
        self.instructions[0b01000110] = self.POP
        self.instructions[0b01010000] = self.CALL
        self.instructions[0b00010001] = self.RET

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
        #print(program)
        for instruction in program:
            self.memory[address] = int(instruction, 2)
            address += 1
        #print(self.memory)

    
    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.r[reg_a] += self.r[reg_b]
        elif op == "MUL":
            self.r[reg_a] *= self.r[reg_b]
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

    def push(self, val):
        self.r[7] -= 1
        self.memory[self.r[7]] = val

    def pop(self):
        value = self.memory[self.r[7]]
        self.memory[self.r[7]] = 0
        self.r[7] += 1
        return value

    ### instructions ###

    def PUSH(self): # really annoying that I have to have two functions for each push/pop: one for use of other instructions and one to be used directly in a program
        self.PC += 1
        val = self.r[self.memory[self.PC]] # value in register at PC
        self.push(val)
        self.PC += 1
        #print("stack after push: ", self.memory[0xE0:0xF4])

    def POP(self):
        self.PC += 1
        register = self.memory[self.PC]
        self.r[register] = self.pop()
        self.PC += 1
        #print("stack after pop:  ", self.memory[0xE0:0xF4])

    def CALL(self):
        self.PC += 1
        register = self.memory[self.PC] # register where subroutine address is saved
        self.PC += 1
        self.push(self.PC)
        self.PC = self.r[register]

    def RET(self):
        self.PC = self.pop()

    def LDI(self):
        self.PC += 1
        register = self.memory[self.PC]
        self.PC += 1
        self.r[register] = self.memory[self.PC]
        self.PC += 1

    def PRN(self):
        self.PC += 1
        register = self.memory[self.PC]
        print(self.r[register])
        self.PC += 1

    def HLT(self):
        sys.exit()
    
    def MUL(self):
        self.PC += 1
        registerA = self.memory[self.PC]
        self.PC += 1
        registerB = self.memory[self.PC]
        self.alu("MUL", registerA, registerB)
        self.PC += 1

    def ADD(self):
        self.PC += 1
        registerA = self.memory[self.PC]
        self.PC += 1
        registerB = self.memory[self.PC]
        self.alu("ADD", registerA, registerB)
        self.PC += 1

    def run(self):
        """Run the CPU."""
        running = True
        IR = None
        #print(self.memory)
        
        while running:
            IR = self.memory[self.PC]
            #print(IR)
            self.instructions[IR]()