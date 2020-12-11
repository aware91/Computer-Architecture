"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
ADD = 0b10100000
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        #Add list properties to 'CPU' class to hold 256 bytes of memory
        self.ram = [0b00000000] * 256
        #and 8 general purpose registers:
        self.reg = [0b00000000] * 8
        self.reg[7] = 0xF4
        #R0
        #R1
        #R2
        #R3
        #R4
        #R5 reserved as the interrupt mask (IM)
        #R6 reserved as the interrupt status (IS)
        #R7 reserved as the stack pointer (SP)

        #Internal Registers
        #PC: Program Counter, current executed instruction
        self.pc = 0
        #IR: Instruction Register, constains the current executed instructions
        #FL: Flags
        self.fl = 0
        self.sp = 7
        self.running = True
    
    #'ram_read()' should accept the address to read and return value stored
    def ram_read(self, address):
        return self.ram[address]

    #'ram_write()' should accept a value to write, and the address to write it to.
    def ram_write(self, address, val):
        self.ram[address] = val

    def load(self):
        """Load a program into memory."""

        if len(sys.argv) != 2:
            print("Need file name!")
            sys.exit(1)
        try:
            address = 0
            with open(sys.argv[1]) as f:
                for line in f:
                    comment_split = line.split("#")
                    value = comment_split[0].strip()
                    if value == "":
                        continue
                    num = int(value, 2)
                    #print(f"{num:08b}: {num}")
                    #print(value)
                    self.ram[address] = num
                    #print(address)
                    address += 1

        except FileNotFoundError:
            print("File not found!")
            sys.exit(2)


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == ADD:
            self.reg[reg_a] += self.reg[reg_b]
        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
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

    def run(self):
        """Run the CPU."""
        while self.running:
            task_1 = self.ram_read(self.pc + 1)
            task_2 = self.ram_read(self.pc + 2)
            command_to_execute = self.ram_read(self.pc)
            if command_to_execute == LDI:
                self.reg[task_1] = task_2
                self.pc += 3
            elif command_to_execute == PRN:
                print(self.reg[task_1])
                self.pc += 2
            elif command_to_execute == ADD:
                self.alu(command_to_execute, task_1, task_2)
                self.pc += 3
            elif command_to_execute == MUL:
                self.alu(command_to_execute, task_1, task_2)
                self.pc += 3
            elif command_to_execute == PUSH:
                self.reg[self.sp] -=1
                self.ram[self.reg[self.sp]] = self.reg[task_1]
                self.pc += 2
            elif command_to_execute == POP:
                self.reg[task_1] = self.ram[self.reg[self.sp]]
                self.reg[self.sp] += 1
                self.pc += 2
            elif command_to_execute == CALL:
                self.reg[self.sp]  -= 1
                self.ram[self.reg[self.sp]] = self.pc + 2
                self.pc = self.reg[task_1]
            elif command_to_execute == RET:
                self.pc = self.ram[self.reg[self.sp]]
                self.reg[self.sp] += 1
            elif command_to_execute == HLT:
                self.running = False
                self.pc += 1