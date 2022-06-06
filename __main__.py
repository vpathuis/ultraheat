import argparse, sys
from pprint import pprint
import os
import sys
from uh50_api.find_ports import find_ports
from uh50_api.service import HeatMeterService
from uh50_api.file_reader import FileReader
from uh50_api.uh50_reader import UH50Reader

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

    return parser.parse_args()


args = parse_arguments()
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
        file_name = os.path.join(path, "tests", "LUGCUH50_dummy.txt")
    else:
        file_name = args.file
    reader = FileReader(file_name)

elif args.port:
    print(
        "WARNING: everytime the UH50-unit is read, battery time of the UH50 will go down by about 30 minutes!"
    )
    print("Reading ... this will take some time...")
    reader = UH50Reader(args.port)
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
