import machine, time, json

# Sensor de temperatura interno del ESP32-S3
sensor_temp = machine.ADC(machine.Pin(4))
sensor_temp.atten(machine.ADC.ATTN_11DB)

while True:
    raw = sensor_temp.read_u16()
    voltaje = raw * 3.3 / 65535
    
    # Enviar JSON por serial → el PC lo lee
    datos = {"t_ms": time.ticks_ms(), "raw": raw, "v": round(voltaje, 4)}
    print(json.dumps(datos))  # una línea JSON por ciclo
    time.sleep_ms(2)         # 10 Hz