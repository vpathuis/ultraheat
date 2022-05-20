# UH50 Python package
This module reads from the Landys & Gyr UH50 heat measuring unit and returns the current GJ and m3 meters.
Note: An (USB) IR reader is needed and connected to the machine running the python script

WARNING: everytime this is called, battery time of the UH50 will go down by about 30 minutes!
This package has been tested with the Landys & Gyr UH50 type LUGCUH50. Other models are likely to work as well.

## Using the python integration

To use the module as a script, call the module directly (uh50_api.uh50) and follow the instructions through the command line. This requires access to the serial ports and might only works as root.

To use the module as an API:
```python
import uh50_api

# check available ports
ports = uh50_api.find_ports() 
for p in ports:
    print(p.device)
print(len(ports), 'ports found')

# read the device
heat_meter = uh50_api.UH50(port) # eg UH50('/dev/ttyUSB0') or UH50('COM5')
heat_meter.update() 
print('GJ :',heat_meter.heat_usage_gj)
print('m3 :',heat_meter.volume_usage_m3)
print('model :',heat_meter.model)


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