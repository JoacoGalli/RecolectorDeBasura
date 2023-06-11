import time
import logging

from clases import Motores_rotacion_cap, Motores_rotacion_dist, Motores_traslacion, Maquina_del_mal, Camara
#from sensores import configurar_sensores

def elegir_tacho(contenedores: dict) -> int or False :
    print("Elijo que tacho quiero llenar")
    aux = []
    clockwise = None
    for contenedor in range(len(contenedores)):
        aux.append(contenedores[str(contenedor)])
    #print("f{aux=}")
    posible_opcion =aux.index(min(aux))
    if posible_opcion <= 4:
        clockwise = 0
        sensor = 1 #cercano al sensor distancia
    else:
        clockwise = 1
        sensor = 2 # cercano al sensor captacion
    if contenedores[str(posible_opcion)] > 95:
        posible_opcion = False

    return posible_opcion, clockwise, sensor

ORDEN_LLENADO = [3,7,2,6,1,5,0,4]
def elegir_tacho_a_llenar(cont):
    aux = []
    clockwise = None
    sensor = None
    for x in range(len(cont)):
        if cont[str(ORDEN_LLENADO[x])] < 90:
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
    maquina = Maquina_del_mal()
    motor_rotacion_dist = Motores_rotacion_dist()
    motor_rotacion_cap = Motores_rotacion_cap()
    traslacion = Motores_traslacion()
    motor_rotacion_dist.start()
    motor_rotacion_cap.start()
    traslacion.start()
    camara = Camara()
    time.sleep(1)
    camara.buffer = 80
    #camara.start()
    #maquina.medir_llenado_tachos(maquina.sensor)

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
                        while maquina.contenedores[str(maquina.posicion_cinta)] < 60:
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
                print("Los tachos estan llenos!!")
        else:
            """stop()"""
            print("No esta el ponton")
            break

# Medir la bateria y mandarla al dashboard
