from datetime import datetime
import os
import unittest
from unittest.mock import patch
from ultraheat_api import FileReader, UltraheatReader, HeatMeterService

DUMMY_FILE = 'LGUHT550_dummy_utf8.txt'
DUMMY_FILE_ERROR = 'LGUHT550_dummy_error_utf8.txt'
DUMMY_PORT = 'DUMMY'
path = os.path.abspath(os.path.dirname(__file__))
dummy_file_path = os.path.join(path, DUMMY_FILE)
dummy_file_path_error = os.path.join(path, DUMMY_FILE_ERROR)

# Create a list from the dummy file to use as mock for reading the port
with open(dummy_file_path, "rb") as f:
    mock_readline = f.read().splitlines(keepends=True)


class HeatMeterTest(unittest.TestCase):

    def assert_response_data(self, response_data):
        # check the response dummy data 
        self.assertEqual('LUGCUH50', response_data.model)
        self.assertEqual(326.062, response_data.heat_usage_mwh)
        self.assertEqual(7939.56, response_data.volume_usage_m3)
        self.assertEqual('00073600', response_data.ownership_number)
        self.assertEqual(7843.48, response_data.volume_previous_year_m3)
        self.assertEqual(323.272, response_data.heat_previous_year_mwh)
        self.assertEqual('0', response_data.error_number)
        self.assertEqual('66935074', response_data.device_number)
        self.assertEqual(60, response_data.measurement_period_minutes)
        self.assertEqual(28.0, response_data.power_max_kw)
        self.assertEqual(28.0, response_data.power_max_previous_year_kw)
        self.assertEqual(0.840, response_data.flowrate_max_m3ph)
        self.assertEqual(108.5, response_data.flow_temperature_max_c)
        self.assertEqual(88.1, response_data.return_temperature_max_c)
        self.assertEqual(88324, response_data.operating_hours)
        self.assertEqual(1, response_data.fault_hours)
        self.assertEqual(1, response_data.fault_hours_previous_year)
        self.assertEqual('01-01 00:00', response_data.yearly_set_day)
        self.assertEqual(0.840, response_data.flowrate_max_previous_year_m3ph)
        self.assertEqual(
            108.5, response_data.flow_temperature_max_previous_year_c)
        self.assertEqual(
            88.1, response_data.return_temperature_max_previous_year_c)
        self.assertEqual('01 00:00', response_data.monthly_set_day)
        self.assertEqual(datetime(2022, 6, 8, 10, 6, 51),
                         response_data.meter_date_time)
        self.assertEqual(1.5, response_data.measuring_range_m3ph)
        self.assertEqual('0 1 0 0017 CECV CECV 1 5.19 5.19 F 081008 040404 08 0 00 ?:',
                         response_data.settings_and_firmware)
        self.assertEqual(59615, response_data.flow_hours)

    @patch('ultraheat_api.ultraheat_reader.Serial')
    def test_read_port(self, mock_Serial):
        mock_Serial().__enter__().readline.side_effect = mock_readline
        reader = UltraheatReader(DUMMY_PORT)

        heat_meter_service = HeatMeterService(reader)
        response_data = heat_meter_service.read()
        self.assert_response_data(response_data)

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
