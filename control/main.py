import time
import threading
import RPi.GPIO as GPIO

from sistema_monitoreo_sensores import SistemaMonitoreoSensores
from motores import Motores_rotacion, Motores_traslacion
from camara import Camara
from mqtt_influx_class import MQTTClient


def elegir_tacho_a_llenar(cont, sistema_sensores, traslacion, ORDEN_LLENADO):
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
                    
        mover_cinta(sistema_sensores, traslacion, ORDEN_LLENADO[0])
        time.sleep(0.2)
        sistema_sensores.medir_llenado_contenedor(sensor,ORDEN_LLENADO[0])
        time.sleep(0.2) 

        if cont[str(ORDEN_LLENADO[0])] < 70: # Este 90 tiene que coincidir con el que hace prender los motores en el main
            pos = ORDEN_LLENADO[0]
            print(f"te mando a llenar contenedor nro: {ORDEN_LLENADO[0]}")
            print(f"{ORDEN_LLENADO=}")
            ORDEN_LLENADO.remove(ORDEN_LLENADO[0])
            return pos, clockwise, sensor

        print(f"pase por {ORDEN_LLENADO[0]} y era mas de 50")
        ORDEN_LLENADO.remove(ORDEN_LLENADO[0])

    print("Los contenedores estan llenos")     
    return None,0,1

def mover_cinta(sistema_sensores, traslacion, pos):
    if (sistema_sensores.posicion_media[str(pos)]-0.65 < sistema_sensores.posicion_cinta_cm < sistema_sensores.posicion_media[str(pos)]+0.65):
        print("La cinta se encuentra posicionada en el contenedor a llenar.")
    else:
        if (sistema_sensores.posicion_cinta_cm - sistema_sensores.posicion_media[str(pos)]) > 0 :
            traslacion.clockwise = False
            traslacion.motores_status = "on"

        elif (sistema_sensores.posicion_cinta_cm - sistema_sensores.posicion_media[str(pos)]) <  0 :
            traslacion.clockwise = True
            traslacion.motores_status = "on"

        while not( sistema_sensores.posicion_media[str(pos)] - 0.65 < sistema_sensores.posicion_cinta_cm < sistema_sensores.posicion_media[str(pos)] + 0.65) :
            sistema_sensores.ubicacion_cinta(traslacion.clockwise)
        
        traslacion.motores_status = "off"
    print("llegue al que elegi, ahora lleno")



if __name__ == "__main__":
    print("Inicio.")
    # Se inicializan las clases en threads diferentes 
    mqtt_client = MQTTClient()
    mqtt_thread = threading.Thread(target=mqtt_client.run_mqtt_client)
    mqtt_thread.start()
    
    camara = Camara(mqtt_client)
    camara.start()
    
    motor_rotacion_dist = Motores_rotacion(mqtt_client,tipo="dist", camara=camara.buffer)
    motor_rotacion_cap = Motores_rotacion(mqtt_client, tipo="cap", camara=camara.buffer)
    traslacion = Motores_traslacion(mqtt_client)
    time.sleep(1)
    motor_rotacion_dist.start()
    motor_rotacion_cap.start()
    traslacion.start()
    
    sistema_sensores = SistemaMonitoreoSensores(mqtt_client)
    
    ORDEN_LLENADO = [3,7,2,6,1,5,0,4]
    contenedor_actual = 10
    mqtt_client.send_metric("metricas/codigo", 1)
    print("Estado = Activo")
    
    try:
        while(True):
            if sistema_sensores.deteccion_ponton() and contenedor_actual != None:
                sistema_sensores.medir_ubicacion_cinta_inicial()
                contenedor_actual, motor_rotacion_dist.sentido, sistema_sensores.sensor = elegir_tacho_a_llenar(sistema_sensores.contenedores, sistema_sensores, traslacion, ORDEN_LLENADO) # elige un tacho, si estan todos llenos devuelve false, con motores_rotacion ademas elige el sentido de rotacion (ej: 1,2,3,4 entonces izquierda)
                mqtt_client.send_metric("metricas/distribucion_pos_nro_cont", contenedor_actual)

                if camara.buffer > 15 or contenedor_actual != None:
                    # Se enciende el motor de captacion, hasta que se llenen todos los contenedores.
                    motor_rotacion_cap.motores_status = "on"
                    
                    while camara.buffer > 5 and contenedor_actual != None:
                        # Si el contenedor no esta lleno, continuo
                        print("El buffer tiene suficiente basura.\n Se activan los motores")
                        print(f"El % de llenado de los contenedores es: {sistema_sensores.contenedores}")
                        motor_rotacion_dist.motores_status = "on"
                        
                        while sistema_sensores.contenedores[str(contenedor_actual)] < 50:
                            sistema_sensores.medir_llenado_contenedor(sistema_sensores.sensor,contenedor_actual)
                            print(f"El % de llenado de los contenedores es: {sistema_sensores.contenedores}")
                        
                        motor_rotacion_dist.motores_status = "off"
                        time.sleep(0.2)
                        # Se coloca la cinta en el proximo contenedor a llenar.
                        contenedor_actual, motor_rotacion_dist.sentido, sistema_sensores.sensor = elegir_tacho_a_llenar(sistema_sensores.contenedores, sistema_sensores, traslacion, ORDEN_LLENADO) # elige un tacho, si estan todos llenos devuelve false, con motores_rotacion ademas elige el sentido de rotacion (ej: 1,2,3,4 entonces izquierda)
                        mqtt_client.send_metric("metricas/distribucion_pos_nro_cont", contenedor_actual)
                        
                        if contenedor_actual == None:
                            motor_rotacion_cap.motores_status = "off"
                            print("Los contenedores estan llenos.\nVaciar contenedores.\nFin del programa.")
                            mqtt_client.send_metric("metricas/codigo", 0)
                            break
                            
                elif camara.buffer < 5 and contenedor_actual != None:
                    print("Estado = Reposo")
                    print(f"El buffer no tiene suficiente basura {camara.buffer}, continuo sacando fotos y verificando.")
                    motor_rotacion_cap.motores_status = "off"
                    while camara.buffer < 15:
                        time.sleep(0.5)

                elif contenedor_actual == None:
                    print("Los contenedores estan llenos.\nVaciar contenedores.\nFin del programa.")
                    mqtt_client.send_metric("metricas/codigo", 0)
                    break
            else:
                if contenedor_actual == None:
                    print("Los contenedores estan llenos.\nVaciar contenedores.\nFin del programa.")
                    mqtt_client.send_metric("metricas/codigo", 0)
                    break
                else:
                    print("El ponton no se encuentra en el catamaran.\nFin del programa.")
                    mqtt_client.send_metric("metricas/codigo", 0)
                    break
    except KeyboardInterrupt:
        mqtt_client.send_metric("metricas/codigo", 0)
        print("Fin")
