"""
    Raspberry Pi Nixie Block using Shift Registrers

    Dr. Scott M Baker, 2014
    http://www.smbaker.com/
    smbaker@smbaker.com
"""

import RPi.GPIO as GPIO
import time
import datetime
import os, sys, termios, tty, fcntl

PIN_DATA = 23
PIN_LATCH = 25 #24 breadboard
PIN_CLK = 24 #25 breadboard

class Nixie:
    def __init__(self, pin_data, pin_latch, pin_clk, digits, flipModules, flipDigits):
        self.pin_data = pin_data
        self.pin_latch = pin_latch
        self.pin_clk = pin_clk
        self.digits = digits
        self.flipModules = flipModules
        self.flipDigits = flipDigits

        GPIO.setmode(GPIO.BCM)

        # Setup the GPIO pins as outputs
        GPIO.setup(self.pin_data, GPIO.OUT)
        GPIO.setup(self.pin_latch, GPIO.OUT)
        GPIO.setup(self.pin_clk, GPIO.OUT)

        # Set the initial state of our GPIO pins to 0
        GPIO.output(self.pin_data, False)
        GPIO.output(self.pin_latch, False)
        GPIO.output(self.pin_clk, False)

    def delay(self):
        # We'll use a 0.1ms delay for our clock
        time.sleep(0.0001)

    def transfer_latch(self):
        # Trigger the latch pin from 0->1. This causes the value that we've
        # been shifting into the register to be copied to the output.
        GPIO.output(self.pin_latch, True)
        self.delay()
        GPIO.output(self.pin_latch, False)
        self.delay()

    def tick_clock(self):
        # Tick the clock pin. This will cause the register to shift its
        # internal value left one position and the copy the state of the DATA
        # pin into the lowest bit.
        GPIO.output(self.pin_clk, True)
        self.delay()
        GPIO.output(self.pin_clk, False)
        self.delay()

    def shift_bit(self, value):
        # Shift one bit into the register.
        GPIO.output(self.pin_data, value)
        # XXX smbaker - if something gets wonky, put delay here XXX+
        self.tick_clock()

    def shift_digit(self, value):
        try:
            value = int(value)
        except ValueError:
            value = 10

        # Shift a 4-bit BCD-encoded value into the register, MSB-first.
        self.shift_bit(value&0x08)
        value = value << 1
        self.shift_bit(value&0x08)
        value = value << 1
        self.shift_bit(value&0x08)
        value = value << 1
        self.shift_bit(value&0x08)

    def set_string(self, str, dp=None):
        if self.flipDigits:
            str = str[::-1]

        if self.flipModules:
            str = str[4:] + str[:4]

        modules = int(self.digits/4)
        for i in range(0, modules):
            nibble = str[:4]
            str = str[4:]

            if (self.flipModules):
                dpoffset = (modules-1-i)*4

            for digit in nibble[:2]:
                self.shift_digit(digit)

            for i in range(0,4):
                self.shift_bit(1)

            for i in range(0,4):
                self.shift_bit(i+dpoffset==dp)

            for digit in nibble[2:]:
                self.shift_digit(digit)

        self.transfer_latch()

    def set_value(self, value, dp=None):
        str = "%0*d" % (self.digits, value)
        self.set_string(str,dp)

TEST_FIXED = "f"
TEST_DIGMOVE = "m"
TEST_COUNT = "c"
TEST_ALL = "a"
TEST_NOP = "n"
TEST_LATCH_FLIPPER = "l"

testmode = TEST_FIXED

def getKey():
   fd = sys.stdin.fileno()
   fl = fcntl.fcntl(fd, fcntl.F_GETFL)
   fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
   old = termios.tcgetattr(fd)
   new = termios.tcgetattr(fd)
   new[3] = new[3] & ~termios.ICANON & ~termios.ECHO
   new[6][termios.VMIN] = 1
   new[6][termios.VTIME] = 0
   termios.tcsetattr(fd, termios.TCSANOW, new)
   key = None
   try:
      key = os.read(fd, 3)
   except:
      return 0
   finally:
      termios.tcsetattr(fd, termios.TCSAFLUSH, old)
   return key

def testpatterns_8dig(nixie):
    global testmode
    val1=0
    val2=0

    while True:
        key = getKey()
        if (key in [TEST_FIXED, TEST_DIGMOVE, TEST_COUNT,TEST_ALL,TEST_NOP,TEST_LATCH_FLIPPER]):
            testmode = key

        if (testmode==TEST_FIXED):
            nixie.set_value(12345678,1)
            time.sleep(1)
        elif (testmode==TEST_DIGMOVE):
            val1 = val1 + 1
            if (val1>=8):
                val1 = 0
                val2 = val2 +1
            if (val2>=10) or (val2<=1):
                val2=1
            nixie.set_value(int( str(val2) + ("0" * val1)))
            time.sleep(0.01)
        elif (testmode==TEST_COUNT):
            val1=val1+1
            nixie.set_value(val1)
            time.sleep(0.001)
        elif (testmode==TEST_ALL):
            val1 = val1 + 1
            if (val1 >= 10):
                val1 = 0
            nixie.set_value(int( str(val1)*8 ))
        elif (testmode==TEST_NOP):
            pass
        elif (testmode==TEST_LATCH_FLIPPER):
            nixie.transfer_latch()
            time.sleep(0.001)

def main():
    try:
        nixie = Nixie(PIN_DATA, PIN_LATCH, PIN_CLK, 8, True, True)

        # Uncomment for a simple test pattern
        # nixie.set_value(12345678)

        testpatterns_8dig(nixie)

        # Repeatedly get the current time of day and display it on the tubes.
        # (the time retrieved will be in UTC; you'll want to adjust for your
        # time zone)

        #while True:
        #    dt = datetime.datetime.now()
        #    nixie.set_value(dt.hour*100 + dt.minute)

    finally:
        # Cleanup GPIO on exit. Otherwise, you'll get a warning next time toy
        # configure the pins.
        GPIO.cleanup()

if __name__ == "__main__":
    main()
