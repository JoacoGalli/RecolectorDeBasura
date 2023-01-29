import time
from logging import info
import logging
import threading

# ==================== #
# FINITE STATE MACHINE #
# ==================== #

def setState(newState):
    global _state
    previousState = _state
    info(f"[MAIN]: se cambio de estado, de {previousState} a {newState}.")
    _state = newState
    _machine[_state]()

def runTurnedOff():
    while True:
        info("Sistema apagado.")
        setState("Turned On")

def runTurnedOn():
    global READ_SENSORS
    while True:
        # Iniciar variables, alertar e interrupciones.
        info("Iniciando variables.")
        time.sleep(5)
        info("El sistema se ha prendido exitosamente.")
        READ_SENSORS = True
        setState("Running")

def runRunning():
    info("Estoy en Running aguardando.")
    time.sleep(1)
    while True:
        setState("Awaiting")

def runAwaiting():
    info("Estoy en Awainting, en un loop infinito.")
    while True:
        pass

def runDownloadingContainers():
    while True:
        pass

def runActive():
    while True:
        pass

def runLoadBuffer():
    while True:
        pass

def runLoadContainer():
    while True:
        pass

def runChangeContainer():
    while True:
        pass

def runHalted():
    while True:
        pass

def runAwaitingAccess():
    while True:
        pass

def runMaintenance():
    while True:
        pass

_state = "Turned Off"

_machine = {
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

# ======= #
# Threads #
# ======= #

READ_BUFFER = False
READ_SENSORS = False
ROTATE_CATCH = False
ROTATE_DISTRIB = False
MOVE_DISTRIB = False


def readBuffer():
    while True:
        if READ_BUFFER == True:
            info("[BUFFER] buffer activado.")
        time.sleep(60) # mido una vez cada 60 segundos?

def readSensors():
    while True:
        if READ_SENSORS is True:
            info("[SENSORES] se leyeron todos.")
        time.sleep(10) # mido una vez cada 10 segundos?

def rotateCatch():
    while True:
        if ROTATE_CATCH is True:
            info("[ROTATE CATCH] cinta de captacion rotando.")

def rotateDistrib():
    while True:
        if ROTATE_DISTRIB is True:
            info("[ROTATE DISTRIB] cinta de distribucion rotando.")

def moveDistrib():
    while True:
        if MOVE_DISTRIB is True:
            info("[MOVE DISTRIB] cinta de distribucion moviendose.")

def main():
    _machine[_state]()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    t1 = threading.Thread(target=main)
    t2 = threading.Thread(target=readBuffer)
    t3 = threading.Thread(target=readSensors)
    t4 = threading.Thread(target=rotateCatch)
    t5 = threading.Thread(target=rotateDistrib)
    t6 = threading.Thread(target=moveDistrib)

    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    t6.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()
    t6.join()