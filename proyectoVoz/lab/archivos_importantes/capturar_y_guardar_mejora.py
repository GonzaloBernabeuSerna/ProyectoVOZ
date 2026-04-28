import serial
import json
import csv
import time
import os
from datetime import datetime

# --- AJUSTES ---
PUERTO = "COM7"  # <--- Cambia esto según tu administrador de dispositivos
BAUDIOS = 115200
DURACION_S = 20  
SUJETO = "javi"

# Crear carpeta de datos
if not os.path.exists("datos"):
    os.makedirs("datos")

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
archivo_csv = f"../datos/captura_{SUJETO}_{ts}.csv"
campos = ["t_ms", "ax", "ay", "az", "L_env", "L_raw", "R_env", "R_raw"]

print(f"📡 Conectando al Arduino en {PUERTO}...")

try:
    # Usamos un timeout corto para no bloquear el bucle
    with serial.Serial(PUERTO, BAUDIOS, timeout=0.1) as ser:
        print("⏳ Esperando a que el sensor se estabilice...")
        time.sleep(2) 
        ser.reset_input_buffer() # Limpiar datos viejos
        
        print(f"🔴 GRABANDO {DURACION_S} SEGUNDOS EN: {archivo_csv}")
        muestras_guardadas = 0
        t_inicio = time.time()
        
        with open(archivo_csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            
            while time.time() - t_inicio < DURACION_S:
                try:
                    # 'errors=ignore' evita que el script muera por ruido en el cable
                    linea = ser.readline().decode('utf-8', errors='ignore').strip()
                    
                    if not linea or not linea.startswith('{'): 
                        continue
                    
                    d = json.loads(linea)
                    
                    # Verificamos que sea un paquete de datos y no de status
                    if "L_env" in d:
                        fila = {
                            "t_ms": d.get("t"), 
                            "ax": d.get("ax"), "ay": d.get("ay"), "az": d.get("az"),
                            "L_env": d.get("L_env"), "L_raw": d.get("L_raw"),
                            "R_env": d.get("R_env"), "R_raw": d.get("R_raw")
                        }
                        writer.writerow(fila)
                        muestras_guardadas += 1
                        
                        # Cada 50 muestras, forzamos la escritura en disco y avisamos
                        if muestras_guardadas % 50 == 0:
                            f.flush()
                            print(f"📦 Muestras capturadas: {muestras_guardadas}", end="\r")

                except json.JSONDecodeError:
                    continue # Ignorar líneas incompletas
                except Exception as e:
                    print(f"\n⚠️ Error en lectura: {e}")

        print("\n" + "="*40)
        print(f"✅ Finalizado. Se han guardado {muestras_guardadas} muestras.")
        print(f"📂 Archivo guardado en:\n {os.path.abspath(archivo_csv)}")
        print("="*40)

except serial.SerialException as e:
    print(f"❌ ERROR DE CONEXIÓN: {e}")
    print("Asegúrate de que el Arduino esté conectado y Thonny (u otro programa) no esté usando el puerto.")
except KeyboardInterrupt:
    print("\n🛑 Grabación interrumpida por el usuario.")