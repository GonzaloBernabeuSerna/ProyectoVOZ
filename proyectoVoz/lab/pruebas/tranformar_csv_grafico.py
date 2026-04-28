import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog

# Esto abre una ventana para elegir el archivo .csv
root = tk.Tk()
root.withdraw()
ruta_archivo = filedialog.askopenfilename(title="Selecciona el archivo CSV del Proyecto Voz", filetypes=[("Archivos CSV", "*.csv")])

if ruta_archivo:
    df = pd.read_csv(ruta_archivo)
    
    # 1. TRUCO DE LAS VIBRACIONES: Restar la media para eliminar la gravedad
    # Así las 3 líneas se centran en el 0 y podemos hacer zoom en los micro-movimientos
    df['ax_vib'] = df['ax'] - df['ax'].mean()
    df['ay_vib'] = df['ay'] - df['ay'].mean()
    df['az_vib'] = df['az'] - df['az'].mean()
    
    # 2. TRUCO DE LAS PROPORCIONES: El acelerómetro será el doble de alto que el EMG
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})

    # Gráfica de Acelerómetro (Ahora muestra las vibraciones puras)
    ax1.plot(df['t_ms'], df['ax_vib'], label='Vibración X', linewidth=0.8)
    ax1.plot(df['t_ms'], df['ay_vib'], label='Vibración Y', linewidth=0.8)
    ax1.plot(df['t_ms'], df['az_vib'], label='Vibración Z', linewidth=0.8)
    ax1.set_title('Vibración del Cuello (Micro-movimientos sin Gravedad)')
    ax1.set_ylabel('Aceleración (g)')
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)

    # Gráfica de Músculo
    # 3. TRUCO VISUAL: Ponemos el RAW de fondo suave y el ENV fuerte encima
    if 'emg_raw' in df.columns:
        ax2.plot(df['t_ms'], df['emg_raw'], color='gray', alpha=0.4, label='EMG Raw', linewidth=0.5)
        
    ax2.plot(df['t_ms'], df['emg_env'], color='red', label='EMG Envolvente', linewidth=1.5)
    ax2.set_title('Actividad Muscular (MyoWare)')
    ax2.set_ylabel('Voltios (V)')
    ax2.set_xlabel('Tiempo (ms)')
    
    # Forzar que el eje Y del músculo empiece en 0 para que no quede flotando
    ax2.set_ylim(bottom=0)
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()
else:
    print("No seleccionaste ningún archivo.")