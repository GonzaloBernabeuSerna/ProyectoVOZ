## Cargar esto main en el arduino y después con el contenedor en marcha, ejecutar este comando para escuchar los mensajes:
# docker exec -it mosquitto_broker mosquitto_sub -h localhost -t "sensores/temperatura"

import network
import time
import machine
import random
from umqtt.simple import MQTTClient

# 1. Configuración de tu red Wi-Fi
SSID = "Ddr"
PASSWORD = ""

# 2. Configuración del Broker MQTT (El Docker de tu ordenador)
MQTT_SERVER = "10.72.221.14" # PON AQUÍ LA IP DE TU ORDENADOR
CLIENT_ID = "ESP_MicroPython"

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Conectando a la red Wi-Fi...')
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.5)
            print('.', end='')
    print('\nWi-Fi conectado!')
    print('IP de la placa:', wlan.ifconfig()[0])

def conectar_mqtt():
    client = MQTTClient(CLIENT_ID, MQTT_SERVER)
    client.connect()
    print('Conectado al broker MQTT en:', MQTT_SERVER)
    return client

# --- EJECUCIÓN PRINCIPAL ---

conectar_wifi()

try:
    cliente_mqtt = conectar_mqtt()
except OSError as e:
    print('Fallo al conectar a MQTT. Reiniciando en 5 segundos...')
    time.sleep(5)
    machine.reset() # Reinicia la placa si no encuentra el servidor

# Bucle infinito enviando datos
while True:
    try:
        # Generamos un valor aleatorio simulando un sensor
        valor_sensor = random.randint(10, 50)
        
        # En MicroPython, MQTT requiere que los mensajes sean en formato texto/bytes
        mensaje = str(valor_sensor)
        
        print("Publicando mensaje:", mensaje)
        
        # Publicamos en el tema "sensores/temperatura"
        cliente_mqtt.publish(b"sensores/temperatura", mensaje.encode('utf-8'))
        
        # Esperamos 5 segundos antes del siguiente envío
        time.sleep(5)
        
    except OSError as e:
        print("Error de conexión. Reiniciando...")
        time.sleep(5)
        machine.reset()
