import serial, json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

# --- CONFIGURACIÓN ---
PUERTO  = "COM7" 
BAUDIOS = 115200
VENTANA = 200  # Cantidad de puntos en pantalla

# Buffers circulares
buf_x = deque([0.0] * VENTANA, maxlen=VENTANA)
buf_y = deque([0.0] * VENTANA, maxlen=VENTANA)
buf_z = deque([0.0] * VENTANA, maxlen=VENTANA)

# Conexión Serial
try:
    ser = serial.Serial(PUERTO, BAUDIOS, timeout=0.1)
    ser.reset_input_buffer()
    print(f"Conectado a {PUERTO}. Pulsa Ctrl+C o cierra la ventana para salir.")
except Exception as e:
    print(f"Error: No se pudo abrir el puerto {PUERTO}. {e}")
    exit()

# --- CONFIGURAR GRÁFICA ---
fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
fig.suptitle("ADXL355 · Análisis de Vibración Laríngea (Filtrado)", fontsize=14)

colores = ['#38bdf8', '#86efac', '#fbbf24']
lineas = []
x_vals = np.arange(VENTANA)

for ax, color, eje in zip(axes, colores, ['X', 'Y', 'Z']):
    ln, = ax.plot(x_vals, [0]*VENTANA, color=color, lw=1.5)
    lineas.append(ln)
    # ZOOM AGRESIVO: +/- 0.05g para ver la voz sin gritar
    ax.set_ylim(-0.05, 0.05) 
    ax.set_ylabel(f"Eje {eje} (g)")
    ax.grid(True, alpha=0.3)
    ax.axhline(0, color='red', alpha=0.2, ls='--')

axes[-1].set_xlabel("Muestras en tiempo real")

def filtrar_y_centrar(data):
    """Resta la media para eliminar la gravedad y centra la señal en 0"""
    arr = np.array(data)
    return arr - np.mean(arr)

def update(frame):
    # Leer todos los datos pendientes en el puerto
    while ser.in_waiting > 0:
        linea = ser.readline().decode('utf-8').strip()
        try:
            d = json.loads(linea)
            buf_x.append(d['x'])
            buf_y.append(d['y'])
            buf_z.append(d['z'])
        except:
            continue

    # Actualizar los datos de las líneas con el filtro aplicado
    lineas[0].set_ydata(filtrar_y_centrar(list(buf_x)))
    lineas[1].set_ydata(filtrar_y_centrar(list(buf_y)))
    lineas[2].set_ydata(filtrar_y_centrar(list(buf_z)))
    
    return lineas

# Animación (interval=20 para que sea fluido)
ani = animation.FuncAnimation(fig, update, interval=20, blit=True, cache_frame_data=False)

plt.tight_layout()
plt.show()

ser.close()
print("Puerto cerrado. Fin del programa.")