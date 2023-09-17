import time
import logging

from clases import Motores_rotacion, Motores_traslacion, Maquina_del_mal, Camara
import threading
from mqtt_influx_class import MQTTClient
import sys
import RPi.GPIO as GPIO


def elegir_tacho_a_llenar(cont, maquina, traslacion, ORDEN_LLENADO):
    print(f"{ORDEN_LLENADO=}")
    clockwise = None
    sensor = None
    while ORDEN_LLENADO:
        print(f"El que deberia llenar es {ORDEN_LLENADO[0]=}")
        if ORDEN_LLENADO[0] in [0,1,2,3]:
            clockwise = 0
            sensor = 1
        else:
            clockwise = 1
            sensor = 2
                    
        mover_cinta(maquina, traslacion, ORDEN_LLENADO[0])
        time.sleep(0.2)
        maquina.medir_llenado_tachos(sensor,ORDEN_LLENADO[0])
        time.sleep(0.2) 

        if cont[str(ORDEN_LLENADO[0])] < 70: # Este 90 tiene que coincidir con el que hace prender los motores en el main
            pos = ORDEN_LLENADO[0]
            print(f"te mando a llenar este: {ORDEN_LLENADO[0]}")
            print(f"{ORDEN_LLENADO=}")
            ORDEN_LLENADO.remove(ORDEN_LLENADO[0])
            return pos, clockwise, sensor

        print(f"pase por {ORDEN_LLENADO[0]} y era mas de 50")
        ORDEN_LLENADO.remove(ORDEN_LLENADO[0])

    print("Los contenedores estan llenos")     
    return None,0,1

def mover_cinta(maquina, traslacion, pos):
    #maquina.medir_ubicacion_cinta_inicial() 
    if (maquina.posicion_media[str(pos)]-0.65 < maquina.posicion_cinta_cm < maquina.posicion_media[str(pos)]+0.65):
        print("La cinta se encuentra posicionada en el contenedor a llenar.")
    else:
        if (maquina.posicion_cinta_cm - maquina.posicion_media[str(pos)]) > 0 :
            traslacion.clockwise = False
            traslacion.motores_status = "on"

        elif (maquina.posicion_cinta_cm - maquina.posicion_media[str(pos)]) <  0 :
            traslacion.clockwise = True
            traslacion.motores_status = "on"

        while not( maquina.posicion_media[str(pos)] - 0.65 < maquina.posicion_cinta_cm < maquina.posicion_media[str(pos)] + 0.65) :
            maquina.ubicacion_cinta(traslacion.clockwise)
            #time.sleep(0.1)
        
        traslacion.motores_status = "off"

    print("llegue al que elegi, ahora lleno")



if __name__ == "__main__":
    #GPIO.cleanup()
    print("Inicio.")
    GPIO.setwarnings(False)
    # Definimos las 3 clases (3 threads)
    mqtt_client = MQTTClient()
    mqtt_thread = threading.Thread(target=mqtt_client.run_mqtt_client)
    mqtt_thread.start()
    camara = Camara(mqtt_client)
    camara.start()
    maquina = Maquina_del_mal(mqtt_client)
    motor_rotacion_dist = Motores_rotacion(mqtt_client,tipo="dist", camara=camara.buffer)
    motor_rotacion_cap = Motores_rotacion(mqtt_client, tipo="cap", camara=camara.buffer)
    traslacion = Motores_traslacion(mqtt_client)
    time.sleep(1)
    motor_rotacion_dist.start()
    motor_rotacion_cap.start()
    traslacion.start()
    time.sleep(1)
    camara.buffer = 25
    ORDEN_LLENADO = [3,7,2,6,1,5,0,4]
    #ORDEN_LLENADO = [7,2,6,1,5,0,4]
    #ORDEN_LLENADO = [0,4]
    
    #ORDEN_LLENADO = [0,4]
    tacho_actual = 10
    mqtt_client.send_metric("metricas/codigo", 1)
    print("Estado = Activo")
    
    while(True):
        if maquina.esta_ponton() and tacho_actual != None:
            maquina.medir_ubicacion_cinta_inicial()
            tacho_actual, motor_rotacion_dist.sentido, maquina.sensor = elegir_tacho_a_llenar(maquina.contenedores, maquina, traslacion, ORDEN_LLENADO) # elige un tacho, si estan todos llenos devuelve false, con motores_rotacion ademas elige el sentido de rotacion (ej: 1,2,3,4 entonces izquierda)
            mqtt_client.send_metric("metricas/distribucion_pos_nro_cont", tacho_actual)

            #while tacho_actual:
            if camara.buffer > 15 or tacho_actual != None:
                motor_rotacion_cap.motores_status = "on"
                
                while camara.buffer > 5 and tacho_actual != None:
                    print("El buffer tiene suficiente basura.\n Se activan los motores")
                    print(f"El % de llenado de los contenedores es: {maquina.contenedores}")
                    motor_rotacion_dist.motores_status = "on"
                    
                    while maquina.contenedores[str(tacho_actual)] < 50:  # este 90 tiene que coincidir con el de elegir_tacho_a_llenar()
                        maquina.medir_llenado_tachos(maquina.sensor,tacho_actual)
                        print(f"El % de llenado de los contenedores es: {maquina.contenedores}")
                    
                    motor_rotacion_dist.motores_status = "off"
                    time.sleep(0.2) 
                    tacho_actual, motor_rotacion_dist.sentido, maquina.sensor = elegir_tacho_a_llenar(maquina.contenedores, maquina, traslacion, ORDEN_LLENADO) # elige un tacho, si estan todos llenos devuelve false, con motores_rotacion ademas elige el sentido de rotacion (ej: 1,2,3,4 entonces izquierda)
                    mqtt_client.send_metric("metricas/distribucion_pos_nro_cont", tacho_actual)
                    
                    if tacho_actual == None:
                        motor_rotacion_cap.motores_status = "off"
                        print("Los contenedores estan llenos.\nVaciar contenedores.\nFin del programa.")
                        mqtt_client.send_metric("metricas/codigo", 0)
                        break
                        
            elif camara.buffer < 5 and tacho_actual != None:
                print("Estado = Reposo")
                print(f"El buffer no tiene suficiente basura {camara.buffer}, continuo sacando fotos y verificando.")
                motor_rotacion_cap.motores_status = "off"
                while camara.buffer < 15:
                    time.sleep(0.5)
                    
                
            if tacho_actual == None:
                print("Los contenedores estan llenos.\nVaciar contenedores.\nFin del programa.")
                mqtt_client.send_metric("metricas/codigo", 0)
                break
        else:
            """stop()"""
            print("El ponton no se encuentra en el catamaran.\nFin del programa.")
            mqtt_client.send_metric("metricas/codigo", 0)
            break
