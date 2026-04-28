# validar_electrodos.py — ejecutar ANTES de cada sesión de captura
import serial, json, numpy as np
from collections import deque

# --- CONFIGURACIÓN ---
PUERTO  = "COM7"   # ¡Asegúrate de que este es el puerto correcto de tu Arduino!
BAUDIOS = 115200
CANALES = ["L_env", "R_env"] # Cambiado para coincidir con el nuevo main.py
VENTANA = 50           # 5 segundos a 10 Hz aprox para la línea base

bufs = {c: deque(maxlen=VENTANA) for c in CANALES}

print("=== VALIDACIÓN DE ELECTRODOS (MODO DUAL L/R) ===")
print("1) Pide al sujeto que esté en REPOSO (sin hablar ni tragar).")
print("2) MIDIENDO LÍNEA BASE... Espera unos segundos.")

try:
    with serial.Serial(PUERTO, BAUDIOS, timeout=1) as ser:
        ser.reset_input_buffer()
        muestras = 0
        
        # FASE 1: REPOSO
        while muestras < VENTANA:
            linea = ser.readline().decode("utf-8").strip()
            if not linea: continue
            try:
                d = json.loads(linea)
                if "L_env" not in d: continue # Salta líneas que no tengan datos EMG
                
                for c in CANALES: 
                    bufs[c].append(d[c])
                muestras += 1
            except: continue

        # Cálculo de línea base
        baselines = {c: np.mean(bufs[c]) for c in CANALES}
        print(f"\nLínea base calculada (Reposo):")
        for c, v in baselines.items():
            estado = "✓ OK" if v < 0.08 else "⚠ ALTA (revisar contacto)"
            nombre = "Izquierdo" if "L" in c else "Derecho"
            print(f"  {nombre} ({c}): {v:.4f} V  {estado}")

        # FASE 2: FONACIÓN
        print("\n" + "="*40)
        print("Ahora pide al sujeto que hable o emita un sonido constante.")
        input("[Pulsa ENTER cuando el sujeto empiece a hablar]")
        print("Midiendo picos de activación...")

        picos = {c: [] for c in CANALES}
        # Tomamos unas 50 muestras durante la fonación
        for _ in range(50): 
            linea = ser.readline().decode("utf-8").strip()
            if not linea: continue
            try:
                d = json.loads(linea)
                if "L_env" in d:
                    for c in CANALES: picos[c].append(d[c])
            except: continue

    # RESULTADOS FINALES
    print("\n=== RESULTADO DE LA VALIDACIÓN ===")
    print(f"{'Canal':<12} {'Reposo':>10} {'Pico':>10} {'Ratio':>8} {'Estado':>16}")
    print("-" * 60)

    todo_ok = True
    for c in CANALES:
        base  = baselines[c]
        pico  = np.max(picos[c]) if picos[c] else 0
        ratio = pico / base if base > 0.001 else 0
        
        # Según el protocolo, buscamos un ratio de al menos 2x
        valido = ratio >= 2.0
        if not valido: todo_ok = False
        
        nombre = "IZQ (S1)" if "L" in c else "DER (S2)"
        estado = "✓ VÁLIDO" if valido else "✗ REPOSICIONAR"
        
        print(f"{nombre:<12} {base:>10.4f} {pico:>10.4f} {ratio:>8.1f}x  {estado}")

    print("-" * 60)
    if todo_ok:
        print("¡TODO LISTO! Puedes proceder con la captura de datos.")
    else:
        print("ATENCIÓN: Algún electrodo no tiene suficiente señal. Revisa el contacto.")

except Exception as e:
    print(f"\nERROR de conexión: {e}")
    print("Asegúrate de que Thonny esté CERRADO o con el stop dado para liberar el puerto COM.")