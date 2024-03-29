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
- raw_response

## Telegram parsing
The telegram that is read from the Heat Meter is parsed as follows. 
For the UH50 (shown below) GJ is parsed. For the T550 this will be MWh.

6.8(**heat_usage_gj**\*GJ)6.26(**volume_usage_m3**\*m3)9.21(**ownership_number**)  
6.26\*01(**volume_previous_year_m3**\*m3)6.8\*01(**heat_previous_year_gj**\*GJ)  
F(**error_number**)9.20(**device_number**)6.35(**measurement_period_minutes**\*m)  
6.6(**power_max_kw**\*kW)6.6\*01(**power_max_previous_year_kw**\*kW)6.33(**flowrate_max_m3ph**\*m3ph)9.4(**flow_temperature_max_c**\*C&**return_temperature_max_c**\*C)  
6.31(**operating_hours**\*h)6.32(**fault_hours**\*h)9.22(R)9.6(000&66153690&0&000&66153690&0)  
9.7(20000)6.32\*01(**fault_hours_previous_year**\*h)6.36(**yearly_set_day**)6.33\*01(**flowrate_max_previous_year_m3ph**\*m3ph)  
6.8.1()6.8.2()6.8.3()6.8.4()6.8.5()  
6.8.1\*01()6.8.2\*01()6.8.3\*01()  
6.8.4\*01()6.8.5\*01()  
9.4\*01(**flow_temperature_max_previous_year_c**\*C&**return_temperature_max_previous_year_c**\*C)  
6.36.1(2018-03-03)6.36.1\*01(2018-03-03)  
6.36.2(2020-06-23)6.36.2\*01(2020-06-23)  
6.36.3(2012-02-03)6.36.3\*01(2012-02-03)  
6.36.4(2017-01-18)6.36.4\*01(2017-01-18)  
6.36.5()6.36\*02(**monthly_set_day**)9.36(**meter_date_time**)9.24(**measuring_range_m3ph**\*m3ph)  
9.17(0)9.18()9.19()9.25()  
9.1(**settings_and_firmware**)  
9.2(&&)9.29()9.31(**flow_hours**\*h)  
9.0.1(00000000)9.0.2(00000000)9.34.1(000.00000\*m3)9.34.2(000.00000\*m3)  
8.26.1(00000000\*m3)8.26.2(00000000\*m3)  
8.26.1\*01(00000000\*m3)8.26.2\*01(00000000\*m3)    
6.26.1()6.26.4()6.26.5()  
6.26.1\*01()6.26.4\*01()6.26.5\*01()0.0(66153690)  
!
