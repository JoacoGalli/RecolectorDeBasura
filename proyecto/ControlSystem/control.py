import time
import threading
import RPi.GPIO as GPIO
from mqtt_influx_class import MQTTClient

from clases import Motores_rotacion, Motores_traslacion, Maquina_del_mal, Camara


def elegir_contenedor_a_llenar(cont, maquina, traslacion, orden_llenado):
    sentido_horario = None
    sensor = None
    for x in orden_llenado:
        # Se setean las variables para la cinta de distribucion con respecto al contenedor a llenar
        if x in [0,1,2,3]:
            sentido_horario = False
            sensor = 1
        elif x in [4,5,6,7]:
            sentido_horario = True
            sensor = 2

        mover_cinta(maquina, traslacion, x)
        time.sleep(0.2)
        maquina.medir_llenado_contenedor(sensor,x)
        time.sleep(0.2) 
        if cont[str(x)] < 50: # el umbral debe coincidir con el que hace prender los motores en el main
            pos = x
            orden_llenado.remove(x)
            print(f"te mando a llenar este: {x}")
            return pos, sentido_horario, sensor
        # El contenedor esta lleno, lo saco de los posibles a llenar
        orden_llenado.remove(x)

    print("Contenedor actual = None, porque estan todos llenos")     
    return None,sentido_horario,sensor

def mover_cinta(maquina, traslacion, pos):
    # ----------------------------------------------
    # Saque el medicion posicion inicial, lo deje por unica vez cuando arranca el main
    # No deberiamos mejorar esto? ponerlo mas bajo que 1.5??
    #----------------------------------------------
    # Puede ya estar ubicada en el lugar donde se le pide.
    if (maquina.posicion_media[str(pos)]-1.5 < maquina.posicion_cinta_cm < maquina.posicion_media[str(pos)]+1.5):
        print(f"Cinta de distribucón en contenedor Nro: {pos}.Comienza el llenado")
    else:
        # Se decide si se mueve la cinta hacia la popa o a la proa
        if (maquina.posicion_cinta_cm - maquina.posicion_media[str(pos)]) > 0 :
            traslacion.sentido_horario = True
            traslacion.estado = "on"
        elif (maquina.posicion_cinta_cm - maquina.posicion_media[str(pos)]) <  0 :
            traslacion.sentido_horario = False
            traslacion.estado = "on"

        # Hasta que no se encuentre en la posicion deseada, se continua moviendo
        while not((maquina.posicion_media[str(pos)] - 1) < maquina.posicion_cinta_cm < (maquina.posicion_media[str(pos)] + 1)) :
            maquina.ubicacion_cinta(traslacion.sentido_horario)
        traslacion.estado = "off"
    print(f"Cinta de distribucón en contenedor Nro: {pos}. Comienza el llenado.")


if __name__ == "__main__":
    # Se inicializan las clases en threads diferentes.
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

    maquina = Maquina_del_mal(mqtt_client)
    time.sleep(1)
    
    orden_llenado = [3,7,2,6,1,5,0,4]

    # Enviar metrica codigo en proceso.
    mqtt_client.send_metric("metricas/codigo", 1)

    try:
        while True:
            # Se verifica que este el ponton.
            if maquina.deteccion_ponton():
                # Se mide la posicion en la que se encuentra la cinta de distribucion por primera vez (None)
                maquina.medir_ubicacion_cinta(None)
                contenedor_actual, motor_rotacion_dist.sentido_horario, maquina.sensor = elegir_contenedor_a_llenar(maquina.contenedores, maquina, traslacion, orden_llenado) 
                # La cinta de distribucion se encuentra en el contenedor a llenar.
                # Se verifica que el buffer tenga basura y los contenedores no esten llenos.
                if camara.buffer > 70 and contenedor_actual != None:
                    # Se enciende el motor de captacion, hasta que se llenen todos los contenedores.
                    motor_rotacion_cap.estado = "on"
                    while camara.buffer > 20 and contenedor_actual != None:
                        motor_rotacion_dist.estado = "on"
                        # Si el contenedor no esta lleno, continuo
                        while maquina.contenedores[str(contenedor_actual)] < 50:  # 50 tiene que coincidir con el de elegir_contenedor_a_llenar()
                            maquina.medir_llenado_contenedor(maquina.sensor,contenedor_actual)
                            print(f"{maquina.contenedores=}")
                        
                        motor_rotacion_dist.estado = "off"
                        time.sleep(0.2)
                        # Se coloca la cinta en el proximo contenedor a llenar. 
                        contenedor_actual, motor_rotacion_dist.sentido_horario, maquina.sensor = elegir_contenedor_a_llenar(maquina.contenedores, maquina, traslacion, orden_llenado) # elige un tacho, si estan todos llenos devuelve false, con motores_rotacion ademas elige el sentido de rotacion (ej: 1,2,3,4 entonces izquierda)
                        if contenedor_actual == None:
                            motor_rotacion_cap.estado = "off"
                            print("Los contenedores estan llenos!!")
                            mqtt_client.send_metric("metricas/codigo", 0)
                    else:
                        # -------------------------------------------------
                        # Esto tiene que ir? para mi si es mayor a 0 sigue.
                        # -------------------------------------------------
                        while camara.buffer < 70:
                            motor_rotacion_cap.estado = "off"
                            # llamar a camara que saque la foto y cargue el valor del buffer
                            print("sacando fotos")
                            time.sleep(60)
                else:
                    motor_rotacion_cap.estado = "off"
                    mqtt_client.send_metric("metricas/codigo", 0)
                    print("Los contenedores estan llenos. Retirar pontón y vaciar contenedores.")
            else:
                """stop()"""
                print("El pontón fue retirado.")
                mqtt_client.send_metric("metricas/codigo", 0)
                motor_rotacion_dist.fin()
                motor_rotacion_cap.fin()
                traslacion.fin()
                camara.fin()
                GPIO.cleanup()
                break

    except KeyboardInterrupt:
        mqtt_client.send_metric("metricas/codigo", 0)
        motor_rotacion_dist.fin()
        motor_rotacion_cap.fin()
        traslacion.fin()
        camara.fin()
        GPIO.cleanup()
