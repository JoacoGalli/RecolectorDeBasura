import time
import logging

from clases import Motores_rotacion, Motores_traslacion, Maquina_del_mal, Camara
import threading
from mqtt_influx_class import MQTTClient


ORDEN_LLENADO = [3,7,2,6,1,5,0,4]

def elegir_tacho_a_llenar(cont):
    aux = []
    clockwise = None
    sensor = None
    for x in range(len(cont)):
        if cont[str(ORDEN_LLENADO[x])] < 90: # Este 90 tiene que coincidir con el que hace prender los motores en el main
            if ORDEN_LLENADO[x] in [0,1,2,3]:
                clockwise = 0
                sensor = 1
            else:
                clockwise = 1
                sensor = 2
                
            pos = ORDEN_LLENADO [x]
            print(f"{pos=} {clockwise=}  {sensor=}")
            return pos, clockwise, sensor
    

def mover_cinta(maquina, traslacion, pos):       
    if (maquina.posicion_cinta - pos) > 0 :
        traslacion.clockwise = True
        traslacion.motores_status = "on"
        #print(f"{maquina.posicion_media[str(pos)]=}")
        #print(f"{maquina.posicion_cinta_cm}")
        while not ( (maquina.posicion_media[str(pos)] - 1) < maquina.posicion_cinta_cm < (maquina.posicion_media[str(pos)] + 1)) :
            #print(" no salgo del while")
            maquina.ubicacion_cinta()
            #print(f"{maquina.posicion_cinta_cm=}")
            time.sleep(0.2)
        traslacion.motores_status = "off"
    elif (maquina.posicion_cinta - pos) < 0: 
        traslacion.clockwise = False
        traslacion.motores_status = "on"
        while not( maquina.posicion_media[str(pos)] - 2.5 < maquina.posicion_cinta_cm < maquina.posicion_media[str(pos)] + 2.5) :
            maquina.ubicacion_cinta()
            #print(f"{maquina.posicion_cinta_cm=}")
            #print("estoy en el otro while")
            time.sleep(0.2)
        traslacion.motores_status = "off"
    else:
        print("ya estoy aca segui")
    print("llegue al que elegi, ahora lleno")



if __name__ == "__main__":
    # Definimos las 3 clases (3 threads)
    mqtt_client = MQTTClient()
    mqtt_thread = threading.Thread(target=mqtt_client.run_mqtt_client)
    mqtt_thread.start()
    maquina = Maquina_del_mal(mqtt_client)
    motor_rotacion_dist = Motores_rotacion(mqtt_client,tipo="dist")
    motor_rotacion_cap = Motores_rotacion(mqtt_client, tipo="cap")
    traslacion = Motores_traslacion(mqtt_client)
    time.sleep(1)
    motor_rotacion_dist.start()
    motor_rotacion_cap.start()
    traslacion.start()
    camara = Camara()
    time.sleep(1)
    camara.buffer = 80
    #camara.start()
    #maquina.medir_llenado_tachos(maquina.sensor)

    mqtt_client.send_metric("metricas/codigo", 1)
    while(True):
        if maquina.esta_ponton():
            maquina.ubicacion_cinta()
            for posicion in range(4):
                print(f"{posicion=} y {maquina.posicion_cinta}")
                time.sleep(0.8)
                mover_cinta(maquina, traslacion, posicion)
                print("mido los tachos")
                maquina.medir_llenado_tachos(1) #mido el de adelante
                print("paso a medir el 2")
                maquina.medir_llenado_tachos(2) # mido el de atras
            #print("********% contenedores**************")
            #print(f"{maquina.contenedores=}")
            tacho_actual, motor_rotacion_dist.sentido, maquina.sensor = elegir_tacho_a_llenar(maquina.contenedores) # elige un tacho, si estan todos llenos devuelve false, con motores_rotacion ademas elige el sentido de rotacion (ej: 1,2,3,4 entonces izquierda)
            if tacho_actual != False:
                mover_cinta(maquina, traslacion, tacho_actual)
                if camara.buffer > 70:
                    while camara.buffer > 20:
                        print("pase el buffer")
                        print(f"{maquina.contenedores=}")
                        while maquina.contenedores[str(maquina.posicion_cinta)] < 90:  # este 90 tiene que coincidir con el de elegir_tacho_a_llenar()
                            print("prendeme los motores")
                            motor_rotacion_dist.motores_status = "on"
                            time.sleep(0.2)
                            motor_rotacion_cap.motores_status = "on"
                            maquina.medir_llenado_tachos(maquina.sensor)
                            time.sleep(0.5)
                        motor_rotacion_dist.motores_status = "off"
                        motor_rotacion_cap.motores_status = "off"
                        
                        tacho_actual, motor_rotacion_dist.sentido, maquina.sensor = elegir_tacho_a_llenar(maquina.contenedores) # elige un tacho, si estan todos llenos devuelve false, con motores_rotacion ademas elige el sentido de rotacion (ej: 1,2,3,4 entonces izquierda)
                        if tacho_actual != False:  # else WARNING VACIAME LOS TACHOS FRENALO
                            mover_cinta(maquina, traslacion, tacho_actual)
                        else:
                            """stop()"""
                            print("Los tachos estan llenos!!")
                            break
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
