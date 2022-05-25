import serial

def find_ports():
    "Returns the available ports"
    return serial.tools.list_ports.comports()
