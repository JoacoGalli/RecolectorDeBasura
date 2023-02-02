import time
from logging import info
import logging
from clases import Motores_rotacion, Maquina_del_mal, Camara

# _STATE = "Turned Off"

# def setState(newState):
#     global _STATE
#     _STATE = newState

def runTurnedOff():
    pass

def runTurnedOn():
    # iniciar alertas
    # inciar variables
    # inciar interrupciones
    pass

def runRunning():
    pass

def runAwaiting():
    pass

def runDownloadingContainers():
    pass

def runActive():
    pass

def runLoadBuffer():
    pass

def runLoadContainer():
    pass

def runChangeContainer():
    pass

def runHalted():
    pass

def runAwaitingAccess():
    pass

def runMaintenance():
    pass

def main():
    logging.getLogger().setLevel(logging.INFO)
    maquina = Maquina_del_mal()
    motores_rotacion = Motores_rotacion()
    camara = Camara()

    while(True):
        # info(f"Currente state: <{_STATE}>")
        # _MACHINE[_STATE]()
        if maquina.esta_ponton():

            for i in range(4):
                maquina.trasladar_cinta(i)
                ubicacion_cinta = maquina.ubicacion_cinta()
                maquina.medir_llenado_tachos()
            tacho_actual = elegir_tacho_a_llenar(maquina.contenedores, motores_rotacion) # elige un tacho, si estan todos llenos devuelve false, con motores_rotacion ademas elige el sentido de rotacion (ej: 1,2,3,4 entonces izquierda)
            if tacho_actual != False: 
                if camara.buffer > 70:
                    motores_rotacion.motor_status = 'on' # el thread de los motores de rotacion arranca
                    while camara.buffer > 20 or maquina.contenedores[maquina.posicion_cinta] < 90 or maquina.contenedores[maquina.posicion_cinta + 4] < 90:
                        time.sleep(2) # este tiempo se va a cambiar dependiendo el tiempo que tarde en llenarse
                        maquina.medir_llenado_tachos()
                        tiempo_inicial = time.time()
                        tf = 0 # este tf esta por si pasa mas de cierto tiempo y el buffer se vacio. se deberia medir el tiempo total que tarde en llenarse un tacho
                        while tacho.llenado < 80 or tf > 30:
                            tacho.llenado = sensar_tacho()
                            tf = time.time() - tiempo_inicial

                        elegir_patron_llenado() #elige a cual tacho moverme y me muevo, leyendo el porcentaje actual de cada uno de los tachos (que me lo devolvio el medir llenado de los tachos)
                        # decidir si se mide la inclinacion tambien o no (podria estar adentro de elegir_patron_llenado())
                        camara_actual = medicion_camara()
        else:
            continue

        #time.sleep(2)

if __name__ == "__main__":

    main()


# Medir la bateria y mandarla al dashboard