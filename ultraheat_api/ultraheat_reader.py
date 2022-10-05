""" 
Reads raw response data from the Ultraheat unit. 
To test the connection use validate, which will return the model name.
"""
import logging
from typing import Tuple

import serial
from serial import Serial

_LOGGER = logging.getLogger(__name__)

MAX_LINES_ULTRAHEAT_REPONSE = 26


class UltraheatReader:
    def __init__(self, port) -> None:
        _LOGGER.debug("Initializing UltraheatReader on port: %s", port)
        self._port = port

    def read(self):
        """Reads the device on the specified port, returning the full string"""
        with self._connect_serial() as conn:
            return self._get_data(conn)

    def _connect_serial(self) -> Serial:
        """Make the connection to the serial device"""
        return Serial(
            self._port,
            baudrate=300,
            bytesize=serial.SEVENBITS,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_TWO,
            timeout=5,
            xonxoff=0,
            rtscts=0,
        )

    def _wake_up(self, conn) -> str:
        """Wake up the device and get the model number. Waking up should be done at 300 baud."""
        # Sending /?!
        _LOGGER.debug("Waking up Ultraheat")
        conn.write(
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x2F\x3F\x21\x0D\x0A"
        )

        # checking if we can read the model (eg. 'LUGCUH50')
        model = conn.readline().decode("utf-8")[1:9]
        if model:
            _LOGGER.debug("Got model %s", model)
        else:
            _LOGGER.error("No model could be read")
            raise Exception("No model could be read")

        return model

    def _get_data(self, conn) -> tuple[str, str]:
        model = self._wake_up(conn)
        _LOGGER.debug("Receiving data")
        # Now switch to 2400 BAUD. This could be different for other models. Let me know if you experience problems.
        conn.baudrate = 2400
        ir_lines = ""
        ir_line = ""
        iteration = 0
        # reading all lines (typically 25 lines)
        while "!" not in ir_line and iteration < MAX_LINES_ULTRAHEAT_REPONSE:
            iteration += 1
            ir_line = conn.readline().decode("utf-8")
            ir_lines += ir_line

        _LOGGER.debug("Read %s lines of data", iteration)
        return model, str(ir_lines)
