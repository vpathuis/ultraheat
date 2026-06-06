"""
Reads raw response data from the Ultraheat unit.
To test the connection use validate, which will return the model name.
"""

import logging

from .const import (
    DEFAULT_BAUDRATE_DATA_STREAM,
    DEFAULT_BAUDRATE_WAKE_UP,
    DEFAULT_TIMEOUT,
)
import serialx
import time


_LOGGER = logging.getLogger(__name__)

MAX_LINES_ULTRAHEAT_RESPONSE = 26


class UltraheatReader:
    def __init__(
        self,
        port,
        baudrate_wake_up=DEFAULT_BAUDRATE_WAKE_UP,
        baudrate_data_stream=DEFAULT_BAUDRATE_DATA_STREAM,
        timeout=DEFAULT_TIMEOUT,
    ) -> None:
        _LOGGER.debug("Initializing UltraheatReader on port: %s", port)
        self._port = port
        self.baudrate_wake_up = baudrate_wake_up
        self.baudrate_data_stream = baudrate_data_stream
        self.timeout = timeout

    def read(self):
        """Reads the device on the specified port, returning the full string"""
        with self._connect_serial() as conn:
            return self._get_data(conn)

    def _connect_serial(self):
        """Make the connection to the serial device"""
        return serialx.serial_for_url(
            self._port,
            baudrate=self.baudrate_wake_up,
            byte_size=7,
            parity=serialx.Parity.EVEN,
            stopbits=serialx.StopBits.TWO,
            read_timeout=self.timeout,
            xonxoff=0,
            rtscts=0,
        )

    def _wake_up(self, conn) -> str:
        """Wake up the device and get the model number. Waking up should be done at 300 baud."""
        _LOGGER.debug("Waking up Ultraheat")
        conn.write(
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x2f\x3f\x21\x0d\x0a"
        )

        _LOGGER.debug("Reading model at baudrate %s", self.baudrate_wake_up)
        data = b""
        for _ in range(5):
            start_time = time.time()
            data = conn.readline()
            elapsed_time = time.time() - start_time
            _LOGGER.debug("Got: %s. This took %s seconds", data, elapsed_time)

            if data.startswith(b"/") and len(data) > 3 and data[1:2] != b"?":
                break
            _LOGGER.debug("Skipping echo or non-identification line: %s", data)

        model = data.decode("utf-8", errors="replace")[1:9]
        if model and not all(c == "\x00" for c in model):
            _LOGGER.debug("Got model %s", model)
        else:
            _LOGGER.error("No model could be read")
            raise Exception("No model could be read")

        return model

    def _get_data(self, conn) -> tuple[str, str]:
        model = self._wake_up(conn)
        _LOGGER.debug(
            "Reading data at baudrate %s. %s bytes in buffer",
            self.baudrate_data_stream,
            conn.num_unread_bytes(),
        )
        # Now switch to 2400 BAUD. This could be different for other models. Let me know if you experience problems.
        conn.baudrate = self.baudrate_data_stream
        ir_lines = ""
        ir_line = ""
        iteration = 0
        # reading all lines (typically 25 lines)
        while "!" not in ir_line and iteration < MAX_LINES_ULTRAHEAT_RESPONSE:
            iteration += 1
            start_time = time.time()
            data = conn.readline()
            elapsed_time = time.time() - start_time

            if len(data) == 0:
                _LOGGER.debug(
                    "No data received after %s seconds. Empty data usually implies timeout on serial read. Stopping after %s lines of data",
                    elapsed_time,
                    iteration,
                )
                break

            _LOGGER.debug(
                "Reading line # %s. Got: %s. This took %s seconds. %s bytes left in buffer.",
                iteration,
                data,
                elapsed_time,
                conn.num_unread_bytes(),
            )
            ir_line = data.decode("utf-8")
            _LOGGER.debug("After decoding: `%s`", ir_line)
            ir_lines += ir_line

        _LOGGER.debug("Finished reading %s lines of data", iteration)
        return model, str(ir_lines)
