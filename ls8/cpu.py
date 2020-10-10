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
        self.FL = [0] * 8
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
        self.instructions[0b10100111] = self.CMP
        self.instructions[0b01010100] = self.JMP
        self.instructions[0b01010110] = self.JNE
        self.instructions[0b01010101] = self.JEQ
        self.instructions[0b10101000] = self.AND
        self.instructions[0b10101010] = self.OR
        self.instructions[0b10101011] = self.XOR
        self.instructions[0b01101001] = self.NOT
        self.instructions[0b10101100] = self.SHL
        self.instructions[0b10101101] = self.SHR
        self.instructions[0b10100100] = self.MOD
        self.instructions[0b10100110] = self.ADDI # chose the binary opcode value myself, might conflict with unimplemented instructions
        
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

    
    def alu(self, op, reg_a, reg_b = 0): # for AND, OR, XOR, NOT etc idk if this is right, there's no tests provided
        """ALU operations."""

        if op == "ADD":
            self.r[reg_a] += self.r[reg_b]
        elif op == "MUL":
            self.r[reg_a] *= self.r[reg_b]
        elif op == "AND":
            self.r[reg_a] &= self.r[reg_b]
        elif op == "OR":
            self.r[reg_a] |= self.r[reg_b]
        elif op == "XOR":
            self.r[reg_a] ^= self.r[reg_b]
        elif op == "NOT":
            self.r[reg_a] = ~self.r[reg_a]
        elif op == "SHL":
            self.r[reg_a] <<= self.r[reg_b]
        elif op == "SHR":
            self.r[reg_a] >>= self.r[reg_b]
        elif op == "MOD":
            self.r[reg_a] %= self.r[reg_b]

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

    def CMP(self): # im assuming when this is called, any bit not explicitly set is cleared
        self.PC += 1
        registerA = self.memory[self.PC]
        self.PC += 1
        registerB = self.memory[self.PC]
        self.FL = [0] * 8
        if self.r[registerA] < self.r[registerB]:
            self.FL[-3] = 1
        elif self.r[registerA] > self.r[registerB]:
            self.FL[-2] = 1
        elif self.r[registerA] == self.r[registerB]:
            self.FL[-1] = 1
        self.PC += 1
        #print(self.r[registerA], self.r[registerB])
        #print(self.FL)

    def JMP(self):
        self.PC += 1
        register = self.memory[self.PC]
        self.PC = self.r[register]

    def JNE(self):
        self.PC += 1
        register = self.memory[self.PC]
        if self.FL[-1] == False:
            self.PC = self.r[register]
        else:
            self.PC += 1

    def JEQ(self):
        self.PC += 1
        register = self.memory[self.PC]
        if self.FL[-1] == True:
            self.PC = self.r[register]
        else:
            self.PC += 1
    
    def AND(self):
        self.PC += 1
        registerA = self.memory[self.PC]
        self.PC += 1
        registerB = self.memory[self.PC]
        self.alu("AND", registerA, registerB)
        self.PC += 1

    def OR(self):
        self.PC += 1
        registerA = self.memory[self.PC]
        self.PC += 1
        registerB = self.memory[self.PC]
        self.alu("OR", registerA, registerB)
        self.PC += 1

    def XOR(self):
        self.PC += 1
        registerA = self.memory[self.PC]
        self.PC += 1
        registerB = self.memory[self.PC]
        self.alu("XOR", registerA, registerB)
        self.PC += 1

    def NOT(self):
        self.PC += 1
        registerA = self.memory[self.PC]
        self.alu("NOT", registerA)
        self.PC += 1

    def SHL(self):
        self.PC += 1
        registerA = self.memory[self.PC]
        self.PC += 1
        registerB = self.memory[self.PC]
        self.alu("SHL", registerA, registerB)
        self.PC += 1

    def SHR(self):
        self.PC += 1
        registerA = self.memory[self.PC]
        self.PC += 1
        registerB = self.memory[self.PC]
        self.alu("SHR", registerA, registerB)
        self.PC += 1

    def MOD(self):
        self.PC += 1
        registerA = self.memory[self.PC]
        self.PC += 1
        registerB = self.memory[self.PC]
        self.alu("MOD", registerA, registerB)
        self.PC += 1

    def ADDI(self): # should use the ALU according to MIPS spec but ALU is set up to only accept registers as arguments
        self.PC += 1
        register = self.memory[self.PC]
        self.PC += 1
        value = self.memory[self.PC]
        self.r[register] += value
        self.PC += 1

    def run(self):
        """Run the CPU."""
        running = True
        IR = None
        #print(self.memory)
        
        while running:
            IR = self.memory[self.PC]
            #print(IR)
            #print("PC: ", self.PC)
            self.instructions[IR]()