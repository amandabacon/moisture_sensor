
#!/usr/bin/python3

# Moisture sensor reading of soil
# Author: Amanda & Inigo
# Date: 03/04/2019

import smbus
import RPi.GPIO as GPIO
from time import *

GPIO.setmode(GPIO.BOARD)
bus = smbus.SMBus(1)

#ADC device information
DEVICE_ADDRESS = 0x48
CONFIG_REGISTER = 0x1
CONVERSION_REGISTER = 0x0

#LED i2c backpack information
DEVICE_ADDRESS_2 = 0x70
CONFIG_REGISTER_2 = 0b00100001
CONVERSION_REGISTER_2 = 0x0

clock_enable = 0b00100001
row_int = 0b10100000
dimming = 0b11100111
blinking = 0b10000101

address_setting = 0b01000000
display_ram =  0b000000000
display_on = 0b10000001

def configure_backpack(bus):
	con = [0x0,0x0]
	bus.write_i2c_block_data(DEVICE_ADDRESS_2, clock_enable,con)
	bus.write_i2c_block_data(DEVICE_ADDRESS_2, row_int,con)
	bus.write_i2c_block_data(DEVICE_ADDRESS_2, dimming,con)
	bus.write_i2c_block_data(DEVICE_ADDRESS_2, blinking,con)


#define a function that will take a string value of the moistness and convert it to the number corresponding to the 7-segment display output
def choose_mode(num):
	if (num == '0'):
		return 63

	if (num =='1'):
		return 6

	if (num == '2'):
		return 91

	if (num == '3'):
		return 79

	if (num == '4'):
		return 102

	if (num == '5'):
		return 109

	if (num == '6'):
		return 125

	if (num == '7'):
		return 7

	if (num == '8'):
		return 127

	if (num == '9'):
		return 111

	else:
		return 54

#define a function that will take a string value of the moistness and convert it to the number corresponding to the 7-segment display output with a period
def choose_mode_period(num):
	if (num == '0'):
		return 63+128 #where +128 is to find the period

	if (num =='1'):
		return 6+128

	if (num == '2'):
		return 91+128

	if (num == '3'):
		return 79+128

	if (num == '4'):
		return 102+128

	if (num == '5'):
		return 109+128

	if (num == '6'):
		return 125+128

	if (num == '7'):
		return 7+128

	if (num == '8'):
		return 127+128

	if (num == '9'):
		return 111+128

	else:
		return 54+128

#define a function that will output the moistness (moistness)
def write_raw_backpack(bus, moistness):
	bus.write_i2c_block_data(DEVICE_ADDRESS_2, address_setting, [1])
	bus.write_i2c_block_data(DEVICE_ADDRESS_2, display_ram, [1])
	bus.write_i2c_block_data(DEVICE_ADDRESS_2, display_on, [])

#the commented section below was used for debugging purposes
#	i = 128
#	while True:
#		bus.write_i2c_block_data(DEVICE_ADDRESS_2, address_setting, [])
#		bus.write_i2c_block_data(DEVICE_ADDRESS_2, display_ram, [i,i,i,i,i,i,i,i,i,i,i,i,i])
#		print(i)
#		sleep(1)
#		i=i+1
#	bus.write_i2c_block_data(DEVICE_ADDRESS_2, display_on, [])

#this is where we convert the moistness to a string (and multiply by 1000 in order to move the decimal point)
	moistness = str(moistness*1000)
#chooses a moistness range for the different outputs (of course it cannot read the extreme values)
	bus.write_i2c_block_data(DEVICE_ADDRESS_2, address_setting, [])
	bus.write_i2c_block_data(DEVICE_ADDRESS_2, display_ram, [choose_mode(moistness[0]),0,choose_mode(moistness[1]),0,0,0,choose_mode_period(moistness[2]),0,choose_mode(moistness[3]),0])

#notes below here for debugging purposes
#
#		bus.write_i2c_block_data(device address, address_setting, [does nothing])
#                bus.write_i2c_block_data(device address, display_ram, [chunck of LED 1, nonsense number, chunck of LED 2, nonsense number, colon, nonsense number,chunck of LED 3, nonsense number,chunck of LED 4, nonsense number,])

#	for i in range(70):
#		bus.write_i2c_block_data(DEVICE_ADDRESS_2, address_setting, [1])
#		bus.write_i2c_block_data(DEVICE_ADDRESS_2, display_ram, [i])
#		sleep(2)
#	bus.write_i2c_block_data(DEVICE_ADDRESS_2, display_on, [])
#end of notes

