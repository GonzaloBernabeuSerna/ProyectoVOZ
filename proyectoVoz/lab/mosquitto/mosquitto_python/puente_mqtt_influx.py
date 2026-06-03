import json
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS

# --- AJUSTES MQTT ---
MQTT_HOST = "localhost"
MQTT_PORT = 1883
TOPIC = "sensores/datos"

# --- AJUSTES INFLUXDB (Deben coincidir con el docker-compose) ---
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "super-secreto-token-1234"
INFLUX_ORG = "biomedica"
INFLUX_BUCKET = "datos_sensores"

print("🔄 Conectando a InfluxDB...")
client_influx = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)

# Usamos batching para no saturar la BD al enviar datos a 100Hz
write_api = client_influx.write_api(write_options=WriteOptions(batch_size=100, flush_interval=500))

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Conectado a Mosquitto. Escuchando datos en tiempo real...")
        client.subscribe(TOPIC)
    else:
        print(f"❌ Error MQTT: {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        
        # Crear un "Punto" de datos para InfluxDB
        punto = Point("lectura_biometrica") \
            .tag("sujeto", "javi") \
            .field("ax", float(payload.get("ax", 0))) \
            .field("ay", float(payload.get("ay", 0))) \
            .field("az", float(payload.get("az", 0))) \
            .field("L_env", float(payload.get("L_env", 0))) \
            .field("L_raw", float(payload.get("L_raw", 0))) \
            .field("R_env", float(payload.get("R_env", 0))) \
            .field("R_raw", float(payload.get("R_raw", 0)))
        
        # Enviar a InfluxDB
        write_api.write(bucket=INFLUX_BUCKET, record=punto)
        
    except Exception as e:
        pass # Silenciamos errores de parseo para no frenar el flujo en tiempo real

# Configuración del cliente MQTT
cliente_mqtt = mqtt.Client()
cliente_mqtt.on_connect = on_connect
cliente_mqtt.on_message = on_message

cliente_mqtt.connect(MQTT_HOST, MQTT_PORT, 60)

try:
    # Inicia el bucle infinito
    cliente_mqtt.loop_forever()
except KeyboardInterrupt:
    print("\n🛑 Puente detenido por el usuario.")
    write_api.close()
    client_influx.close()