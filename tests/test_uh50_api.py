import unittest
from uh50_api.uh50 import (UH50)
import serial


class UH50Test(unittest.TestCase):

    def test_update_dummy(self):
        heat_meter = UH50('test')
        heat_meter.update_dummy()      
        self.assertEqual('123.456', heat_meter.gj)
        self.assertEqual('1234.56', heat_meter.m3)
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

    def test_search_data_list(self):
        heat_meter = UH50('dummy')
        gj, m3 = heat_meter._search_data(['6.8(0255.987*GJ)6.26(02458.16*m3)9.21(66153690)', \
                            '6.26*01(02196.39*m3)6.8*01(0233.431*GJ)', \
                            'F(0)9.20(66153690)6.35(60*m)', \
                            '6.6(0022.4*kW)6.6*01(0022.4*kW)6.33(000.708*m3ph)9.4(098.5*C&096.1*C)',])
        self.assertEqual('0255.987', gj)
        self.assertEqual('02458.16', m3)

    def test_search_data_str(self):
        heat_meter = UH50('dummy')
        gj, m3 = heat_meter._search_data('6.8(0255.987*GJ)6.26(02458.16*m3)9.21(66153690)')
        self.assertEqual('0255.987', gj)
        self.assertEqual('02458.16', m3)

    def test_read_data_not_found(self):
        heat_meter = UH50('dummy')
        with self.assertRaises(Exception) as cm:
            _ = heat_meter._search_data(['6.8(0255.987*XX)6.26(02458.16*YY)9.21(66153690)', \
                                '6.26*01(02196.39*m3)6.8*01(0233.431*GJ)', \
                                'F(0)9.20(66153690)6.35(60*m)', \
                                '6.6(0022.4*kW)6.6*01(0022.4*kW)6.33(000.708*m3ph)9.4(098.5*C&096.1*C)',])
        self.assertEqual('GJ and m3 values not found', str(cm.exception))

