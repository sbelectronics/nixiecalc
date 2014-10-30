"""
    Calculator Engine

    Dr. Scott M Baker, 2014
    http://www.smbaker.com/
    smbaker@smbaker.com
"""

import math
import sys

class Calculator(object):
    def __init__(self):
        self.display = 0
        self.memory = 0
        self.accumulator = None
        self.inputBuffer = ""

        self.operators = {}
        self.operators["+"] = self.plus
        self.operators["-"] = self.minus
        self.operators["*"] = self.times
        self.operators["/"] = self.divide

        self.unary = {}
        self.unary["!"] = self.factorial
        self.unary["x2"] = self.x2
        self.unary["x3"] = self.x3
        self.unary["int"] = self.int
        self.unary["MR"] = self.memRead
        self.unary["pi"] = self.pi

        self.operator = None
        self.operand = None
        self.lastEqualOperator = None
        self.lastKey = None

        self.memory = 0

    def handle_key(self, key):
        if key in ['0','1','2','3','4','5','6','7','8','9','.']:
            self.inputBuffer = self.inputBuffer + key
            self.operand = float(self.inputBuffer)
            self.display = self.operand
            if (self.lastKey == "="):
                self.accumulator = None

        elif (key == "C") or (key == "AC"):
            if (self.inputBuffer != "") or (key == "AC"):
                self.inputBuffer = ""
                self.operand = 0
                self.display = 0
                if (key=="AC") or (self.lastKey == "="):
                    self.accumulator = None

        elif key in self.operators.keys():
            if (self.operand is None):
                return

            if self.accumulator is None:
                self.accumulator = self.operand
            elif self.operator is not None:
                self.accumulator = self.operator(self.accumulator, self.operand)
            self.display = self.accumulator

            self.operator = self.operators[key]
            self.inputBuffer = ""

        elif key in self.unary.keys():
            self.operator = self.unary[key]
            self.accumulator = self.operator(self.display)
            self.operator = None
            self.lastEqualOperator = None
            self.display = self.accumulator
            self.inputBuffer = ""

        elif key=="=":
            if self.operator:
                self.accumulator = self.operator(self.accumulator, self.operand)
                self.lastEqualOperator = self.operator
            elif self.lastEqualOperator:
                self.accumulator = self.lastEqualOperator(self.accumulator, self.operand)
            self.display = self.accumulator
            self.inputBuffer = ""
            self.operator = None
            print "accum", self.accumulator

        elif key=="MC":
            self.memory = 0

        elif key=="M+":
            self.memory = self.memory + self.display

        elif key=="M-":
            self.memory = self.memory - self.display

        elif key=="q":
            sys.exit(0)

        self.lastKey = key

    def plus(self, accumulator, operand):
        print "plus", accumulator, operand
        return float(accumulator) + operand

    def minus(self, accumulator, operand):
        print "minus", accumulator, operand
        return float(accumulator) - operand

    def times(self, accumulator, operand):
        print "times", accumulator, operand
        return float(accumulator) * operand

    def divide(self, accumulator, operand):
        print "divide", accumulator, operand
        return float(accumulator) / operand

    def factorial(self, value):
        return math.factorial(int(value))

    def x2(self, value):
        return (value * value)

    def x3(self, value):
        return (value * value * value)

    def int(self, value):
        return int(value)

    def memRead(self, value):
        return self.memory

    def pi(self, value):
        return math.pi


def getch():
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def main():
    c = Calculator()
    while True:
        c.handle_key(getch())
        print "%0.0f        \r"% c.display,

if __name__ == "__main__":
    main()



