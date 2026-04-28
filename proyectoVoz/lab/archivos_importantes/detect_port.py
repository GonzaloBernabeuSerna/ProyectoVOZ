# lab01/detect_port.py — Detectar puerto del Arduino
import serial.tools.list_ports

def listar_puertos():
    puertos = list(serial.tools.list_ports.comports())
    if not puertos:
        print("❌ No se encontró ningún puerto serie.")
        return
    
    print(f"Puertos disponibles: {len(puertos)}\n")
    for p in puertos:
        print(f"  🔌 {p.device}")
        print(f"     Descripción : {p.description}")
        print(f"     Fabricante  : {p.manufacturer}")
        print()

listar_puertos()