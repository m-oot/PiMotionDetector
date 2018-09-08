
import sys
import termios
import tty
import os
import RPi.GPIO as GPIO
import time

servoPIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)

currentDC = 6
right = 12.5
middle = 6
left = 2.5

def move(n):
   p.ChangeDutyCycle(n)

def getch():
   fd = sys.stdin.fileno()
   old_settings = termios.tcgetattr(fd)
   try:
      tty.setraw(sys.stdin.fileno())
      ch = sys.stdin.read(1)
 
   finally:
      termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
   return ch
 
button_delay = 0.2

p = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz
p.start(2.5) # Initialization
try:
  while True:
    char = getch()
 
    if (char == "q"):
        GPIO.cleanup()
        exit(0)

    if (char == "l"):
        move(left)
        print("l pressed")


    if (char == "j"):
        move(right)
        print("j pressed")

    if (char == "k"):
        move(middle)
        print("k pressed")

except KeyboardInterrupt:
  p.stop()
  GPIO.cleanup()
