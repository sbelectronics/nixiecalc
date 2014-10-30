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
import smbus
from ioexpand import *

class Nixie:
    def __init__(self, drivers, dpDrivers, digits, flipModules, flipDigits):
        self.drivers = drivers
        self.dpDrivers = dpDrivers
        self.digits = digits
        self.flipModules = flipModules
        self.flipDigits = flipDigits

        for driver in self.drivers:
            driver.configure_as_display()

    def get_bcd(self, c):
        try:
            return int(c)
        except ValueError:
            return 10

    def set_string(self, str, dp=None):
        str = str[:self.digits]

        if self.flipDigits:
            str = str[::-1]

        if dp is not None:
            dp=7-dp

        for driver in self.drivers:
            for bank in range(0,driver.banks):
                nibble = str[:2]
                str = str[2:]

                driver.set_gpio(bank, self.get_bcd(nibble[0]) + (self.get_bcd(nibble[1]) << 4))

        for (offset,driver) in enumerate(self.dpDrivers):
            value = 0
            if (dp is not None):
                if (dp>=offset*4) and (dp<offset*4+4):
                    value = 1<<(dp%4)

            driver.set_gpio(0, value)


    def set_value(self, value, dp=None):
        str = "%0*d" % (self.digits, value)
        self.set_string(str,dp)

TEST_FIXED = "f"
TEST_DIGMOVE = "m"
TEST_COUNT = "c"
TEST_ALL = "a"
TEST_NOP = "n"
TEST_LATCH_FLIPPER = "l"
TEST_CLOCK = "k"
TEST_DP ="d"

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
        if (key in [TEST_FIXED, TEST_DIGMOVE, TEST_COUNT,TEST_ALL,TEST_NOP,TEST_LATCH_FLIPPER,TEST_CLOCK,TEST_DP]):
            testmode = key

        if (testmode==TEST_FIXED):
            nixie.set_value(12345678,7)
            time.sleep(1)
        elif (testmode==TEST_DIGMOVE):
            val1 = val1 + 1
            if (val1>=8):
                val1 = 0
                val2 = val2 +1
            if (val2>=10) or (val2<=1):
                val2=1
            nixie.set_value(int( str(val2) + ("0" * val1)))
            time.sleep(0.1)
        elif (testmode==TEST_COUNT):
            val1=val1+1
            nixie.set_value(val1)
            time.sleep(0.1)
        elif (testmode==TEST_ALL):
            val1 = val1 + 1
            if (val1 >= 10):
                val1 = 0
            nixie.set_value(int( str(val1)*8 ))
            time.sleep(0.1)
        elif (testmode==TEST_NOP):
            pass
        elif (testmode==TEST_CLOCK):
            dt = datetime.datetime.now()
            nixie.set_string("%02d%02d" % (dt.hour, dt.minute))
            time.sleep(0.1)
        elif (testmode==TEST_LATCH_FLIPPER):
            nixie.transfer_latch()
            time.sleep(0.001)
        elif (testmode==TEST_DP):
            val1 = val1 + 1
            if (val1>7):
                val1 = 0
            nixie.set_value(12345678,val1)
            time.sleep(0.1)

def main():
    try:
        bus = smbus.SMBus(1)
        nixie = Nixie([MCP23017(bus, 0x25),MCP23017(bus, 0x27)], [PCF8574(bus, 0x24),PCF8574(bus, 0x26)], 8, False, False)

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
