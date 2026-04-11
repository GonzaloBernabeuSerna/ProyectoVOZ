import serial, json, csv, time, os
from datetime import datetime

# --- AJUSTES ---
PUERTO = "COM7"  # <--- Aseguraos de que es el puerto correcto
BAUDIOS = 115200
DURACION_S = 10  # Tiempo que grabará cada vez
SUJETO = "david"

# Crear carpeta de datos si no existe (se crea en la misma carpeta donde ejecutes el script)
if not os.path.exists("datos"):
    os.makedirs("datos")

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
archivo_csv = f"datos/captura_{SUJETO}_{ts}.csv"

# 1. ACTUALIZAMOS LAS COLUMNAS AL MODO DUAL
campos = ["t_ms", "ax", "ay", "az", "L_env", "L_raw", "R_env", "R_raw"]

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
                    
                    # Ignorar los mensajes de estado (como el status: ready)
                    if "L_env" not in d: 
                        continue
                        
                    # 2. MAPEAR LOS DATOS DE LOS DOS CANALES
                    fila = {
                        "t_ms": d["t"], 
                        "ax": d["ax"], "ay": d["ay"], "az": d["az"],
                        "L_env": d["L_env"], "L_raw": d["L_raw"],
                        "R_env": d["R_env"], "R_raw": d["R_raw"]
                    }
                    writer.writerow(fila)
                    muestras.append(fila)
                    
                except json.JSONDecodeError:
                    pass # Ignorar líneas que lleguen cortadas
                except KeyError as e:
                    # Ahora si falta un dato, os avisará por pantalla
                    print(f"⚠️ Error de formato JSON: Falta la clave {e}")

        print("\n" + "="*40)
        print(f"✅ Finalizado. Se han guardado {len(muestras)} muestras.")
        # Usamos os.path.abspath para deciros exactamente dónde está el archivo en vuestro PC
        print(f"📂 Archivo guardado en:\n {os.path.abspath(archivo_csv)}")
        print("="*40)

except Exception as e:
    print(f"❌ ERROR: {e}")
    print("Asegúrate de que Thonny esté CERRADO y el puerto COM sea el correcto.")