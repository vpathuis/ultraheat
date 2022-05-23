from pprint import pprint
import sys
from service import HeatMeterService
from file_reader import FileReader
from uh50_reader import UH50Reader
import serial.tools.list_ports


def find_ports():
    "Returns the available ports"
    return serial.tools.list_ports.comports()


if __name__ == "__main__":
    file_name = ""
    if sys.argv[1] == 'ports':
        print('showing available ports: ')
        ports = find_ports()
        for p in ports:
            print(p.device)
        print(len(ports), 'ports found')
        exit()

    elif sys.argv[1] == 'file':
        if len(sys.argv) > 2:
            file_name = sys.argv[2]
        else:
            print('Using default dummy file')
            file_name = r"C:\repositories\thuis\domotica\uh50\tests\dummy_response.txt"

    elif sys.argv[1] == 'port':
        if len(sys.argv) > 2:
            port = sys.argv[2]
        else:
            print("Port missing")
            exit()
    else:
        print("usage: python uh50_api.py <ports|file|port> [path_to_file|portname]")
        print("port: something like '/dev/ttyUSB0' or 'COM5'")
        exit()

    if file_name:
        reader = FileReader(file_name)
    else:
        # reader = UH50Reader
        print('WARNING: everytime the UH50-unit is read, battery time of the UH50 will go down by about 30 minutes!')
        reader = UH50Reader(port)

    heat_meter_service = HeatMeterService(reader)
    response_data = heat_meter_service.read()

    print('heat_usage_gj: ' + str(response_data.heat_usage_gj))
    print('volume_usage_m3: ' + str(response_data.volume_usage_m3))
    print('ownership_number: ' + str(response_data.ownership_number))
    print('volume_previous_year_m3: ' +
          str(response_data.volume_previous_year_m3))
    print('heat_previous_year_gj: ' + str(response_data.heat_previous_year_gj))
    print('error_number: ' + str(response_data.error_number))
    print('device_number: ' + str(response_data.device_number))
    print('measurement_period_minutes: ' +
          str(response_data.measurement_period_minutes))
    print('power_max_kw: ' + str(response_data.power_max_kw))
    print('power_max_previous_year_kw: ' +
          str(response_data.power_max_previous_year_kw))
    print('flowrate_max_m3ph: ' + str(response_data.flowrate_max_m3ph))
    print('flow_temperature_max_c: ' + str(response_data.flow_temperature_max_c))
    print('flowrate_max_previous_year_m3ph: ' +
          str(response_data.flowrate_max_previous_year_m3ph))
    print('return_temperature_max_c: ' +
          str(response_data.return_temperature_max_c))
    print('flow_temperature_max_previous_year_c: ' +
          str(response_data.flow_temperature_max_previous_year_c))
    print('return_temperature_max_previous_year_c: ' +
          str(response_data.return_temperature_max_previous_year_c))
    print('operating_hours: ' + str(response_data.operating_hours))
    print('fault_hours: ' + str(response_data.fault_hours))
    print('fault_hours_previous_year: ' +
          str(response_data.fault_hours_previous_year))
    print('yearly_set_day: ' + str(response_data.yearly_set_day))
    print('monthly_set_day: ' + str(response_data.monthly_set_day))
    print('meter_date_time: ' + str(response_data.meter_date_time))
    print('measuring_range_m3ph: ' + str(response_data.measuring_range_m3ph))
    print('settings_and_firmware: ' + str(response_data.settings_and_firmware))
    print('flow_hours: ' + str(response_data.flow_hours))
