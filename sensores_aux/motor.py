import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib as motor
import time

direction = 22
step = 23
en_pin = 24

mymotortest =  motor.A4988Nema(direction, step, (14, 15, 18),"A4988")
GPIO.setup(en_pin, GPIO.OUT)

dir_array = [False, True]
GPIO.output(en_pin, GPIO.LOW)

dir_arr = [False,True]
start_time = time.time()
finish_time = time.time()
while finish_time - start_time < 10:
    mymotortest.motor_go(False,"Full", 2000,.01, False, .005)
    print("girando")
    finish_time = time.time()

#time.sleep(10)
GPIO.cleanup()
