from datetime import datetime
import os
import unittest
from unittest.mock import patch
from ultraheat_api import FileReader, UltraheatReader, HeatMeterService

DUMMY_FILE = 'LUGCUH50_dummy_utf8_kwh.txt'
DUMMY_PORT = 'DUMMY'
path = os.path.abspath(os.path.dirname(__file__))
dummy_file_path = os.path.join(path, DUMMY_FILE)

# Create a list from the dummy file to use as mock for reading the port
with open(dummy_file_path, "rb") as f:
    mock_readline = f.read().splitlines(keepends=True)

class HeatMeterTest(unittest.TestCase):

    def assert_response_data(self, response_data):
        # check the response dummy data 
        self.assertEqual('LUGCUH50', response_data.model)
        self.assertEqual(71.813, response_data.heat_usage_mwh)
        self.assertEqual(1084.58, response_data.volume_usage_m3)
        self.assertEqual(59.059, response_data.heat_previous_year_mwh)

    def test_heat_meter_read_file(self):
        heat_meter_service = HeatMeterService(
            FileReader(dummy_file_path)
        )
        response_data = heat_meter_service.read()
        self.assert_response_data(response_data)

if __name__ == '__main__':
    unittest.main()
