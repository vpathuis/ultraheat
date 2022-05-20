from datetime import datetime
import unittest
from uh50_api.uh50 import (UH50)
import serial


class UH50Test(unittest.TestCase):

    def test_update_dummy(self):
        heat_meter = UH50('test')
        heat_meter.update_dummy()      
        self.assertRegex(heat_meter.heat_usage_gj, r'^999.\d{3}$')
        self.assertRegex(heat_meter.volume_usage_m3, r'^9999.\d{2}$')
        self.assertEqual('LUGCUH50', heat_meter.model)

    def test_validate_fail(self):
        heat_meter = UH50('non-existing-port')
        with self.assertRaises(serial.serialutil.SerialException):
            _ = heat_meter.validate()

    def test_connect_fail(self):
        heat_meter = UH50('non-existing-port')
        with self.assertRaises(serial.serialutil.SerialException):
            _ = heat_meter._connect_serial()

    def test_update_fail(self):
        heat_meter = UH50('non-existing-port')
        with self.assertRaises(serial.serialutil.SerialException):
            _ = heat_meter.update()

    def test_search_response(self):
        f = open('tests/dummy_response.txt')
        dummy_response = f.readlines()
        f.close()
        heat_meter = UH50('dummy')
        heat_meter._search_response(dummy_response)
        self.assertEqual(328.871, heat_meter.heat_usage_gj)
        self.assertEqual(3329.67, heat_meter.volume_usage_m3)
        self.assertEqual('66153690', heat_meter.ownership_number)
        self.assertEqual(3188.07, heat_meter.volume_previous_year_m3)
        self.assertEqual(314.658, heat_meter.heat_previous_year_gj)
        self.assertEqual('0', heat_meter.error_number)
        self.assertEqual('66153690', heat_meter.device_number)
        self.assertEqual(60, heat_meter.measurement_period_minutes)
        self.assertEqual(22.4, heat_meter.power_max_kw)
        self.assertEqual(22.4, heat_meter.power_max_previous_year_kw)
        self.assertEqual(0.744, heat_meter.flowrate_max_m3ph)
        self.assertEqual(98.5, heat_meter.flow_temperature_max_c)
        self.assertEqual(96.1, heat_meter.return_temperature_max_c)
        self.assertEqual(107988, heat_meter.operating_hours)
        self.assertEqual(5, heat_meter.fault_hours)
        self.assertEqual(5, heat_meter.fault_hours_previous_year)
        self.assertEqual('01-01&00:00', heat_meter.yearly_set_day)
        self.assertEqual(0.744, heat_meter.flowrate_max_previous_year_m3ph)
        self.assertEqual(98.5, heat_meter.flow_temperature_max_previous_year_c)
        self.assertEqual(96.1, heat_meter.return_temperature_max_previous_year_c)
        self.assertEqual('01&00:00', heat_meter.monthly_set_day)
        self.assertEqual(datetime(2022,5,19,19,41,17), heat_meter.meter_date_time)
        self.assertEqual(1.5, heat_meter.measuring_range_m3ph)
        self.assertEqual('0&1&0&0000&CECV&CECV&1&5.16&5.16&F&101008&040404&08&0', heat_meter.settings_and_firmware)
        self.assertEqual(28849, heat_meter.flow_hours)

    def test_read_data_not_found(self):
        heat_meter = UH50('dummy')
        with self.assertRaises(Exception) as cm:
            _ = heat_meter._search_data(['6.8(0255.987*XX)6.26(02458.16*YY)9.21(66153690)', \
                                '6.26*01(02196.39*m3)6.8*01(0233.431*GJ)', \
                                'F(0)9.20(66153690)6.35(60*m)', \
                                '6.6(0022.4*kW)6.6*01(0022.4*kW)6.33(000.708*m3ph)9.4(098.5*C&096.1*C)',])
        self.assertEqual('GJ and m3 values not found', str(cm.exception))

