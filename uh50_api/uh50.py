"""
This module reads from the Landys & Gyr UH50 heat measuring unit and returns the currect GJ and m3 meters.
WARNING: everytime this is called, battery time of the UH50 will go down by about 30 minutes!

Usage: read_uh50(port), eg read_uh50('/dev/ttyUSB0') or read_uh50('COM5')

Calling the module directly will allow for usage through command lime
"""
import re
from serial import Serial
import serial
import serial.tools.list_ports
from typing import TypedDict

class _UH50Summary(TypedDict):
    gj: str
    m3: str
    model: str
    full_response: str

def read_uh50(port) -> _UH50Summary:
    "Reads the UH50 on the specified port, searching for info on GJ and m3"
    with _connect_serial(port) as conn:
        model = _wake_up(conn)

        # checking if we can read the model (eg. 'LUGCUH50')
        if not(model):
            raise('No model could be read')
        
        full_response = _get_data(conn)
        gj, m3 = _search_data(full_response)
        return {'gj': gj, 'm3': m3, 'model': model, 'full_response': full_response}

def find_ports():
    "Returns the available ports"
    return serial.tools.list_ports.comports()

def _search_data(data):
    match = re.search( r'6.8\((.*)\*GJ\)6.26\((.*)\*m3\)9.21\(66153690\)', str(data), re.M|re.I)
    if match: 
        return match.group(1),match.group(2)

    raise Exception("GJ and m3 values not found")

def _connect_serial(port) -> Serial:
    return serial.Serial(port,
                        baudrate=300,
                        bytesize=serial.SEVENBITS,
                        parity=serial.PARITY_EVEN,
                        stopbits=serial.STOPBITS_TWO,
                        timeout=1,
                        xonxoff=0,
                        rtscts=0
                        )

def _wake_up(conn) -> str:
    # Waking up should be done at 300 baud
    # Sending /?!
    conn.write(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x2F\x3F\x21\x0D\x0A")
    ir_command='/?!\x0D\x0A'
    conn.write(ir_command.encode('utf-8'))
    conn.flush()   
    return conn.readline().decode('utf-8')[1:9]   # Read at 300 baud, this gives us the typenr

def _get_data(conn):
    #TODO make this asyc
    conn.baudrate=2400 # Now switch to 2400 BAUD. This could be different for other models. Let me know if you experience problems.
    return conn.readline().decode('utf-8') # Reading just one line, because that's where we know the data is.

if __name__ == "__main__":
    print('WARNING: everytime this is called, battery time of the UH50 will go down by about 30 minutes!')
    print('showing available ports: ')
    ports = find_ports()
    for p in ports:
        print(p.device)
    print(len(ports), 'ports found')

    port = input('Type the port the the IR-reader is on: ')  # eg /dev/ttyUSB0 or COM5
    try:
        result = read_uh50(port)
        print('GJ :',result['gj'])
        print('m3 :',result['m3'])
        print('model :',result['model'])
        print('full response :',result['full_response'])
    except serial.serialutil.SerialException:
        print("Couldn't connect to port", port)
        print("Are you using sudo?")
    except:
        print('Something went wrong')
        raise
