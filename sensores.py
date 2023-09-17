import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib as motor
import time

# Infrarrojos
sensor = 16
buzzer = 18
GPIO.setmode(GPIO.BOARD)
GPIO.setup(sensor,GPIO.IN)
GPIO.setup(buzzer,GPIO.OUT)
GPIO.output(buzzer,False)



# Ultrasonido distancia cinta
TRIG = 23 #Variable que contiene el GPIO al cual conectamos la señal TRIG del sensor
ECHO = 24 #Variable que contiene el GPIO al cual conectamos la señal ECHO del sensor
sound_speed = 34300

GPIO.setmode(GPIO.BCM)     #Establecemos el modo según el cual nos refiriremos a los GPIO de nuestra RPi            
GPIO.setup(TRIG, GPIO.OUT) #Configuramos el pin TRIG como una salida 
GPIO.setup(ECHO, GPIO.IN)  #Configuramos el pin ECHO como una salida

# Motro traslacion
direction_tras1 = 25
step_tras1 = 26
en_pin_tras1 = 27
motor_traslacion=  motor.A4988Nema(direction_tras1, step_tras1, (14, 15, 18),"A4988")
GPIO.setup(en_pin_tras1, GPIO.OUT)
GPIO.output(en_pin_tras1, GPIO.LOW)


# Motro rotacion1
direction_rot1 = 28
step_rot1 = 29
en_pin_rot1 = 30
motor_rotacion_1 =  motor.A4988Nema(direction_rot1, step_rot1, (14, 15, 18),"A4988")
GPIO.setup(en_pin_rot1, GPIO.OUT)
GPIO.output(en_pin_rot1, GPIO.LOW)


# Motro rotacion2 
direction_rot2 = 31
step_rot2 = 32
en_pin_rot2 = 33
motor_rotacion_2 =  motor.A4988Nema(direction_rot2, step_rot2, (14, 15, 18),"A4988")
GPIO.setup(en_pin_rot2, GPIO.OUT)
GPIO.output(en_pin_rot2, GPIO.LOW)

def medir_si_esta_ponton():
    ti = time.time()
    tf = time.time()
    while(tf - ti < 1):
        if GPIO.input(sensor):
            GPIO.output(buzzer,True)
            ponton = True
            print("Ponton detectado")
            while GPIO.input(sensor):
                time.sleep(0.2)
        else:
            GPIO.output(buzzer,False)
            print("no hay ponton")
            ponton = False
        tf = time.time()
    # GPIO.cleanup() hay que ponerlo aca??
        return ponton

def medir_ubicacion_cinta():
        # Ponemos en bajo el pin TRIG y después esperamos 0.5 seg para que el transductor se estabilice
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

        # Faltaria definir que la distancia sea una posicion
        if distancia < 20:
            posicion = 1
        elif 20 < distancia < 40:
            posicion = 2
        elif 40 < distancia < 60:
            posicion = 3
        elif 60 < distancia < 80:
            posicion = 4
        else:
            posicion = False
        return posicion


def mover_cinta_traslacion(nueva_posicion):
    start_time = time.time()
    finish_time = time.time()

    # dependiendo la posicion y el sentido elijo el tiempo con un dicionario

    while finish_time - start_time < 10:
        motor_traslacion.motor_go(False,"Full", 2000,.01, False, .005)
        print("girando")
        finish_time = time.time()

def medir_buffer():
    # hay que usar el codigo de control
    pass

def activar_motores_rotacion():
    # se tiene que activar 2 motores
    # ver el 
    while True:
        motor_rotacion_1.motor_go(False,"Full", 2000,.01, False, .005)
        motor_rotacion_2.motor_go(False,"Full", 2000,.01, False, .005)
        
        print("girando")
def reset_motores_rotacion():
    # esto limpia todo el GPIO hay que limpiar solo los del motor OJOOO
    GPIO.cleanup()
