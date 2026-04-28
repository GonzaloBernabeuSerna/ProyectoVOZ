import serial
import json
import csv
import time
import os
from datetime import datetime

# --- AJUSTES ---
PUERTO = "COM7" 
BAUDIOS = 115200
DURACION_S = 20  
SUJETO = "tomas"

if not os.path.exists("datos"):
    os.makedirs("datos")

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
archivo_csv = f"../datos/captura_single_{SUJETO}_{ts}.csv"

# Columnas finales
campos = ["t_ms", "ax", "ay", "az", "emg_env", "emg_raw"]

print(f"📡 Conectando al Arduino en {PUERTO}...")

try:
    with serial.Serial(PUERTO, BAUDIOS, timeout=1) as ser:
        time.sleep(2) 
        ser.reset_input_buffer()
        
        print(f"🔴 GRABANDO {DURACION_S} SEGUNDOS...")
        muestras = 0
        t_inicio = time.time()
        
        with open(archivo_csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            
            while time.time() - t_inicio < DURACION_S:
                linea = ser.readline().decode('utf-8', errors='ignore').strip()
                if not linea or not linea.startswith('{'): continue
                
                try:
                    d = json.loads(linea)
                    
                    # Verificamos que el JSON tenga las claves correctas (env y raw)
                    if "env" in d:
                        writer.writerow({
                            "t_ms": d["t"], 
                            "ax": d["ax"], 
                            "ay": d["ay"], 
                            "az": d["az"],
                            "emg_env": d["env"], 
                            "emg_raw": d["raw"]
                        })
                        muestras += 1
                        if muestras % 50 == 0:
                            print(f"📦 Muestras: {muestras}", end="\r")
                            f.flush() # Asegura que se guarde en disco
                            
                except Exception as e:
                    continue

        print(f"\n\n✅ ¡ÉXITO! {muestras} muestras guardadas en:\n{os.path.abspath(archivo_csv)}")

except Exception as e:
    print(f"❌ Error: {e}")