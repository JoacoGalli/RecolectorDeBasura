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
        time.sleep(2)

if __name__ == "__main__":
    main()