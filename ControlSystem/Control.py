from abc import ABC, abstractmethod
from logging import info
import time


# Machine with state-dependent code
# ---------------------------------

class StateMachine:

    _state = None

    def __init__(self, state):
        self.transitionTo(state)

    def transitionTo(self, state):
        print(f"[info] Pasando de {type(self._state).__name__} a {type(state).__name__}.")
        self._state = state
        self._state.machine = self

    def do(self):
        self._state.do()

    def measure(self):
        self._state.measure()


# Interface to connect states and machine
# ---------------------------------------

class State(ABC):

    datos = 'ger'

    @property
    def machine(self):
        return self._machine

    @machine.setter
    def machine(self, machine):
        self._machine = machine

    @abstractmethod
    def do(self):
        pass

    @abstractmethod
    def measure(self):
        pass


# Concrete states
# ---------------

class StateTurnedOff(State): # APAGADO.
    def measure(self):
        pass

    def do(self):
        print("[APAGADO] alimentacion ok.")
        self.machine.transitionTo(StateTurnedOn())

class StateTurnedOn(State): # PRENDIDO.
    def measure(self):
        pass

    def do(self):
        print("[PRENDIDO] verificaciones correctas")
        self.machine.transitionTo(StateRunning())

class StateRunning(State): # OPERANDO.
    def measure(self):
        pass

    def do(self):
        print("[OPERANDO] listo para operar.")
        self.machine.transitionTo(StateActive())
        pass

class StateAwaiting(State): # EN ESPERA (OPERANDO).
    def measure(self):
        pass

    def do(self):
        pass

class StateUnloadingPonton(State): # DESCARGANDO PONTON (OPERANDO).
    def measure(self):
        pass

    def do(self):
        pass

class StateActive(State): # ACTIVO (OPERANDO).
    def measure(self):
        pass

    def do(self):
        print("[ACTIVO] controlando .. .. ..")
        pass

class StateHalted(State): # DETENIDO.
    def measure(self):
        pass

    def do(self):
        pass

class StateAwaitingAccess(State): # ESPERANDO ACCESO (DETENIDO).
    def measure(self):
        pass

    def do(self):
        pass

class StateMaintainace(State): # MAINTAINANCE (DETENIDO).
    def measure(self):
        pass

    def do(self):
        pass


# Actual main
#------------

def main():
    app = StateMachine(StateTurnedOff())
    while(True):
        app.measure()
        app.do()
        time.sleep(2)



if __name__ == "__main__":
    main()

#TODO: use logging info!