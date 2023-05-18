import RPi.GPIO as GPIO
from threading import Thread
import time

# Ultrasonido
TRIG = 23 
ECHO = 24

# Direction pin from controller
DIR = 15
# Step pin from controller
STEP = 14
# 0/1 used to signify clockwise or counterclockwise.


# Set the first direction you want it to spin

def nema_27_rigth():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DIR, GPIO.OUT)
    GPIO.setup(STEP, GPIO.OUT)

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

def ultrasonido():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)

    sound_speed = 34300
    GPIO.output(TRIG, GPIO.LOW)
    time.sleep(0.5)

        #Ponemos en alto el pin TRIG esperamos 10 uS antes de ponerlo en bajo
    GPIO.output(TRIG, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG, GPIO.LOW)

        # En este momento el sensor envía 8 pulsos ultrasónicos de 40kHz y coloca su pin ECHO en alto
        # Debemos detectar dicho evento para iniciar la medición del tiempo
        
    while True:
        pulso_inicio = time.time()
        if GPIO.input(ECHO) == GPIO.HIGH:
            break

        # El pin ECHO se mantendrá en HIGH hasta recibir el eco rebotado por el obstáculo. 
        # En ese momento el sensor pondrá el pin ECHO en bajo.
	# Prodedemos a detectar dicho evento para terminar la medición del tiempo
        
    while True:
        pulso_fin = time.time()
        if GPIO.input(ECHO) == GPIO.LOW:
            break

    # Tiempo medido en segundos
    duracion = pulso_fin - pulso_inicio

    #Obtenemos la distancia considerando que la señal recorre dos veces la distancia a medir y que la velocidad del sonido es 343m/s
    distancia = (sound_speed * duracion) / 2
    return distancia 
    # Imprimimos resultado

def ultrasonido2():
    for x in range(20):
        distancia =  ultrasonido()
        print(f'la distancia es: {distancia} cm ')
        
# Once finished clean everything up
def stop():
	print("cleanup")
	GPIO.cleanup()

if __name__ == '__main__':
    #setup()
    nema_thread = Thread(target = nema_27_rigth)
    ultrasonido_thread = Thread(target = ultrasonido2)
    time_s = time.time()
    nema_thread.start()
    ultrasonido_thread.start()
    time_f = time.time()

    while time_f - time_s < 20:
        time.sleep(1)
        time_f = time.time()

    stop()    
