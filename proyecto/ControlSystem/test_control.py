import pytest
from ControlGer import setState, _machine

states = [
        'runTurnedOff', # Apagado
        # 'runTurnedOn', # Prendido
        # 'runRunning', #Operando
        # 'runAwaiting', # En Espera
        # 'runDownloadingContainers', # Descargando Contendores
        # 'runActive', # Activo
        # 'runLoadBuffer', # Cargar Buffer
        # 'runLoadContainer', # Captar y distribuir contenedor
        # 'runChangeContainer', # Cambiar de contendor
        # 'runHalted',  # Detenido
        # 'runAwaitingAccess',  # Esperando Accesso
        # 'runMaintenance',  # Mantenimiento
]

@pytest.mark.parametrize("state", states)
def test_SetState(state):
    
    print(f'{state=}')
    setState(state)
    # print(f'{_machine[state].__name__=}')
    assert _machine[state].__name__ == state

# @pytest.mark.parametrize("test_input,expected", [("3+5", 8), ("2+4", 6), ("6*9", 42)])
# def test_eval(test_input, expected):
#     assert eval(test_input) == expected