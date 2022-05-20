"""
This module reads from the Landys & Gyr UH50 heat measuring unit and returns the currect GJ and m3 meters.
WARNING: everytime this is called, battery time of the UH50 will go down by about 30 minutes!

"""
from datetime import datetime
from pyexpat import model
import re
from serial import Serial
import serial
import serial.tools.list_ports
from random import randrange
from pprint import pprint

# defines the search expressions used when parsing the response from the heat meter
UH50_REGEX_CONFIG = {
    'heat_usage_gj': r'6.8\((.*?)\*GJ\)',
    'volume_usage_m3': r'6.26\((.*?)\*m3\)',
    'ownership_number': r'9.21\((.*?)\)',
    'volume_previous_year_m3': r'6.26\*01\((.*?)\*m3\)',
    'heat_previous_year_gj': r'6.8\*01\((.*?)\*GJ\)',
    'error_number': r'F\((.*?)\)',
    'device_number': r'9.20\((.*?)\)',
    'measurement_period_minutes': r'6.35\((.*?)\*m\)',
    'power_max_kw': r'6.6\((.*?)\*kW\)',
    'power_max_previous_year_kw': r'6.6\*01\((.*?)\*kW\)',
    'flowrate_max_m3ph': r'6.33\((.*?)\*m3ph\)',
    'flowrate_max_previous_year_m3ph': r'6.33\*01\((.*?)\*m3ph\)',
    'flow_temperature_max_c': r'9.4\((.*?)\*C',
    'return_temperature_max_c': r'9.4\(.*?\*C&(.*?)\*C',
    'flow_temperature_max_previous_year_c': r'9.4\*01\((.*?)\*C',
    'return_temperature_max_previous_year_c': r'9.4\*01\(.*?\*C&(.*?)\*C',
    'operating_hours': r'6.31\((.*?)\*h\)',
    'fault_hours': r'6.32\((.*?)\*h\)',
    'fault_hours_previous_year': r'6.32\*01\((.*?)\*h\)',
    'yearly_set_day': r'6.36\((.*?)\)',
    'monthly_set_day': r'6.36\*02\((.*?)\)',
    'meter_date_time': r'9.36\((.*?)\)',
    'measuring_range_m3ph': r'9.24\((.*?)\*m3ph\)',
    'settings_and_firmware': r'9.1\((.*?)\)',
    'flow_hours': r'9.31\((.*?)\*h\)',
}

def find_ports():
    "Returns the available ports"
    return serial.tools.list_ports.comports()

