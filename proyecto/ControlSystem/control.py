import time
import logging

from clases import Motores_rotacion, Motores_traslacion, Maquina_del_mal, Camara
import threading
from mqtt_influx_class import MQTTClient
import sys

#ORDEN_LLENADO = [3,7,2,6,1,5,0,4]

def elegir_tacho_a_llenar(cont, maquina, traslacion, ORDEN_LLENADO):
    print(f"{ORDEN_LLENADO=}")
    aux = []
    clockwise = None
    sensor = None
    for x in ORDEN_LLENADO:
        print(f"El que deberia llenar es {x=}")
        #maquina.medir_llenado_tachos(2,posicion) # mido el de atras
        #if cont[str(ORDEN_LLENADO[x])] < 70: # Este 90 tiene que coincidir con el que hace prender los motores en el main
        if x in [0,1,2,3]:
                clockwise = 0
                sensor = 1
                mover_cinta(maquina, traslacion, x)
                time.sleep(0.2)
                maquina.medir_llenado_tachos(sensor,x)
                time.sleep(0.5) 
                if cont[str(x)] < 50: # Este 90 tiene que coincidir con el que hace prender los motores en el main
                    pos = x
                    ORDEN_LLENADO.remove(x)
                    print(f"te mando a llenar este: {x}")
                    #print(f"{ORDEN_LLENADO=}")
                    return pos, clockwise, sensor
                print(f"pase por {x} y era mas de 50")
                ORDEN_LLENADO.remove(x)
        else:
                clockwise = 1
                sensor = 2
                mover_cinta(maquina, traslacion, x)
                time.sleep(0.2)
                maquina.medir_llenado_tachos(sensor,x)
                time.sleep(0.5)
                if cont[str(x)] < 50: # Este 90 tiene que coincidir con el que hace prender los motores en el main
                    pos = x
                    ORDEN_LLENADO.remove(x)
                    print(f"te mando a llenar este: {x}")
                    #print(f"{ORDEN_LLENADO=}")
                    return pos, clockwise, sensor
                ORDEN_LLENADO.remove(x)
                print(f"pase por {x} y era mas de 50")
    print("Tacho actual = None, porque estan todos llenos")     
    return None,0,1

def mover_cinta(maquina, traslacion, pos):
    maquina.medir_ubicacion_cinta_inicial() 
    if (maquina.posicion_media[str(pos)]-1.5 < maquina.posicion_cinta_cm < maquina.posicion_media[str(pos)]+1.5):
        print("ya estoy aca")
    else:
        if (maquina.posicion_cinta_cm - maquina.posicion_media[str(pos)]) > 0 :
            traslacion.clockwise = True
            traslacion.motores_status = "on"
        #print(f"{maquina.posicion_media[str(pos)]=}")
        #print(f"{maquina.posicion_cinta_cm}")
            while not ( (maquina.posicion_media[str(pos)] - 1) < maquina.posicion_cinta_cm < (maquina.posicion_media[str(pos)] + 1)) :
                #print(" no salgo del while")
                maquina.ubicacion_cinta(traslacion.clockwise)
                print(f"{maquina.posicion_cinta_cm=}")
                #time.sleep(0.2)
            traslacion.motores_status = "off"
        if (maquina.posicion_cinta_cm - maquina.posicion_media[str(pos)]) <  0 :
            traslacion.clockwise = False
            traslacion.motores_status = "on"
            while not( maquina.posicion_media[str(pos)] - 1 < maquina.posicion_cinta_cm < maquina.posicion_media[str(pos)] + 1) :
                maquina.ubicacion_cinta(traslacion.clockwise)
                print(f"{maquina.posicion_cinta_cm=}")
                #print("estoy en el otro while")
                #time.sleep(0.2)
            traslacion.motores_status = "off"
    print("llegue al que elegi, ahora lleno")



