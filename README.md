# Landis+Gyr Heat Meter Python package
This module reads from the Landys & Gyr Ultraheat heat meter unit and returns the meter values.
Note: An (USB) IR reader is needed and connected to the machine running the python script

WARNING: everytime this is called, battery time of the Ultraheat will go down by about 30 minutes!
This package has been tested with the Landys & Gyr Ultraheat type UH50 (LUGCUH50). Other models are likely to work as well.

## Using the python integration from CLI
To use the module as a script, call the module directly with an -h flag, which will explain how to use it.
Reading the serial port requires access to the serial ports and might only works as root.

## Using the python integration as API
```python
import ultraheat_api as hm

# check available ports
ports = hm.find_ports() 
for p in ports:
    print(p.device)
print(len(ports), 'ports found')

# read the device from file for integration testing purposes
path = os.path.abspath(os.path.dirname(__file__))
file_name = os.path.join(path, "tests", "LUGCUH50_dummy.txt")
heat_meter_service = hm.HeatMeterService(hm.FileReader(file_name))
response_data = heat_meter_service.read()

# read the Ultraheat device
heat_meter_service = hm.HeatMeterService(hm.UltraheatReader(args.port))
response_data = heat_meter_service.read()

print('model :',heat_meter.model['value'])
print('GJ :',heat_meter.heat_usage_gj['value'])
print('m3 :',heat_meter.volume_usage_m3['value'])
..
print('m3 :',heat_meter.volume_usage_m3['unit'])
etc..

```
## Full list of available data
- heat_usage_gj
- volume_usage_m3
- ownership_number
- volume_previous_year_m3
- heat_previous_year_gj
- error_number
- device_number
- measurement_period_minutes
- power_max_kw
- power_max_previous_year_kw
- flowrate_max_m3ph
- flowrate_max_previous_year_m3ph
- flow_temperature_max_c
- return_temperature_max_c
- flow_temperature_max_previous_year_c
- return_temperature_max_previous_year_c
- operating_hours
- fault_hours
- fault_hours_previous_year
- yearly_set_day
- monthly_set_day
- meter_date_time
- measuring_range_m3ph
- settings_and_firmware
- flow_hours