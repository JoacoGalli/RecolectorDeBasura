import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib as motor
import time

# Infrarrojos
sensor = 8
GPIO.setmode(GPIO.BOARD)
GPIO.setup(sensor,GPIO.IN)

def medir_si_esta_ponton():
    print("Estamos listos para arrancar a medir")
    ti = time.time()
    tf = time.time()
    while(tf - ti < 1):
        if (not GPIO.input(sensor)):
            ponton = True
            #print("Ponton detectado")
            while GPIO.input(sensor):
                time.sleep(0.2)
        else:
            #print("No se detecto el ponton")
            ponton = False
        tf = time.time()
    # GPIO.cleanup() hay que ponerlo aca??
    return ponton

if __name__ == "__main__":
    print("vamo a arrancar")
    ponton = medir_si_esta_ponton()
    if ponton:
        print("Se detecto el ponton")
    else:
        print("No se detecto el ponton")