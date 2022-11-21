import argparse
import logging
from pprint import pprint
import os
from ultraheat_api.find_ports import find_ports
from ultraheat_api.service import HeatMeterService
from ultraheat_api.file_reader import FileReader
from ultraheat_api.ultraheat_reader import UltraheatReader

parser = argparse.ArgumentParser()


def parse_arguments():

    parser.add_argument(
        "--file", help="Choose file mode and supply the filename or type default"
    )
    parser.add_argument("--ports", help="Show available ports", action="store_true")
    parser.add_argument(
        "--port",
        help="Choose port mode, supply the port name, eg. '/dev/ttyUSB0' or 'COM5'",
    )
    parser.add_argument(
        "--validate",
        help="Choose validate mode. Combine with --file or --port",
        action="store_true",
    )

    parser.add_argument(
        "--log",
        help="Choose log level DEBUG, INFO, WARNING or ERROR",
    )

    parser.add_argument(
        "--brw",
        help="Set the baudrate for waking up the default. Defaults to 300",
    )

    parser.add_argument(
        "--brd",
        help="Set the baudrate for reading the datastream. Defaults to 2400",
    )

    return parser.parse_args()


args = parse_arguments()
if args.log:
    logging.basicConfig(level=args.log)

if args.ports:
    print("showing available ports: ")
    ports = find_ports()
    for p in ports:
        print(p.device)
    print(len(ports), "ports found")
    exit()

if args.file:
    if args.file == "default":
        print("Using default dummy file")
        path = os.path.abspath(os.path.dirname(__file__))
        file_name = os.path.join(path, "tests", "LUGCUH50_dummy_utf8.txt")
    else:
        file_name = args.file
    reader = FileReader(file_name)

elif args.port:
    print(
        "WARNING: everytime the unit is read, battery time will go down by about 30 minutes!"
    )
    print("Reading ... this will take some time...")
    baudrate_wake_up = None
    baudrate_data_stream = None
    if args.brw:
        baudrate_wake_up = args.brw
    if args.brd:
        baudrate_data_stream = args.brd
    reader = UltraheatReader(args.port, baudrate_wake_up, baudrate_data_stream)
else:
    parser.print_help()
    exit()

heat_meter_service = HeatMeterService(reader)

if args.validate:
    model = heat_meter_service.validate()
    print("model: " + model)
else:
    response_data = heat_meter_service.read()
    pprint(response_data)
