import serial.tools.list_ports

def find_ports():
    "Returns the available ports"
    return serial.tools.list_ports.comports()