#defines a function that will configure the ADC
def configure_adc(bus):
	config_bytes = [0xc0, 0x83]
	bus.write_i2c_block_data(DEVICE_ADDRESS, CONFIG_REGISTER, config_bytes)

#defines a function that will get the raw data info.
def get_raw_adc_reading(bus):
	raw_reading = bus.read_i2c_block_data(DEVICE_ADDRESS,CONVERSION_REGISTER)
	MSB = raw_reading[0] << 8
	raw = MSB + raw_reading[1]
#	rawstr = str(bin(raw))
#	print(raw)
#	print("rawstr ", rawstr)
#	if raw >= (2**15):
#		raw = 0
	return raw

def convert_raw_to_moisture(raw):
	ratio = 8.8
	moistness = ((raw)/(ratio))
	return moistness

#defines a function that initialises the GPIO pins for the 5 LEDs
def initialize_GPIO(): #sets all GPIO pins in use for LEDs
	GPIO.setup(11, GPIO.OUT)
	GPIO.setup(13, GPIO.OUT)
	GPIO.setup(15, GPIO.OUT)
	GPIO.setup(16, GPIO.OUT)
	GPIO.setup(18, GPIO.OUT)
	for i in range(3): #blinks all LEDs three times
		GPIO.output(11, GPIO.HIGH)
		GPIO.output(13, GPIO.HIGH)
		GPIO.output(15, GPIO.HIGH)
		GPIO.output(16, GPIO.HIGH)
		GPIO.output(18, GPIO.HIGH)
		sleep(1)
		GPIO.output(11, GPIO.LOW)
		GPIO.output(13, GPIO.LOW)
		GPIO.output(15, GPIO.LOW)
		GPIO.output(16, GPIO.LOW)
		GPIO.output(18, GPIO.LOW)
		sleep(1)

#defines a function that shines specific LEDs in ranges defined below depending on moistness
def shine_moistness(moistness):
	if moistness < 0: #all off (bone dry)
		GPIO.output(11, GPIO.LOW)
		GPIO.output(13, GPIO.LOW)
		GPIO.output(15, GPIO.LOW)
		GPIO.output(16, GPIO.LOW)
		GPIO.output(18, GPIO.LOW)
	elif moistness >= 0 and moistness < 20: #only pin 11 on (dry)
		GPIO.output(11, GPIO.HIGH)
		GPIO.output(13, GPIO.LOW)
		GPIO.output(15, GPIO.LOW)
		GPIO.output(16, GPIO.LOW)
		GPIO.output(18, GPIO.LOW)
	elif moistness >= 20 and moistness < 40: #pin 11 and 13 on (semi-dry)
		GPIO.output(11, GPIO.HIGH)
		GPIO.output(13, GPIO.HIGH)
		GPIO.output(15, GPIO.LOW)
		GPIO.output(16, GPIO.LOW)
		GPIO.output(18, GPIO.LOW)
	elif moistness >= 40 and moistness < 60: #pin 11,13,15 on (semi-wet)
		GPIO.output(11, GPIO.HIGH)
		GPIO.output(13, GPIO.HIGH)
		GPIO.output(15, GPIO.HIGH)
		GPIO.output(16, GPIO.LOW)
		GPIO.output(18, GPIO.LOW)
	elif moistness >= 60 and moistness < 80: #pin 11,13,15,16 on (wet)
		GPIO.output(11, GPIO.HIGH)
		GPIO.output(13, GPIO.HIGH)
		GPIO.output(15, GPIO.HIGH)
		GPIO.output(16, GPIO.HIGH)
		GPIO.output(18, GPIO.LOW)
	else: #anything beyond bounds--turns on (sea levels)
		GPIO.output(11, GPIO.HIGH)
		GPIO.output(13, GPIO.HIGH)
		GPIO.output(15, GPIO.HIGH)
		GPIO.output(16, GPIO.HIGH)
		GPIO.output(18, GPIO.HIGH)


#main
configure_adc(bus)

configure_backpack(bus)

raw_adc = get_raw_adc_reading(bus)
print(raw_adc)
moistness = convert_raw_to_moisture(raw_adc)
print("This is the moisture reading: ", moistness)

initialize_GPIO()

#infinite loop checking and printing of values
while True:
	raw_adc = get_raw_adc_reading(bus)
	moistness = convert_raw_to_moisture(raw_adc)
	print(moistness)
	write_raw_backpack(bus,moistness)
	shine_moistness(moistness)
	sleep(5)
