import smbus
import time
from calculator import Calculator
from keyboard import Keypad, MCP23017, PCF8574
#from nixie import Nixie, PIN_DATA, PIN_LATCH, PIN_CLK
from nixie_i2c import Nixie

def diglen(x):
    return len(x.replace(".",""))

MODE_OFF = "off"
MODE_ON = "on"
MODE_CLK = "clk"

class PiNixieCalculator(Calculator):
    def __init__(self, nixie, keypads):
        Calculator.__init__(self)
        self.nixie = nixie
        self.keypads = keypads
        self.mode = MODE_OFF
        self.clockLastTime = None

    def updateDisplay(self):
        s="%0.10f" % self.display

        if "." in s:
            while (s[-1] == "0") or (len(s)-1>self.nixie.digits):
                s = s[:-1]

            if (s[-1] == "."):
                s = s[:-1]

        if "." in s:
            dp = len(s) - s.index(".") - 2
            s = s.replace(".","")
        else:
            dp = None

        while (len(s)<self.nixie.digits):
           s=" " + s

        self.nixie.set_string(s, dp=dp)

        print "%0.0f        \r"% self.display,

    def handle_key(self, key):
        if (key == "CLK"):
            self.clockLastTime=None
            self.mode=MODE_CLK
        elif (key == "PWR"):
            if self.mode in [MODE_ON, MODE_CLK]:
                self.mode = MODE_OFF
            else:
                self.reset()
                self.mode = MODE_ON
        elif (self.mode in [MODE_OFF, MODE_CLK]):
            self.mode = MODE_ON
        super(PiNixieCalculator, self).handle_key(key)

    def poll(self):
        for keypad in self.keypads:
            keypad.calculator = self
            keypad.poll()

        if self.mode == MODE_CLK:
            t = time.strftime("%H %M %S")
            if t!=self.clockLastTime:
                self.clockLastTime=t
                self.nixie.set_string(self.clockLastTime)
        elif self.mode == MODE_OFF:
            self.nixie.set_string("        ")

class KeyPadNumbers(Keypad):
    keyMap = ["/", "=", "0", ".",
              "*", "3", "2", "1",
              "-", "6", "5", "4",
              "+", "9", "8", "7"]

    def __init__(self, driver, base=0):
        Keypad.__init__(self, driver, base)

    def keyup(self, keyNum):
        self.calculator.handle_key(self.keyMap[keyNum])
        self.calculator.updateDisplay()

class KeyPadFunctions(Keypad):
    keyMap = ["int", "xy", "pi", "exp",
              "sqrt", "x3", "tan", "log",
              "10x", "x2", "cos", "ln",
              "!", "1/x", "sin", "inv"]

    def __init__(self, driver, base=0):
        Keypad.__init__(self, driver, base)

    def keyup(self, keyNum):
        self.calculator.handle_key(self.keyMap[keyNum])
        self.calculator.updateDisplay()

class KeyPadMemory(Keypad):
    keyMap = ["CLK", "PWR", "M-", "M+", "MR", "MC", "AC", "C"]

    def __init__(self, driver, base=0):
        Keypad.__init__(self, driver, base)

    def keyup(self, keyNum):
        self.calculator.handle_key(self.keyMap[keyNum])
        self.calculator.updateDisplay()

def main():
    bus = smbus.SMBus(1)

    keyPadNumbers = KeyPadNumbers(MCP23017(bus, 0x20))
    keyPadFunctions = KeyPadFunctions(MCP23017(bus, 0x21))
    keyPadMemory = KeyPadMemory(PCF8574(bus,0x22))

#    nixieDisplay = Nixie(PIN_DATA, PIN_LATCH, PIN_CLK, 8, True, True)

    nixieDisplay = Nixie([MCP23017(bus, 0x25),MCP23017(bus, 0x27)], [PCF8574(bus, 0x24),PCF8574(bus, 0x26)], 8, False, False)

    c = PiNixieCalculator(nixieDisplay, [keyPadNumbers, keyPadFunctions, keyPadMemory])
    while True:
        c.poll()

if __name__ == "__main__":
    main()

