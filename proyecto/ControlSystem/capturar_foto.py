import cv2
import sys

def capturar_foto(nombre_archivo):
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(nombre_archivo, frame)
        print("Foto capturada y guardada como:", nombre_archivo)
    else:
        print("No se pudo capturar la foto.")
    cap.release()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python capturar_foto.py <nombre_archivo>")
        sys.exit(1)

    nombre_archivo = sys.argv[1]
    capturar_foto(nombre_archivo)
