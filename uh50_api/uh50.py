"""
This module reads from the Landys & Gyr UH50 heat measuring unit and returns the currect GJ and m3 meters.
WARNING: everytime this is called, battery time of the UH50 will go down by about 30 minutes!

Usage: read_uh50(port), eg read_uh50('/dev/ttyUSB0') or read_uh50('COM5')

Calling the module directly will allow for usage through command lime
"""
from pyexpat import model
import re
from serial import Serial
import serial
import serial.tools.list_ports
from typing import TypedDict
from random import randrange

def find_ports():
    "Returns the available ports"
    return serial.tools.list_ports.comports()
    
class UH50:
    """Class for reading the UH50 on the specified port"""
    #TODO toevoegen van variabelen en read vervangen door update en die zet dan de waarden in de variabelen 

    def __init__(self, port: str) -> None:
        self.port = port

    _gj = ''
    _m3 = ''
    _model = ''
    _full_response = ''

    class _UH50Summary(TypedDict):
        gj: str
        m3: str
        model: str
        full_response: str

    @property
    def gj(self) -> str:
        """Get the current GJ measurement of the connected device."""
        return self._gj

    @property
    def m3(self) -> str:
        """Get the current m3 measurement of the connected device."""
        return self._m3

    @property
    def model(self) -> str:
        """Get the model of the connected device."""
        return self._model

    @property
    def full_response(self) -> str:
        """Get the full response of the connected device."""
        return self._full_response

    def update(self) -> None:
        "Reads the UH50 on the specified port, searching for info on GJ and m3"
        with self._connect_serial() as conn:
            self._model = self._wake_up(conn)

            # checking if we can read the model (eg. 'LUGCUH50')
            if not(self._model):
                raise Exception('No model could be read')
            
            self._full_response = self._get_data(conn)
            self._gj, self._m3 = self._search_data(self._full_response)

    def update_dummy(self) -> None:
        "Sets dummy values for testing purposes, when no live connection is available"
        self._gj = '999.'+str(randrange(100,999)) 
        self._m3 = '9999.'+str(randrange(10,99))
        self._model = 'LUGCUH50' 

    def _search_data(self, data):
        match = re.search( r'6.8\((.*)\*GJ\)6.26\((.*)\*m3\)9.21\(66153690\)', str(data), re.M|re.I)
        if match: 
            return match.group(1),match.group(2)

        raise Exception("GJ and m3 values not found")

    def validate(self) -> Serial:
        try:
            result = self._connect_serial()
            result.close
        except:
            raise

    def _connect_serial(self) -> Serial:
        "Make the connection to the serial device"
        return serial.Serial(self.port,
                            baudrate=300,
                            bytesize=serial.SEVENBITS,
                            parity=serial.PARITY_EVEN,
                            stopbits=serial.STOPBITS_TWO,
                            timeout=1,
                            xonxoff=0,
                            rtscts=0
                            )

    def _wake_up(self, conn) -> str:
        "Waking up the device and get the model number"
        # Waking up should be done at 300 baud
        # Sending /?!
        conn.write(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x2F\x3F\x21\x0D\x0A")
        ir_command='/?!\x0D\x0A'
        conn.write(ir_command.encode('utf-8'))
        conn.flush()
        return conn.readline().decode('utf-8')[1:9]   # Read at 300 baud, this gives us the typenr

    def _get_data(self, conn):
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
        heat_meter = UH50(port)
        heat_meter.update()
        result = heat_meter.read
        print('GJ :',heat_meter.gj)
        print('m3 :',heat_meter.m3)
        print('model :',heat_meter.model)
        print('full response :',heat_meter.full_response)
    except serial.serialutil.SerialException:
        print("Couldn't connect to port", port)
        print("Are you using sudo?")
    except:
        print('Something went wrong')
        raise
