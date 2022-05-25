from datetime import datetime
import os
import unittest
from uh50_api import *


DUMMY_FILE = 'LUGCUH50_dummy.txt'
DUMMY_FILE_ERROR = 'LUGCUH50_dummy_error.txt'
path = os.path.abspath(os.path.dirname(__file__))
dummy_file_path = os.path.join(path,DUMMY_FILE)
dummy_file_path_error = os.path.join(path,DUMMY_FILE_ERROR)


class UH50Test(unittest.TestCase):

    def test_validate(self):
        reader = FileReader(dummy_file_path)

        heat_meter_service = HeatMeterService(reader)
        self.assertEqual('LUGCUH50', heat_meter_service.validate())

    def test_heat_meter_read_file(self):
        file_name = 'tests/LUGCUH50_dummy.txt'
        heat_meter_service: HeatMeterService = HeatMeterService(
            FileReader(file_name))
        response_data = HeatMeterResponse(heat_meter_service.read())
        self.assertEqual(328.871, response_data.heat_usage_gj)
        self.assertEqual(3329.67, response_data.volume_usage_m3)
        self.assertEqual('66153690', response_data.ownership_number)
        self.assertEqual(3188.07, response_data.volume_previous_year_m3)
        self.assertEqual(314.658, response_data.heat_previous_year_gj)
        self.assertEqual('0', response_data.error_number)
        self.assertEqual('66153690', response_data.device_number)
        self.assertEqual(60, response_data.measurement_period_minutes)
        self.assertEqual(22.4, response_data.power_max_kw)
        self.assertEqual(22.4, response_data.power_max_previous_year_kw)
        self.assertEqual(0.744, response_data.flowrate_max_m3ph)
        self.assertEqual(98.5, response_data.flow_temperature_max_c)
        self.assertEqual(96.1, response_data.return_temperature_max_c)
        self.assertEqual(107988, response_data.operating_hours)
        self.assertEqual(5, response_data.fault_hours)
        self.assertEqual(5, response_data.fault_hours_previous_year)
        self.assertEqual('01-01&00:00', response_data.yearly_set_day)
        self.assertEqual(0.744, response_data.flowrate_max_previous_year_m3ph)
        self.assertEqual(
            98.5, response_data.flow_temperature_max_previous_year_c)
        self.assertEqual(
            96.1, response_data.return_temperature_max_previous_year_c)
        self.assertEqual('01&00:00', response_data.monthly_set_day)
        self.assertEqual(datetime(2022, 5, 19, 19, 41, 17),
                         response_data.meter_date_time)
        self.assertEqual(1.5, response_data.measuring_range_m3ph)
        self.assertEqual('0&1&0&0000&CECV&CECV&1&5.16&5.16&F&101008&040404&08&0',
                         response_data.settings_and_firmware)
        self.assertEqual(28849, response_data.flow_hours)


    def test_heat_meter_read_file_conversion_error(self):
        file_name = 'tests/LUGCUH50_dummy_error.txt'
        heat_meter_service: HeatMeterService = HeatMeterService(
            FileReader(file_name))
        reponse_data = HeatMeterResponse(heat_meter_service.read())
        with self.assertRaises(ValueError):
            _ = reponse_data.heat_usage_gj
