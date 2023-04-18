#!/usr/bin/python
import RPi.GPIO as GPIO
import time

PIN_TRIGGER = 23
PIN_ECHO = 24

def conf_ultrasonido():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN_TRIGGER, GPIO.OUT)
    GPIO.setup(PIN_ECHO, GPIO.IN)

def medir_ubicacion_cinta():
    # Ponemos en bajo el pin TRIG y después esperamos 0.5 seg para que el transductor se estabilice
    GPIO.output(PIN_TRIGGER, GPIO.LOW)
#     print("Waiting for sensor to settle")
    time.sleep(2)
    #print("Calculating distance")
    GPIO.output(PIN_TRIGGER, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(PIN_TRIGGER, GPIO.LOW)
    while GPIO.input(PIN_ECHO)==0:
        pulse_start_time = time.time()
    while GPIO.input(PIN_ECHO)==1:
        pulse_end_time = time.time()

    pulse_duration = pulse_end_time - pulse_start_time
    distance = round(pulse_duration * 17150, 2)
    print("Distancia:",distance,"cm")
    return distance

if __name__ == "__main__":
    #GPIO.cleanup()
    conf_ultrasonido()
    while True:
        distancia = medir_ubicacion_cinta()
#         print(distancia)
    GPIO.cleanup()
    