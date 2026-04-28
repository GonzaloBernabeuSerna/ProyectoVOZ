from machine import SPI, Pin, ADC
import time, json

# --- Configuración ADXL355 ---
spi = SPI(1, baudrate=1_000_000, polarity=0, phase=0,
          sck=Pin(48), mosi=Pin(38), miso=Pin(47))
cs = Pin(21, Pin.OUT, value=1)

# --- Configuración MyoWare ---
env = ADC(Pin(1)) # A0 del Nano (ENV)
env.atten(ADC.ATTN_11DB)

def reg_read(reg, n=1):
    cs(0); spi.write(bytearray([(reg << 1) | 1])); data = spi.read(n); cs(1)
    return data

# Wake up ADXL
cs(0); spi.write(bytearray([0x2D << 1, 0x00])); cs(1)

print("--- TEST DE BRAZO: ACELERÓMETRO + MÚSCULO ---")
print("Cierra el puño fuerte para ver el EMG...")

while True:
    # 1. Leer ADXL
    try:
        data = reg_read(0x08, 9)
        def conv(b):
            v = (b[0] << 12) | (b[1] << 4) | (b[2] >> 4)
            if v & 0x80000: v -= 0x100000
            return v * (2.0 / 2**19)
        ax = conv(data[0:3])
    except:
        ax = 0

    # 2. Leer MyoWare (EMG)
    v_emg = env.read_u16() * 3.3 / 65535
    
    # 3. Visualización en barritas (Para verlo claro en la consola)
    barra_emg = "|" * int(v_emg * 30)
    # Detectamos movimiento brusco con el acelerómetro
    mov = "MOVIMIENTO!" if abs(ax) > 0.5 else "quieto"

    print(f"EMG: {v_emg:.2f}V {barra_emg.ljust(30)} | Accel X: {ax:.2f}g ({mov})")
    
    time.sleep_ms(50)