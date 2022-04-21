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

uh50_api.findports()  # to check available ports

heat_meter = UH50(port) # eg UH50('/dev/ttyUSB0') or UH50('COM5')
heat_meter.update() 
print('GJ :',heat_meter.gj)
print('m3 :',heat_meter.m3)
print('model :',heat_meter.model)
print('full response :',heat_meter.full_response)

```