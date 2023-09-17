import RPi.GPIO as GPIO
from threading import Thread
import time

# Ultrasonido
TRIG = 16
ECHO = 18

# Direction pin from controller
DIR = 10
# Step pin from controller
STEP = 8
# 0/1 used to signify clockwise or counterclockwise.


# Set the first direction you want it to spin

def nema_27_rigth():
    CW = 1
    start = time.time()
    finished = time.time()
    while finished-start < 10:
        # Esablish the direction you want to go
        GPIO.output(DIR,CW)

        # Run for 200 steps. This will change based on how you set you controller
        for x in range(200):

            # Set one coil winding to high
            GPIO.output(STEP,GPIO.HIGH)
            # Allow it to get there.
            time.sleep(.005) # Dictates how fast stepper motor will run
            # Set coil winding to low
            GPIO.output(STEP,GPIO.LOW)
            time.sleep(.005) # Dictates how fast stepper motor will run
        finished = time.time()

def nema_27_left():
    CCW = 0

    GPIO.output(DIR,CCW)
    for x in range(200):
        GPIO.output(STEP,GPIO.HIGH)
        time.sleep(.005)
        GPIO.output(STEP,GPIO.LOW)
        time.sleep(.005)

def ultasonido():
    sound_speed = 34300
    GPIO.output(TRIG, GPIO.LOW)
    time.sleep(0.5)
    GPIO.output(TRIG, GPIO.LOW)
    time.sleep(0.0001)
    GPIO.output(TRIG, GPIO.LOW)

    start = time.time()
    finished = time.time()
    while finished-start < 10:
        pulso_inicio = time.time()
        if GPIO.input(ECHO) == GPIO.HIGH:
            break
        while True:
            pulso_fin = time.time()
            if GPIO.input(ECHO) == GPIO.LOW:
                break
        
        duracion = pulso_fin - pulso_inicio
        distancia = (sound_speed * duracion) / 2
        print(f'La distancia es: {distancia}')
        finished = time.time()

# Once finished clean everything up
def stop():
	print("cleanup")
	GPIO.cleanup()

def setup():
    GPIO.cleanup()
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)
    GPIO.setup(DIR, GPIO.OUT)
    GPIO.setup(STEP, GPIO.OUT)


if __name__ == '__main__':
    print("arranco")
    nema_thread = Thread(target = nema_27_rigth)
    ultrasonido_thread = Thread(target = ultasonido)
    time_s = time.time()
    nema_thread.start()
    ultrasonido_thread.start()
    time_f = time.time()

    while time_f - time_s < 20:
        print("activo")
        time.sleep(1)
        time_f = time.time()

    stop()
