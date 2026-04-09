import serial, json, csv, time, os
from datetime import datetime

# --- AJUSTES ---
PUERTO = "COM7"  # <--- Cambiad esto por vuestro puerto (ej: COM3, COM8...)
BAUDIOS = 115200
DURACION_S = 10  # Tiempo que grabará cada vez
SUJETO = "Prueba"

# Crear carpeta de datos si no existe
if not os.path.exists("datos"):
    os.makedirs("datos")

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
archivo_csv = f"datos/captura_{SUJETO}_{ts}.csv"
campos = ["t_ms", "ax", "ay", "az", "emg_env", "emg_raw"]

print(f"📡 Conectando al Arduino en {PUERTO}...")

try:
    with serial.Serial(PUERTO, BAUDIOS, timeout=2) as ser:
        time.sleep(2) # Esperar conexión
        ser.reset_input_buffer()
        
        print(f"🔴 GRABANDO {DURACION_S} SEGUNDOS EN: {archivo_csv}")
        muestras = []
        t_inicio = time.time()
        
        with open(archivo_csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            
            while time.time() - t_inicio < DURACION_S:
                linea = ser.readline().decode('utf-8').strip()
                if not linea: continue
                
                try:
                    d = json.loads(linea)
                    # Mapear datos del JSON a las columnas del CSV
                    fila = {
                        "t_ms": d["t"], 
                        "ax": d["ax"], "ay": d["ay"], "az": d["az"],
                        "emg_env": d["env"], "emg_raw": d["raw"]
                    }
                    writer.writerow(fila)
                    muestras.append(fila)
                except:
                    continue

        print(f"✅ Finalizado. Se han guardado {len(muestras)} muestras.")
        print(f"📂 Podéis abrir el archivo en Excel para ver las gráficas.")

except Exception as e:
    print(f"❌ ERROR: {e}")
    print("Asegúrate de que Thonny esté cerrado y el puerto COM sea el correcto.")