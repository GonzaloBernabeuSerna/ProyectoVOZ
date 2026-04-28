# ... (mantened la parte del SPI y ADXL355 igual) ...

# --- PARÁMETROS DE SENSIBILIDAD ---
GANANCIA_EMG = 1.5  # Podéis subir esto a 2.0 si sigue saliendo bajito
UMBRAL_RUIDO = 0.02 # Ignora pequeñas fluctuaciones cuando no habláis

while True:
    try:
        t = time.ticks_ms()
        x, y, z = leer_xyz()
        
        # Lectura y amplificación por software
        v_env = (emg_env.read_u16() * 3.3 / 65535) * GANANCIA_EMG
        v_raw = (emg_raw.read_u16() * 3.3 / 65535) * GANANCIA_EMG
        
        # Filtro de ruido simple
        if v_env < UMBRAL_RUIDO: v_env = 0.0
        
        print(json.dumps({
            "t": t,
            "ax": round(x, 5), "ay": round(y, 5), "az": round(z, 5),
            "env": round(v_env, 4),
            "raw": round(v_raw, 4)
        }))
    except:
        pass
    
    time.sleep_ms(10) # 100 Hz estables