from datetime import datetime
import unittest
from uh50_api import *
import serial


class UH50Test(unittest.TestCase):

    # def test_update_dummy(self):
    #     heat_meter = HeatMeterService('test')
    #     heat_meter.update_dummy()
    #     self.assertRegex(heat_meter.heat_usage_gj, r'^999.\d{3}$')
    #     self.assertRegex(heat_meter.volume_usage_m3, r'^9999.\d{2}$')
    #     self.assertEqual('LUGCUH50', heat_meter.model)

    # def test_validate_fail(self):
    #     heat_meter = HeatMeterService('non-existing-port')
    #     with self.assertRaises(serial.serialutil.SerialException):
    #         _ = heat_meter.validate()

    # def test_connect_fail(self):
    #     heat_meter = HeatMeterService('non-existing-port')
    #     with self.assertRaises(serial.serialutil.SerialException):
    #         _ = heat_meter._connect_serial()

    # def test_update_fail(self):
    #     heat_meter = HeatMeterService('non-existing-port')
    #     with self.assertRaises(serial.serialutil.SerialException):
    #         _ = heat_meter.update()

    def test_heat_meter_read_file(self):
        file_name = 'tests/dummy_response.txt'
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
        file_name = 'tests/dummy_response_error.txt'
        heat_meter_service: HeatMeterService = HeatMeterService(
            FileReader(file_name))
        reponse_data = HeatMeterResponse(heat_meter_service.read())
        with self.assertRaises(ValueError):
            _ = reponse_data.heat_usage_gj



    # def test_read_data_not_found(self):
    #     heat_meter = HeatMeterService('dummy')
    #     with self.assertRaises(Exception) as cm:
    #         _ = heat_meter._search_data(['6.8(0255.987*XX)6.26(02458.16*YY)9.21(66153690)', \
    #                             '6.26*01(02196.39*m3)6.8*01(0233.431*GJ)', \
    #                             'F(0)9.20(66153690)6.35(60*m)', \
    #                             '6.6(0022.4*kW)6.6*01(0022.4*kW)6.33(000.708*m3ph)9.4(098.5*C&096.1*C)',])
    #     self.assertEqual('GJ and m3 values not found', str(cm.exception))
