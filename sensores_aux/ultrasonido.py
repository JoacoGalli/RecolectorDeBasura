# Importamos la paquteria necesaria
import RPi.GPIO as GPIO
import time
import csv
import threading


TRIG = 16 #Variable que contiene el GPIO al cual conectamos la señal TRIG del sensor
ECHO =18 #Variable que contiene el GPIO al cual conectamos la señal ECHO del sensor
sound_speed = 34300

GPIO.setmode(GPIO.BCM)     #Establecemos el modo según el cual nos refiriremos a los GPIO de nuestra RPi            
GPIO.setup(TRIG, GPIO.OUT) #Configuramos el pin TRIG como una salida 
GPIO.setup(ECHO, GPIO.IN)  #Configuramos el pin ECHO como una salida 


#Contenemos el código principal en un aestructura try para limpiar los GPIO al terminar o presentarse un error
#try:
    #Implementamos un loop infinito
#    while True:
def sensar_tacho():
        # Ponemos en bajo el pin TRIG y después esperamos 0.5 seg para que el transductor se estabilice
        GPIO.output(TRIG, GPIO.LOW)
        time.sleep(0.7)

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
        #print(f"la distancia es {distancia}")
        return distancia 
        # Imprimimos resultado
        
#finally:
    # Reiniciamos todos los canales de GPIO.
    #GPIO.cleanup()

class Motores_rotacion(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.deamon = True
        self.motores_status = 'off' # on, off, reset
        self.sentido = None # "right" "left"
        self.config()
        self.stop_event = threading.Event()
        

    def config(self):
        # ver si los definimos a los 2 iguales
        self.dir = 26 
        self.step = 19 
        self.velocidad = .01

        # Setup pin layout on PI
        GPIO.setmode(GPIO.BCM)

        # Establish Pins in software
        GPIO.setup(self.dir, GPIO.OUT)
        GPIO.setup(self.step, GPIO.OUT)

        # Set the first direction you want it to spin
        GPIO.output(self.dir, 1)

    def activar_motores_rotacion(self):

            print("rotando")
            GPIO.output(self.dir,1)
            
            while self.motores_status == "on":
                print("tengo que arrancar")
                time.sleep(0.01)
                # Run for 200 steps. This will change based on how you set you controller
                for x in range(200):

                    # Set one coil winding to high
                    GPIO.output(self.step,GPIO.HIGH)
                    # Allow it to get there.
                    time.sleep(self.velocidad) # Dictates how fast stepper motor will run
                    # Set coil winding to low
                    GPIO.output(self.step,GPIO.LOW)
                    time.sleep(self.velocidad) # Dictates how fast stepper motor will run
                    #finish_time = time.time()
    def fin(self):
        self.stop_event.set()
    
    def run(self):
        while not self.stop_event.is_set():
            if self.motores_status == 'on':
                self.activar_motores_rotacion()
            elif self.motores_status == 'off':
                #print("se deberia apagar")
                #self.reset_motores_traslacion()
                
                time.sleep(0.1)
            else:
                pass

if __name__ == "__main__":
    #GPIO.cleanup()
  
        rotacion = Motores_rotacion()
        rotacion.start()
        time.sleep(2)
        rotacion.motores_status = 'on'
# field names 
        fields = ['distancia'] 
        list_llenado = []
        for x in range(60):
                time.sleep(0.2)
                distancia = sensar_tacho()
                list_llenado.append(distancia)
        print(f'{list_llenado=}')
        rows = []
        for n in list_llenado:
                print(f"{str(n)=}")
                rows.append([str(n)])
        print(rows)
# data rows of csv file 
          
        with open('tacho_goma_motor', 'w') as f:
              
            # using csv.writer method from CSV package
            write = csv.writer(f)
              
            write.writerow(fields)
            write.writerows(rows)
        rotacion.motores_status = 'off'
        rotacion.fin()
        GPIO.cleanup()
