import threading
import time

from sensores import medir_si_esta_ponton, medir_ubicacion_cinta, mover_cinta_traslacion, medir_buffer, activar_motores_rotacion, reset_motores_rotacion

class Maquina_del_mal():
    def __init__(self):
        self.ponton = False
        self.cant_tachos = 8
        self.contenedores = {"1":0,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0,"8":0}
        self.buffer = None
        self.motor_rotacion = False # True=On False=Off
        self.motor_traslacion = False
        self.posicion_cinta = None # 1 2 3 4 

    def esta_ponton(self):
        self.ponton = medir_si_esta_ponton()
        return self.ponton
    
    def ubicacion_cinta(self): # existen cuatro ubicaciones
        self.posicion_cinta = medir_ubicacion_cinta()
        return self.posicion_cinta

    def trasladar_cinta(self, nueva_posicion):
        self.motor_traslacion = True
        if mover_cinta_traslacion(nueva_posicion):
            self.motor_traslacion = False

    def medir_llenado_tachos(self):
        self.contenedores[str(self.posicion_cinta)], self.contenedores[str(self.posicion_cinta + 4)] = medir_llenado()

    def porcentaje_buffer(self):
        self.buffer = medir_buffer()
        return self.buffer


class Motores_rotacion(threading.Thread): # posdemos usar 1 solo thread??
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.motores_status = 'off' # on, off, reset
        self.sentido = None # "right" "left"
    
    def run(self):
        while(True):
            if self.motores_status == 'on':
                activar_motores_rotacion(self.sentido)
            if self.motores_status == 'reset':
                reset_motores_rotacion()
                self.motores_status = 'off'

class Camara(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.buffer = None
    
    def run(self):
        while(True):
            self.buffer = medir_buffer()
            time.sleep(60) #60 segundos?
