import time
import logging

from clases import Motores_rotacion, Maquina_del_mal, Camara
from sensores import configurar_sensores

def elegir_tacho_a_llenar(contenedores: dict) -> int or False :
    aux = []
    for contenedor in range(len(contenedores)):
        aux.append(contenedores[str(contenedor + 1)])

    posible_opcion =aux.index(min(aux)) + 1 
    if posible_opcion <= 4:
        sentido = "izquierda"
    else:
        sentido = "derecha"

    if contenedores[str(posible_opcion)] > 95:
        posible_opcion = False

    return posible_opcion, sentido



        #time.sleep(2)

if __name__ == "__main__":
    configurar_sensores()
    logger = logging.get_logger()
    # Definimos las 3 clases (3 threads)
    maquina = Maquina_del_mal()
    motores_rotacion = Motores_rotacion()
    camara = Camara()
    posiciones_cinta = 4
    max_tiempo = 10
    while(True):
        if maquina.esta_ponton():
            for posicion in range(posiciones_cinta):
                maquina.trasladar_cinta(posicion)
                ubicacion_cinta = maquina.ubicacion_cinta()
                maquina.medir_llenado_tachos()

            tacho_actual, motores_rotacion.sentido = elegir_tacho_a_llenar(maquina.contenedores) # elige un tacho, si estan todos llenos devuelve false, con motores_rotacion ademas elige el sentido de rotacion (ej: 1,2,3,4 entonces izquierda)
            if tacho_actual != False:  # else WARNING VACIAME LOS TACHOS FRENALO
                maquina.trasladar_cinta(tacho_actual) #ojo puedo mover y medir a la vez o tengo que hacer otro thred??
                time.sleep(max_tiempo) # mover de la pos 1 a la 4
                while maquina.posicion_cinta != tacho_actual or maquina.posicion_cinta != tacho_actual + 4:
                    time.sleep(2)
                    maquina.ubicacion_cinta()

                if camara.buffer > 70:
                    while camara.buffer > 20:
                        motores_rotacion.motor_status = 'on' # el thread de los motores de rotacion arranca 
                        while maquina.contenedores[tacho_actual] < 90:
                            time.sleep(2) # este tiempo se va a cambiar dependiendo el tiempo que tarde en llenarse
                            maquina.medir_llenado_tachos()
                        
                        motores_rotacion.motor_status = 'reset'
                        tacho_actual, motores_rotacion.sentido = elegir_tacho_a_llenar(maquina.contenedores) # elige un tacho, si estan todos llenos devuelve false, con motores_rotacion ademas elige el sentido de rotacion (ej: 1,2,3,4 entonces izquierda)
                        if tacho_actual != False:  # else WARNING VACIAME LOS TACHOS FRENALO
                            maquina.trasladar_cinta(tacho_actual) #ojo puedo mover y medir a la vez o tengo que hacer otro thred??
                            while maquina.posicion_cinta != tacho_actual or maquina.posicion_cinta != tacho_actual + 4:
                                time.sleep(2)
                                maquina.ubicacion_cinta()
                        else:
                            """stop()"""
                            logger.warning("Los tachos estan llenos!!")
            else:
                """stop()"""
                logger.warning("Los tachos estan llenos!!")
        else:
            """stop()"""
            logger.warning("No esta el ponton")
            time.sleep(30)


# Medir la bateria y mandarla al dashboard