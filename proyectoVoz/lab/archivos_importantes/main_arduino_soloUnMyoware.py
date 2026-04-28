from machine import SPI, Pin, ADC
import time, json

# --- CONFIGURACIÓN SPI (Acelerómetro) ---
spi = SPI(1, baudrate=1_000_000, polarity=0, phase=0, sck=Pin(48), mosi=Pin(38), miso=Pin(47))
cs = Pin(21, Pin.OUT, value=1)

# --- CONFIGURACIÓN ADC (1 solo Myoware) ---
emg_env = ADC(Pin(1))
emg_raw = ADC(Pin(2))
emg_env.atten(ADC.ATTN_11DB)
emg_raw.atten(ADC.ATTN_11DB)

# --- PARÁMETROS ---
GANANCIA = 1.5
ESCALA_ADXL = 2.0 / 524288

def leer_xyz():
    try:
        cmd = bytearray([(0x08 << 1) | 1] + [0] * 9)
        buf = bytearray(10)
        cs(0); spi.write_readinto(cmd, buf); cs(1)
        raw = buf[1:]
        def c(a,b,c_):
            v = (a<<12)|(b<<4)|(c_>>4)
            return (v - (1<<20)) * ESCALA_ADXL if v & (1<<19) else v * ESCALA_ADXL
        return c(raw[0],raw[1],raw[2]), c(raw[3],raw[4],raw[5]), c(raw[6],raw[7],raw[8])
    except:
        return 0, 0, 0

# Wake up ADXL355
cs(0); spi.write(bytearray([0x2D<<1, 0x00])); cs(1)
time.sleep_ms(100)

print('{"status":"ready", "config":"Single-MyoWare"}')

while True:
    try:
        t = time.ticks_ms()
        ax, ay, az = leer_xyz()
        
        # Lectura única
        val_env = (emg_env.read_u16() * 3.3 / 65535) * GANANCIA
        val_raw = (emg_raw.read_u16() * 3.3 / 65535)
        
        print(json.dumps({
            "t": t,
            "ax": round(ax, 4), "ay": round(ay, 4), "az": round(az, 4),
            "env": round(val_env, 4), 
            "raw": round(val_raw, 4)
        }))
        
    except Exception:
        pass
    time.sleep_ms(10)