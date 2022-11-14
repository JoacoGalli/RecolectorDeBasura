import time
from logging import info
import logging

_STATE = "Turned Off"

def setState(newState):
    global _STATE
    _STATE = newState

def runTurnedOff():
    setState("Turned On")

def runTurnedOn():
    # iniciar alertas
    # inciar variables
    # inciar interrupciones
    setState("Running")
    pass

def runRunning():
    setState("Active")
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

_MACHINE = {
        "Turned Off": runTurnedOff, # Apagado
        "Turned On": runTurnedOn, # Prendido
        "Running": runRunning, #Operando
        "Awaiting": runAwaiting, # En Espera
        "DownloadingContainers": runDownloadingContainers, # Descargando Contendores
        "Active": runActive, # Activo
        "LoadBuffer": runLoadBuffer, # Cargar Buffer
        "LoadContainer": runLoadContainer, # Captar y distribuir contenedor
        "ChangeContainer": runChangeContainer, # Cambiar de contendor
        "Halted": runHalted,  # Detenido
        "AwaitingAccess": runAwaitingAccess,  # Esperando Accesso
        "Maintenance": runMaintenance,  # Mantenimiento
    }

def main():
    logging.getLogger().setLevel(logging.INFO)

    while(True):
        info(f"Currente state: <{_STATE}>")
        _MACHINE[_STATE]()
        sensar_si_esta_contenedor()
        if esta_contenedor:
            lleno = medir_llenado_tachos() # lleno puede ser una variable booleana global que me indique si TODOS los tachos estan llenos
            tacho_actual = elegir_tacho_a_llenar() # esta activa cual es el tacho actual, por ej = tacho_actual = 3
            if lleno == False:
                camara_inicio = medicion_camara()
                if camara_inicio > 90:
                    activar_motores(rotacion=True)
                    camara_actual = camara_inicio
                    while camara_actual > 20 or lleno == False:
                        time.sleep(2) # este tiempo se va a cambiar dependiendo el tiempo que tarde en llenarse
                        tacho.llenado = sensar_tacho(tacho.posicion)
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