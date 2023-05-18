import time
import logging

from clases import Motores_rotacion, Motores_traslacion, Maquina_del_mal, Camara
#from sensores import configurar_sensores

def elegir_tacho_a_llenar(contenedores: dict) -> int or False :
    print("Elijo que tacho quiero llenar")
    aux = []
    clockwise = None
    for contenedor in range(len(contenedores)):
        aux.append(contenedores[str(contenedor)])

    posible_opcion =aux.index(min(aux))
    if posible_opcion <= 4:
        clockwise = True
    else:
        clockwise = False

    if contenedores[str(posible_opcion)] > 95:
        posible_opcion = False

    return posible_opcion, clockwise

def mover_cinta(maquina, traslacion, pos):       
    if (maquina.posicion_cinta - pos) > 0 :
        traslacion.clockwise = False
        traslacion.motores_status = "on"
        print(f"{maquina.posicion_media[str(pos)]=}")
        print(f"{maquina.posicion_cinta_cm}")
        while not ( (maquina.posicion_media[str(pos)] - 1) < maquina.posicion_cinta_cm < (maquina.posicion_media[str(pos)] + 1)) :
            #print(" no salgo del while")
            maquina.ubicacion_cinta()
            time.sleep(0.2)
        traslacion.motores_status = "off"
    elif (maquina.posicion_cinta - pos) < 0: 
        traslacion.clockwise = True
        traslacion.motores_status = "on"
        while not( maquina.posicion_media[str(pos)] - 1 < maquina.posicion_cinta_cm < maquina.posicion_media[str(pos)] + 1) :
            maquina.ubicacion_cinta()
            time.sleep(0.2)
        traslacion.motores_status = "off"
    else:
        print("ya estoy aca segui")
    print("llegue al que elegi, ahora lleno")



if __name__ == "__main__":
    # Definimos las 3 clases (3 threads)
    maquina = Maquina_del_mal()
    motores_rotacion = Motores_rotacion()
    traslacion = Motores_traslacion()
    time.sleep(1)
    motores_rotacion.start()
    traslacion.start()
    camara = Camara()
    camara.start()

    while(True):
        if maquina.esta_ponton():
            maquina.ubicacion_cinta()
            for posicion in range(4):
                print(f"{posicion=} y {maquina.posicion_cinta}")
                time.sleep(0.8)
                mover_cinta(maquina, traslacion, posicion)
                print("mido los tachos")
                maquina.medir_llenado_tachos(1) #mido el de adelante
                #maquina.medir_llenado_tachos(2) # mido el de atras
            print("********% contenedores**************")
            print(f"{maquina.contenedores=}")
            tacho_actual, motores_rotacion.sentido = elegir_tacho_a_llenar(maquina.contenedores) # elige un tacho, si estan todos llenos devuelve false, con motores_rotacion ademas elige el sentido de rotacion (ej: 1,2,3,4 entonces izquierda)
            if tacho_actual != False:
                mover_cinta(maquina, traslacion, tacho_actual)
                if camara.buffer > 70:
                    while camara.buffer > 20:
                        while maquina.contenedores[str(maquina.posicion_cinta)] < 60:
                            motores_rotacion.motores_status = "on"
                            maquina.medir_llenado_tachos(1)
                            time.sleep(0.5)
                        motores_rotacion.motores_status = "off"
                        
                        tacho_actual, motores_rotacion.sentido = elegir_tacho_a_llenar(maquina.contenedores) # elige un tacho, si estan todos llenos devuelve false, con motores_rotacion ademas elige el sentido de rotacion (ej: 1,2,3,4 entonces izquierda)
                        if tacho_actual != False:  # else WARNING VACIAME LOS TACHOS FRENALO
                            mover_cinta(maquina, traslacion, tacho_actual)
                            #while maquina.posicion_cinta != tacho_actual or maquina.posicion_cinta != tacho_actual + 4:
                            #    time.sleep(2)
                            #    maquina.ubicacion_cinta()
                        else:
                            """stop()"""
                            print("Los tachos estan llenos!!")
                            break
                else:
                    while camara.buffer < 70:
                        print("sacando fotos")
                        time.sleep(5)
                    
                
            else:
                """stop()"""
                print("Los tachos estan llenos!!")
        else:
            """stop()"""
            print("No esta el ponton")
            break

# Medir la bateria y mandarla al dashboard
