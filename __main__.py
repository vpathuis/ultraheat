import argparse, sys
import os
import sys
from uh50_api.service import HeatMeterService
from uh50_api.file_reader import FileReader
from uh50_api.uh50_reader import UH50Reader
import serial.tools.list_ports


def find_ports():
    "Returns the available ports"
    return serial.tools.list_ports.comports()


if __name__ == "__main__":

    parser=argparse.ArgumentParser()

    parser.add_argument('--file', help='Choose file mode and supply the filename or type default')
    parser.add_argument('--ports', help='Show available ports', action="store_true")
    parser.add_argument('--port', help="Choose port mode, supply the port name, eg. '/dev/ttyUSB0' or 'COM5'")
    parser.add_argument('--validate', help="Choose validate mode. Combine with --file or --port", action="store_true")

    args=parser.parse_args()

    if args.ports:
        print('showing available ports: ')
        ports = find_ports()
        for p in ports:
            print(p.device)
        print(len(ports), 'ports found')
        exit()

    elif args.file:
        if args.file == 'default':
            print('Using default dummy file')
            path = os.path.abspath(os.path.dirname(__file__))
            file_name = os.path.join(path,"tests","LUGCUH50_dummy.txt")
        else:
            file_name = args.file
        reader = FileReader(file_name)

    elif args.port:
        print('WARNING: everytime the UH50-unit is read, battery time of the UH50 will go down by about 30 minutes!')
        print('Reading ... this will take some time...')
        reader = UH50Reader(args.port)
    else:
        parser.print_help()
        exit()

    heat_meter_service = HeatMeterService(reader)

    if args.validate:
        model = heat_meter_service.validate()
        print('model: ' + model)
    else:
        response_data = heat_meter_service.read()

        print('model: ' + response_data.model)
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
