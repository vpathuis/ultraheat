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

result = uh50_api.read_uh50('port')  # eg uh50.read_uh50('/dev/ttyUSB0') or uh50.read_uh50('COM5')
print('GJ :',result['gj'])
print('m3 :',result['m3'])
print('model :',result['model'])
print('full response :',result['full_response'])

```