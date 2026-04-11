from machine import SPI, Pin, ADC
import time, json

# --- CONFIGURACIÓN SPI (Acelerómetro) ---
spi = SPI(1, baudrate=1_000_000, polarity=0, phase=0, sck=Pin(48), mosi=Pin(38), miso=Pin(47))
cs = Pin(21, Pin.OUT, value=1)

# --- CONFIGURACIÓN ADC (2 Myowares) ---
# Canal Izquierdo (L) -> A0 (ENV) y A1 (RAW)
emg_L_env = ADC(Pin(1))
emg_L_raw = ADC(Pin(2))

# Canal Derecho (R) -> A2 (ENV) y A3 (RAW)
emg_R_env = ADC(Pin(3))
emg_R_raw = ADC(Pin(4))

for adc in [emg_L_env, emg_L_raw, emg_R_env, emg_R_raw]:
    adc.atten(ADC.ATTN_11DB)

# --- PARÁMETROS ---
GANANCIA = 1.5
UMBRAL = 0.000 
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

print('{"status":"ready", "config":"Dual-MyoWare-L/R"}')

while True:
    try:
        # 1. Captura de tiempo y movimiento
        t = time.ticks_ms()
        ax, ay, az = leer_xyz()
        
        # 2. Captura Músculo Izquierdo (L)
        L_env = (emg_L_env.read_u16() * 3.3 / 65535) * GANANCIA
        L_raw = (emg_L_raw.read_u16() * 3.3 / 65535)
        
        # 3. Captura Músculo Derecho (R)
        R_env = (emg_R_env.read_u16() * 3.3 / 65535) * GANANCIA
        R_raw = (emg_R_raw.read_u16() * 3.3 / 65535)
        
        # 4. Filtro de ruido digital
        L_env = L_env if L_env > UMBRAL else 0.0
        R_env = R_env if R_env > UMBRAL else 0.0

        # 5. Envío JSON
        print(json.dumps({
            "t": t,
            "ax": round(ax, 4), "ay": round(ay, 4), "az": round(az, 4),
            "L_env": round(L_env, 4), "L_raw": round(L_raw, 4),
            "R_env": round(R_env, 4), "R_raw": round(R_raw, 4)
        }))
        
    except Exception as e:
        pass # Silenciamos errores momentáneos para no romper la gráfica
        
    time.sleep_ms(10)
