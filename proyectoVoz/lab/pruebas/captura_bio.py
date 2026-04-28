# captura_bio.py — EMG + Acelerómetro simultáneos
from machine import SPI, Pin, ADC
import time, json

# ── SPI para ADXL355 ─────────────────────────────────
spi = SPI(1, baudrate=1_000_000, polarity=0, phase=0,
         sck=Pin(14), mosi=Pin(11), miso=Pin(12))
cs = Pin(10, Pin.OUT, value=1)

# ── ADC para MyoWare ─────────────────────────────────
emg_env = ADC(Pin(1))   # señal envolvente (procesada)
emg_raw = ADC(Pin(2))   # señal cruda
emg_env.atten(ADC.ATTN_11DB)
emg_raw.atten(ADC.ATTN_11DB)

ESCALA_ADXL = 2.0 / 524288  # ±2g, 20-bit

def leer_xyz():
    """Lee los 9 bytes de XYZ del ADXL355."""
    cmd = bytearray([(0x08 << 1) | 1] + [0] * 9)
    buf = bytearray(10)
    cs(0); spi.write_readinto(cmd, buf); cs(1)
    raw = buf[1:]
    def c(a,b,c_): 
        v = (a<<12)|(b<<4)|(c_>>4)
        return (v - (1<<20)) * ESCALA_ADXL if v & (1<<19) else v * ESCALA_ADXL
    return c(raw[0],raw[1],raw[2]), c(raw[3],raw[4],raw[5]), c(raw[6],raw[7],raw[8])

# ── Inicializar ADXL355 ───────────────────────────────
cs(0); spi.write(bytearray([0x2D<<1, 0x00])); cs(1)  # wake up
time.sleep_ms(100)
print('{"status":"ready","sensors":["adxl355","myoware"]}')

# ── Bucle de captura ─────────────────────────────────
while True:
    t = time.ticks_ms()
    x, y, z = leer_xyz()
    env_v = emg_env.read_u16() * 3.3 / 65535
    raw_v = emg_raw.read_u16() * 3.3 / 65535
    
    print(json.dumps({
        "t": t,
        "ax": round(x,5), "ay": round(y,5), "az": round(z,5),
        "emg_env": round(env_v,4),
        "emg_raw": round(raw_v,4)
    }))
    time.sleep_ms(10)   # 100 Hz