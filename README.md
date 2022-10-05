# Landis+Gyr Heat Meter Python package
This module reads from the Landys & Gyr Ultraheat heat meter unit and returns the meter values.
Note: An (USB) IR reader is needed and connected to the machine running the python script

WARNING: everytime this is called, battery time of the Ultraheat will go down by about 30 minutes!
This package has been tested with the Landys & Gyr Ultraheat type UH50 and T550. Other models are likely to work as well (please contact me if you want to help/test with adding support for other models).

## Using the python integration as API
```python
import ultraheat_api as hm

# Check available ports
ports = hm.find_ports() 
for p in ports:
    print(p.device)
print(len(ports), 'ports found')

# Read the device from file for integration testing purposes
path = os.path.abspath(os.path.dirname(__file__))
file_name = os.path.join(path, "tests", "LUGCUH50_dummy.txt")
heat_meter_service = hm.HeatMeterService(hm.FileReader(file_name))
response_data = heat_meter_service.read()

# Read the Ultraheat device
heat_meter_service = hm.HeatMeterService(hm.UltraheatReader(args.port))
response_data = heat_meter_service.read()

print('model :',heat_meter.model)
print('GJ :',heat_meter.heat_usage_gj)  # UH50 
print('MWh :',heat_meter.heat_usage_mwh)  # T550 
print('m3 :',heat_meter.volume_usage_m3)
etc..

```
## Full list of available data
- heat_usage_gj (empty for T550)
- heat_usage_mwh (empty for UH50)
- volume_usage_m3
- ownership_number
- volume_previous_year_m3
- heat_previous_year_gj (empty for T550)
- heat_previous_year_mwh (empty for UH50)
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