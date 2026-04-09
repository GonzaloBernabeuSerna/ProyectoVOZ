# lab01/leer_adc.py — Leer datos JSON del Arduino en tiempo real
import serial, json, time

PUERTO = "COM7"
BAUDIOS = 115200
N_MUESTRAS = 50   # leer 50 muestras y parar

muestras = []

with serial.Serial(PUERTO, BAUDIOS, timeout=3) as ser:
    print(f"Leyendo {N_MUESTRAS} muestras del Arduino...\n")
    ser.reset_input_buffer()
    
    for i in range(N_MUESTRAS):
        linea = ser.readline().decode('utf-8').strip()
        try:
            dato = json.loads(linea)
            muestras.append(dato)
            print(f"  [{i+1:3d}] t={dato['t_ms']:6d}ms  raw={dato['raw']:5d}  v={dato['v']:.3f}V")
        except:
            print(f"  ⚠️  Línea no JSON: {linea[:40]}")

print(f"\n✓ {len(muestras)} muestras recibidas.")