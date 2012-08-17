#!/usr/bin/env python
import time
import os
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
DEBUG = 0

# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)

        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)     # bring CS low

        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1

        GPIO.output(cspin, True)
        
        adcout >>= 1       # first bit is 'null' so drop it
        return adcout

# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25
mosi = 19
# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)
# 10k trim pot connected to adc #0
potentiometer_adc = 0;

last_read = 0       # this keeps track of the last potentiometer value
tolerance = 25       # to keep from being jittery
2readsago = 0       # to keep from lights turning off too soon? maybe?

while True:
        # we'll assume that the pot didn't move
        read_changed = False

        # read the analog pin
        read = readadc(potentiometer_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
        # how much has it changed since the last read?
        if tolerance < abs(read - last_read):
            read_changed = True
            
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(19, GPIO.OUT)
        if read_changed:
            print read
            if read > 700 and last_read > 2readsago:
                GPIO.output(19, GPIO.LOW)
                print "Lights Off"

            if read < 700:
                GPIO.output(19, GPIO.HIGH)
                print "Lights On"
        GPIO.setmode(GPIO.BCM)
        ##if ( trim_pot_changed ):
        

        # save the potentiometer reading for the next loop
        2readsago = last_read
        last_read = read
        # hang out and do nothing for a half second
        time.sleep(1)
