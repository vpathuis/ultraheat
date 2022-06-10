from datetime import datetime
import os
import unittest
from unittest.mock import patch
from landisgyr_ultraheat_api import FileReader, UltraheatReader, HeatMeterService


DUMMY_FILE = 'LUGCUH50_dummy_utf8.txt'
DUMMY_FILE_ERROR = 'LUGCUH50_dummy_error_utf8.txt'
DUMMY_PORT = 'DUMMY'
path = os.path.abspath(os.path.dirname(__file__))
dummy_file_path = os.path.join(path,DUMMY_FILE)
dummy_file_path_error = os.path.join(path,DUMMY_FILE_ERROR)

# Create a list from the dummy file to use as mock for reading the port
with open(dummy_file_path, "rb") as f:
    mock_readline = f.read().splitlines()

class HeatMeterTest(unittest.TestCase):

    def assert_response_data(self, response_data):
        # check the response dummy data 
        self.assertEqual(328.871, response_data.heat_usage_gj['value'])
        self.assertEqual(3329.67, response_data.volume_usage_m3['value'])
        self.assertEqual('66153690', response_data.ownership_number['value'])
        self.assertEqual(3188.07, response_data.volume_previous_year_m3['value'])
        self.assertEqual(314.658, response_data.heat_previous_year_gj['value'])
        self.assertEqual('0', response_data.error_number['value'])
        self.assertEqual('66153690', response_data.device_number['value'])
        self.assertEqual(60, response_data.measurement_period_minutes['value'])
        self.assertEqual(22.4, response_data.power_max_kw['value'])
        self.assertEqual(22.4, response_data.power_max_previous_year_kw['value'])
        self.assertEqual(0.744, response_data.flowrate_max_m3ph['value'])
        self.assertEqual(98.5, response_data.flow_temperature_max_c['value'])
        self.assertEqual(96.1, response_data.return_temperature_max_c['value'])
        self.assertEqual(107988, response_data.operating_hours['value'])
        self.assertEqual(5, response_data.fault_hours['value'])
        self.assertEqual(5, response_data.fault_hours_previous_year['value'])
        self.assertEqual('01-01 00:00', response_data.yearly_set_day['value'])
        self.assertEqual(0.744, response_data.flowrate_max_previous_year_m3ph['value'])
        self.assertEqual(
            98.5, response_data.flow_temperature_max_previous_year_c['value'])
        self.assertEqual(
            96.1, response_data.return_temperature_max_previous_year_c['value'])
        self.assertEqual('01 00:00', response_data.monthly_set_day['value'])
        self.assertEqual(datetime(2022, 5, 19, 19, 41, 17),
                         response_data.meter_date_time['value'])
        self.assertEqual(1.5, response_data.measuring_range_m3ph['value'])
        self.assertEqual('0 1 0 0000 CECV CECV 1 5.16 5.16 F 101008 040404 08 0',
                         response_data.settings_and_firmware['value'])
        self.assertEqual(28849, response_data.flow_hours['value'])

    @patch('landisgyr_ultraheat_api.ultraheat_reader.Serial')
    def test_validate_port(self, mock_Serial):
        mock_Serial().__enter__().readline.side_effect = mock_readline
        reader = UltraheatReader(DUMMY_PORT)

        heat_meter_service = HeatMeterService(reader)
        self.assertEqual('LUGCUH50', heat_meter_service.validate())

    @patch('landisgyr_ultraheat_api.ultraheat_reader.Serial')
    def test_read_port(self, mock_Serial):
        mock_Serial().__enter__().readline.side_effect = mock_readline
        reader = UltraheatReader(DUMMY_PORT)

        heat_meter_service = HeatMeterService(reader)
        response_data = heat_meter_service.read()
        self.assert_response_data(response_data)


    def test_validate_file(self):
        reader = FileReader(dummy_file_path)

        heat_meter_service = HeatMeterService(reader)
        self.assertEqual('LUGCUH50', heat_meter_service.validate())

    def test_heat_meter_read_file(self):
        heat_meter_service = HeatMeterService(
            FileReader(dummy_file_path)
        )
        response_data = heat_meter_service.read()
        self.assert_response_data(response_data)

    def test_heat_meter_read_file_conversion_error(self):
        heat_meter_service: HeatMeterService = HeatMeterService(
            FileReader(dummy_file_path_error))
        with self.assertRaises(ValueError):
            _ = heat_meter_service.read()

if __name__ == '__main__':
    unittest.main()