if __name__ == "__main__":
    # Definimos las 3 clases (3 threads)
    mqtt_client = MQTTClient()
    mqtt_thread = threading.Thread(target=mqtt_client.run_mqtt_client)
    mqtt_thread.start()
    camara = Camara(mqtt_client)
    #camara.start()
    maquina = Maquina_del_mal(mqtt_client)
    motor_rotacion_dist = Motores_rotacion(mqtt_client,tipo="dist", camara=camara.buffer)
    motor_rotacion_cap = Motores_rotacion(mqtt_client, tipo="cap", camara=camara.buffer)
    traslacion = Motores_traslacion(mqtt_client)
    time.sleep(1)
    motor_rotacion_dist.start()
    motor_rotacion_cap.start()
    traslacion.start()
    time.sleep(1)
    camara.buffer = 80
    ORDEN_LLENADO = [3,7,2,6,1,5,0,4]

    mqtt_client.send_metric("metricas/codigo", 1)
    while(True):
        if maquina.esta_ponton():
            maquina.medir_ubicacion_cinta_inicial()
            
           # for posicion in [0,1,2,3,7,6,5,4]:
           #     print(f"{posicion=} y {maquina.posicion_cinta}")
           #     mover_cinta(maquina, traslacion, posicion)
           #     if posicion in [0, 1, 2, 3]:    
           #         print("mido con sensor 1")
           #         maquina.medir_llenado_tachos(1,posicion) #mido el de adelante
           #         print(f"{maquina.contenedores=}")
           #     else:
           #         print("paso a medir el 2")
           #         maquina.medir_llenado_tachos(2,posicion) # mido el de atras
           #         print(f"{maquina.contenedores=}")
            #print("********% contenedores**************")
            #print(f"{maquina.contenedores=}")
            tacho_actual, motor_rotacion_dist.sentido, maquina.sensor = elegir_tacho_a_llenar(maquina.contenedores, maquina, traslacion, ORDEN_LLENADO) # elige un tacho, si estan todos llenos devuelve false, con motores_rotacion ademas elige el sentido de rotacion (ej: 1,2,3,4 entonces izquierda)
            #mover_cinta(maquina, traslacion, tacho_actual)
            if camara.buffer > 70:
                while camara.buffer > 20:
                    print("pase el buffer")
                    print(f"{maquina.contenedores=}")
                    time.sleep(1)
                    motor_rotacion_dist.motores_status = "on"
                    motor_rotacion_cap.motores_status = "on"
                    while maquina.contenedores[str(tacho_actual)] < 50:  # este 90 tiene que coincidir con el de elegir_tacho_a_llenar()
                        maquina.medir_llenado_tachos(maquina.sensor,tacho_actual)
                        print(f"{maquina.contenedores=}")
                    motor_rotacion_dist.motores_status = "off"
                    motor_rotacion_cap.motores_status = "off"
                    time.sleep(0.2) 
                    tacho_actual, motor_rotacion_dist.sentido, maquina.sensor = elegir_tacho_a_llenar(maquina.contenedores, maquina, traslacion, ORDEN_LLENADO) # elige un tacho, si estan todos llenos devuelve false, con motores_rotacion ademas elige el sentido de rotacion (ej: 1,2,3,4 entonces izquierda)
                    #if tacho_actual != None:  # else WARNING VACIAME LOS TACHOS FRENALO
                    #    mover_cinta(maquina, traslacion, tacho_actual)
                    #    print(f"{tacho_actual=}")
                    if tacho_actual == None:
                        """stop()"""
                        print("Los tachos estan llenos!!")
                        mqtt_client.send_metric("metricas/codigo", 0)
                else:
                    while camara.buffer < 70:
                        # llamar a camara que saque la foto y cargue el valor del buffer
                        print("sacando fotos")
                        time.sleep(5)
                    
                
            else:
                """stop()"""
                mqtt_client.send_metric("metricas/codigo", 0)
                print("Los tachos estan llenos!!")
        else:
            """stop()"""
            print("No esta el ponton")
            mqtt_client.send_metric("metricas/codigo", 0)
            break

# Medir la bateria y mandarla al dashboard
