import serial
import time

PUERTO = "COM7" 
BAUDIOS = 115200

try:
    with serial.Serial(PUERTO, BAUDIOS, timeout=1) as ser:
        print("Esperando datos... si ves texto abajo, el Arduino está enviando info.")
        time.sleep(2)
        while True:
            linea = ser.readline().decode('utf-8', errors='ignore').strip()
            if linea:
                print(f"RECIBIDO: {linea}")
except Exception as e:
    print(f"Error: {e}")