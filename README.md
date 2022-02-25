This module reads from the Landys & Gyr UH50 heat measuring unit and returns the currect GJ and m3 meters.
WARNING: everytime this is called, battery time of the UH50 will go down by about 30 minutes!

Usage: read_uh50(port), eg read_uh50('/dev/ttyUSB0') or read_uh50('COM5')

Calling the module directly will allow for usage through command lime