# Este script sustituye por completo a tu antiguo script de lectura Serial. Ahora se conecta al Mosquitto de 
# Docker, abre un hilo de escucha durante los segundos que le pidas (DURACION_S), procesa los JSON entrantes 
# y los guarda en un archivo .csv idéntico al que tenías.

import json
import csv
import time
import os
from datetime import datetime
import paho.mqtt.client as mqtt

# --- AJUSTES ---
MQTT_HOST = "localhost" # Al estar en el mismo PC que Docker, usamos localhost
MQTT_PORT = 1883
TOPIC = "sensores/datos"
DURACION_S = 20  
SUJETO = "javi"

# Crear carpeta de datos
if not os.path.exists("datos"):
    os.makedirs("datos")

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
archivo_csv = f"datos/captura_{SUJETO}_{ts}.csv"
campos = ["t_ms", "ax", "ay", "az", "L_env", "L_raw", "R_env", "R_raw"]

muestras_guardadas = 0
f = None
writer = None

# --- CALLBACKS DE MQTT ---
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Conectado exitosamente al Broker Mosquitto (Docker)")
        client.subscribe(TOPIC)
        print(f"📡 Escuchando el tópico '{TOPIC}'...")
        print(f"🔴 GRABANDO {DURACION_S} SEGUNDOS EN: {archivo_csv}")
    else:
        print(f"❌ Error de conexión al broker. Código: {rc}")

def on_message(client, userdata, msg):
    global muestras_guardadas, writer, f
    try:
        # Decodificar el mensaje JSON que viene del Wi-Fi
        linea = msg.payload.decode('utf-8')
        d = json.loads(linea)
        
        if "L_env" in d:
            fila = {
                "t_ms": d.get("t"), 
                "ax": d.get("ax"), "ay": d.get("ay"), "az": d.get("az"),
                "L_env": d.get("L_env"), "L_raw": d.get("L_raw"),
                "R_env": d.get("R_env"), "R_raw": d.get("R_raw")
            }
            writer.writerow(fila)
            muestras_guardadas += 1
            
            # Cada 50 muestras, forzamos la escritura física en el disco
            if muestras_guardadas % 50 == 0:
                f.flush()
                print(f"📦 Muestras capturadas vía Wi-Fi: {muestras_guardadas}", end="\r")

    except json.JSONDecodeError:
        pass # Ignorar mensajes corruptos o incompletos
    except Exception as e:
        print(f"\n⚠️ Error procesando mensaje: {e}")

# --- EJECUCIÓN PRINCIPAL ---
try:
    # Preparar el archivo CSV antes de conectar
    f = open(archivo_csv, "w", newline="")
    writer = csv.DictWriter(f, fieldnames=campos)
    writer.writeheader()

    # Configurar cliente MQTT
    cliente = mqtt.Client()
    cliente.on_connect = on_connect
    cliente.on_message = on_message

    # Conectar al broker local (Docker)
    cliente.connect(MQTT_HOST, MQTT_PORT, 60)

    # Iniciar la escucha en un hilo secundario de fondo
    cliente.loop_start()

    # Mantener el script vivo durante el tiempo de grabación
    t_inicio = time.time()
    while time.time() - t_inicio < DURACION_S:
        time.sleep(0.1)

    # Detener la captura ordenadamente
    cliente.loop_stop()
    cliente.disconnect()
    f.flush()
    f.close()

    print("\n" + "="*40)
    print(f"✅ Finalizado. Se han guardado {muestras_guardadas} muestras inalámbricas.")
    print(f"📂 Archivo guardado en:\n {os.path.abspath(archivo_csv)}")
    print("="*40)

except KeyboardInterrupt:
    print("\n🛑 Grabación interrumpida por el usuario.")
    if f:
        f.close()