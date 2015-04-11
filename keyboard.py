""" I2C keypad for Raspberry Pi

    Dr. Scott M Baker, 2014
    http://www.smbaker.com/
    smbaker@smbaker.com
"""

import smbus
import time

from ioexpand import *

class Keypad:
   def __init__(self, driver, base=0, led=False):
       self.driver = driver
       self.base = base
       self.keystate = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
       self.keychangetime = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
       self.led = led
       self.configure_driver()

   def configure_driver(self):
       if self.led:
           self.ledbits = 0
           self.driver.configure_as_led_keypad()
           self.banks = 1
           self.driver.set_gpio(1,self.ledbits)   # set all LEDS to off
       else:
           self.driver.configure_as_keypad()
           self.banks = self.driver.banks

   def process_keybit(self, keynum, value):
       if value == self.keystate[keynum]:
           return

       if self.keystate[keynum]==1:
           self.keydown(keynum)
       else:
           self.keyup(keynum)

       self.keystate[keynum] = value

   def keyup(self, keynum):
       pass

   def keydown(self, keynum):
       pass

   def setled(self, led, value):
       mask = 1 << led
       if value:
           bit = mask
       else:
           bit = 0

       self.ledbits = self.ledbits & (~mask & 0xFF) | bit
       self.driver.set_gpio(1,self.ledbits)

   def poll(self):
       for bank in range(0, self.banks):
           keys=~self.driver.get_gpio(bank)
           for i in range(0, 8):
               self.process_keybit(i+bank*8, keys & 1)
               keys = keys >> 1

class KeyPrinter(Keypad):
    def __init__(self, driver, base=0, led=False):
        Keypad.__init__(self, driver, base, led)

    def keyup(self, keynum):
       print "K%d down" % (keynum+self.base)

    def keydown(self, keynum):
       print "K%d up" % (keynum+self.base)

def test():
    """ keyboard self-test.

        Configured for three keypads:
           MCP23017 at 0x20   (16 keys)
           MCP23017 at 0x21   (16 keys)
           PCF8574 at 0x22    (8 keys)
    """
    bus = smbus.SMBus(1)
    kp = KeyPrinter(MCP23017(bus, 0x20), 0)
    kp2 = KeyPrinter(MCP23017(bus, 0x21), 100)
    kp3 = KeyPrinter(PCF8574(bus, 0x22), 200)
    while 1:
       kp.poll()
       kp2.poll()
       kp3.poll()

def test2():
    """ LED keyboard self-test.

        Configured for three keypads:
           MCP23017 at 0x20   (16 keys)
           MCP23017 at 0x21   (16 keys)
           PCF8574 at 0x22    (8 keys)
    """
    bus = smbus.SMBus(1)
    kp = KeyPrinter(MCP23017(bus, 0x20), 0, led=True)
    while 1:
       kp.poll()


if __name__ == "__main__":
   test2()


