import time
import threading
import RPi.GPIO as GPIO
from mqtt_influx_class import MQTTClient

from clases import Motores_rotacion, Motores_traslacion, Maquina_del_mal, Camara

if __name__ == "__main__":
    # Se inicializan las clases en threads diferentes.
    mqtt_client = MQTTClient()
    mqtt_thread = threading.Thread(target=mqtt_client.run_mqtt_client)
    mqtt_thread.start()


    motor_rotacion_dist = Motores_rotacion(mqtt_client, "dist", 80)
#    motor_rotacion_cap = Motores_rotacion(mqtt_client, "cap", camara.buffer)
#    traslacion = Motores_traslacion(mqtt_client)
#    time.sleep(1)
    motor_rotacion_dist.start()
 #   motor_rotacion_cap.start()
 #   traslacion.start()

#    maquina = Maquina_del_mal(mqtt_client)
#    time.sleep(1)
    
#    orden_llenado = [3,7,2,6,1,5,0,4]
    motor_rotacion_dist.estado ="on"
    print("arranco")
    time.sleep(2)
    motor_rotacion_dist.estado ="off"
    motor_rotacion_dist.fin()
    print("termine")
    motor_rotacion_dist.stop()
    # Enviar metrica codigo en proceso.
