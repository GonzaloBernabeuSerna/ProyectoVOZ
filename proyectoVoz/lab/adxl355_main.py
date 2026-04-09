# adxl355_main.py — Lectura del ADXL355 por SPI
from machine import SPI, Pin
import time, json, struct

# ── Registros del ADXL355 ────────────────────────────
REG_DEVID_AD  = 0x00   # Debe leer 0xAD
REG_RANGE     = 0x2C   # Configurar rango
REG_POWER_CTL = 0x2D   # Control de energía
REG_XDATA3    = 0x08   # Primer byte de X (MSB)

# ── Configurar SPI ────────────────────────────────────
spi = SPI(1, baudrate=1_000_000, polarity=0, phase=0,
          sck=Pin(48), mosi=Pin(38), miso=Pin(47))
cs = Pin(21, Pin.OUT, value=1)

def leer_registro(reg, n=1):
    """Lee n bytes del registro reg."""
    cmd = bytearray([reg << 1 | 1] + [0] * n)  # bit0=1: lectura
    buf = bytearray(n + 1)
    cs(0)
    spi.write_readinto(cmd, buf)
    cs(1)
    return buf[1:]

def escribir_registro(reg, valor):
    cmd = bytearray([reg << 1, valor])   # bit0=0: escritura
    cs(0)
    spi.write(cmd)
    cs(1)

# ── Inicializar ADXL355 ───────────────────────────────
devid = leer_registro(REG_DEVID_AD)[0]
print(f"DEVID: 0x{devid:02X}")   # Debe imprimir: DEVID: 0xAD

escribir_registro(REG_RANGE, 0x01)       # Rango ±2g
escribir_registro(REG_POWER_CTL, 0x00)   # Modo medición (activo)
time.sleep_ms(100)

# ── Escala para ±2g (20-bit) ──────────────────────────
ESCALA = 2.0 / (2**19)   # LSB → g

def leer_aceleracion():
    raw = leer_registro(REG_XDATA3, 9)  # 3 bytes × 3 ejes
    
    # Convertir 20 bits con signo (complemento a 2)
    def conv(b0, b1, b2):
        val = (b0 << 12) | (b1 << 4) | (b2 >> 4)
        if val & (1 << 19):   # bit de signo
            val -= 1 << 20
        return val * ESCALA
    
    x = conv(raw[0], raw[1], raw[2])
    y = conv(raw[3], raw[4], raw[5])
    z = conv(raw[6], raw[7], raw[8])
    return x, y, z

# ── Bucle principal ───────────────────────────────────
while True:
    x, y, z = leer_aceleracion()
    datos = {"t": time.ticks_ms(), "x": x, "y": y, "z": z}
    print(json.dumps(datos))
    time.sleep_ms(20)   # 50 Hz