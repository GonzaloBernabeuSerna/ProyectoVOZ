import serial
import time

PUERTO = "COM7" 
BAUDIOS = 115200

def enviar(ser, comando):
    ser.write(f"{comando}\r\n".encode())
    time.sleep(0.1)

try:
    with serial.Serial(PUERTO, BAUDIOS, timeout=2) as ser:
        print(f"✓ Conectado. Iniciando secuencia de colores en {PUERTO}...")
        time.sleep(2)
        
        # Configurar los 3 pines RGB como salida
        enviar(ser, "import machine")
        enviar(ser, "r = machine.Pin(14, machine.Pin.OUT)")
        enviar(ser, "g = machine.Pin(15, machine.Pin.OUT)")
        enviar(ser, "b = machine.Pin(16, machine.Pin.OUT)")
        
        # Apagar todos primero (poniéndolos a 1)
        enviar(ser, "r.value(1); g.value(1); b.value(1)")
        
        colores = [("ROJO", "r"), ("VERDE", "g"), ("AZUL", "b")]
        
        for nombre, led in colores:
            print(f"Encendiendo {nombre}...")
            enviar(ser, f"{led}.value(0)") # 0 lo ENCIENDE
            time.sleep(1)
            enviar(ser, f"{led}.value(1)") # 1 lo APAGA
            
        print("✨ ¡Prueba superada! Ahora ya sabes que los pines 14, 15 y 16 funcionan.")

except Exception as e:
    print(f"❌ Error: {e}")