class UH50:
    """Class for reading the UH50 on the specified port"""

    def __init__(self, port: str) -> None:
        self.port = port

    def update(self) -> None:
        "Reads the UH50 on the specified port, searching for info on GJ and m3"
        with self._connect_serial() as conn:
            self.model = self._wake_up(conn)

            # checking if we can read the model (eg. 'LUGCUH50')
            if not(self.model):
                raise Exception('No model could be read')
            
            self._full_response = self._get_data(conn)
            self._gj, self._m3 = self._search_data(self._full_response)

    def update_dummy(self) -> None:
        "Sets dummy values for testing purposes, when no live connection is available"
        self.heat_usage_gj = '999.'+str(randrange(100,999)) 
        self.volume_usage_m3 = '9999.'+str(randrange(10,99))
        self.model = 'LUGCUH50' 

    def _search_response(self, data):
        """Search the response from the heat meter for values that we can use"""

        # heat_usage_gj
        match = re.search(UH50_REGEX_CONFIG['heat_usage_gj'], str(data), re.M|re.I)
        if match:
            try:
                self.heat_usage_gj = float(match.group(1))
            except:
                self.heat_usage_gj = match.group(1)

        # volume_usage_m3
        match = re.search(UH50_REGEX_CONFIG['volume_usage_m3'], str(data), re.M|re.I)
        if match:
            try:
                self.volume_usage_m3 = float(match.group(1))
            except:
                self.volume_usage_m3 = match.group(1)
        
        # ownership_number
        match = re.search(UH50_REGEX_CONFIG['ownership_number'], str(data), re.M|re.I)
        if match:
            self.ownership_number = match.group(1)
        
        # volume_previous_year_m3
        match = re.search(UH50_REGEX_CONFIG['volume_previous_year_m3'], str(data), re.M|re.I)
        if match:
            try:
                self.volume_previous_year_m3 = float(match.group(1))
            except:
                self.volume_previous_year_m3 = match.group(1)

        # heat_previous_year_gj
        match = re.search(UH50_REGEX_CONFIG['heat_previous_year_gj'], str(data), re.M|re.I)
        if match:
            try:
                self.heat_previous_year_gj = float(match.group(1))
            except:
                self.heat_previous_year_gj = match.group(1)
        
        # error_number
        match = re.search(UH50_REGEX_CONFIG['error_number'], str(data), re.M|re.I)
        if match:
            self.error_number = match.group(1)

        # device_number
        match = re.search(UH50_REGEX_CONFIG['device_number'], str(data), re.M|re.I)
        if match:
            self.device_number = match.group(1)

        # measurement_period_minutes
        match = re.search(UH50_REGEX_CONFIG['measurement_period_minutes'], str(data), re.M|re.I)
        if match:
            try:
                self.measurement_period_minutes = int(match.group(1))
            except:
                self.measurement_period_minutes = match.group(1)

        # power_max_kw
        match = re.search(UH50_REGEX_CONFIG['power_max_kw'], str(data), re.M|re.I)
        if match:
            try:
                self.power_max_kw = float(match.group(1))
            except:
                self.power_max_kw = match.group(1)

        # power_max_previous_year_kw
        match = re.search(UH50_REGEX_CONFIG['power_max_previous_year_kw'], str(data), re.M|re.I)
        if match:
            try:
                self.power_max_previous_year_kw = float(match.group(1))
            except:
                self.power_max_previous_year_kw = match.group(1)

        # flowrate_max_m3ph
        match = re.search(UH50_REGEX_CONFIG['flowrate_max_m3ph'], str(data), re.M|re.I)
        if match:
            try:
                self.flowrate_max_m3ph = float(match.group(1))
            except:
                self.flowrate_max_m3ph = match.group(1)
        
        # flow_temperature_max_c
        match = re.search(UH50_REGEX_CONFIG['flow_temperature_max_c'], str(data), re.M|re.I)
        if match:
            try:
                self.flow_temperature_max_c = float(match.group(1))
            except:
                self.flow_temperature_max_c = match.group(1)

        # flowrate_max_previous_year_m3ph
        match = re.search(UH50_REGEX_CONFIG['flowrate_max_previous_year_m3ph'], str(data), re.M|re.I)
        if match:
            try:
                self.flowrate_max_previous_year_m3ph = float(match.group(1))
            except:
                self.flowrate_max_previous_year_m3ph = match.group(1)
                
        # return_temperature_max_c
        match = re.search(UH50_REGEX_CONFIG['return_temperature_max_c'], str(data), re.M|re.I)
        if match:
            try:
                self.return_temperature_max_c = float(match.group(1))
            except:
                self.return_temperature_max_c = match.group(1)

        # flow_temperature_max_previous_year_c
        match = re.search(UH50_REGEX_CONFIG['flow_temperature_max_previous_year_c'], str(data), re.M|re.I)
        if match:
            try:
                self.flow_temperature_max_previous_year_c = float(match.group(1))
            except:
                self.flow_temperature_max_previous_year_c = match.group(1)

        # return_temperature_max_previous_year_c
        match = re.search(UH50_REGEX_CONFIG['return_temperature_max_previous_year_c'], str(data), re.M|re.I)
        if match:
            try:
                self.return_temperature_max_previous_year_c = float(match.group(1))
            except: 
                self.return_temperature_max_previous_year_c = match.group(1)
        
        # operating_hours
        match = re.search(UH50_REGEX_CONFIG['operating_hours'], str(data), re.M|re.I)
        if match:
            try:
                self.operating_hours = int(match.group(1))
            except:
                self.operating_hours = match.group(1)
        
        # fault_hours
        match = re.search(UH50_REGEX_CONFIG['fault_hours'], str(data), re.M|re.I)
        if match:
            try:
                self.fault_hours = int(match.group(1))
            except:
                self.fault_hours = match.group(1)

        # fault_hours_previous_year
        match = re.search(UH50_REGEX_CONFIG['fault_hours_previous_year'], str(data), re.M|re.I)
        if match:
            try:
                self.fault_hours_previous_year = int(match.group(1))
            except:
                self.fault_hours_previous_year = match.group(1)

        # yearly_set_day
        match = re.search(UH50_REGEX_CONFIG['yearly_set_day'], str(data), re.M|re.I)
        if match:
            self.yearly_set_day = match.group(1)

        # monthly_set_day
        match = re.search(UH50_REGEX_CONFIG['monthly_set_day'], str(data), re.M|re.I)
        if match:
            self.monthly_set_day = match.group(1)

        # meter_date_time
        match = re.search(UH50_REGEX_CONFIG['meter_date_time'], str(data), re.M|re.I)
        if match:
            try:
                self.meter_date_time = datetime.strptime(match.group(1),'%Y-%m-%d&%H:%M:%S')
            except:
                self.meter_date_time = match.group(1)

        # measuring_range_m3ph
        match = re.search(UH50_REGEX_CONFIG['measuring_range_m3ph'], str(data), re.M|re.I)
        if match:
            try:
                self.measuring_range_m3ph = float(match.group(1))
            except:
                self.measuring_range_m3ph = match.group(1)

        # settings_and_firmware
        match = re.search(UH50_REGEX_CONFIG['settings_and_firmware'], str(data), re.M|re.I)
        if match:
            self.settings_and_firmware = match.group(1)

        # flow_hours
        match = re.search(UH50_REGEX_CONFIG['flow_hours'], str(data), re.M|re.I)
        if match:
            try:
                self.flow_hours = int(match.group(1))
            except:
                self.flow_hours = match.group(1)

        return
 
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
        conn.baudrate=2400 # Now switch to 2400 BAUD. This could be different for other models. Let me know if you experience problems.
        ir_lines = ""
        ir_line = ""
        iteration = 0
        while ir_line != b'' and iteration < 100:
            iteration += 1
            ir_line = conn.readline()
            ir_lines+=ir_line.decode('utf-8')

        return ir_lines

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
        pprint(vars(heat_meter))
    except serial.serialutil.SerialException:
        print("Couldn't connect to port", port)
        print("Are you using sudo?")
    except:
        print('Something went wrong')
        raise
