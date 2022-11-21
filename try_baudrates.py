"""This is a program for try several baudrates to try and find one that works for this particular device """
import argparse
import logging
from pprint import pprint

from ultraheat_api import HeatMeterService, UltraheatReader

WAKE_UP_BAUDRATES = [50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 9600, 19200, 38400, 57600, 115200]
DATA_STREAM_BAUDRATES = [2400, 9600, 38400 or 115200]

logging.basicConfig(level="DEBUG")
_LOGGER = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument(
    "--port",
    help="Choose port mode, supply the port name, eg. '/dev/ttyUSB0' or 'COM5'",
)

args = parser.parse_args()

if not args.port:
    parser.print_help()
    exit()

for wake_up_baudrate in WAKE_UP_BAUDRATES:
    for data_stream_baudrate in DATA_STREAM_BAUDRATES:
        _LOGGER.debug("***********TRYING WAKE UP: %s and DATA STREAM: %s ***********", wake_up_baudrate, data_stream_baudrate)
        reader = UltraheatReader(args.port, wake_up_baudrate, data_stream_baudrate)
        heat_meter_service = HeatMeterService(reader)
        response_data = heat_meter_service.read()
        pprint(response_data)
