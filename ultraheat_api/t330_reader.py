"""
Reader for Landis+Gyr T330 over optical M-Bus, following the proven perl flow.

Assumptions impacting behavior:
- Serial params: start at 2400 baud, 8E1; after short-frame speed switch, read at 9600 baud, 8E1.
- Timing: conservative sleeps and limited retries similar to the perl script. Too-aggressive polling may yield no response.
- We only collect a short burst of frames (~2 seconds) after switching to 9600. Users with slow meters may need to increase timeout.

This reader returns (model, raw_bytes). The model is set to "T330".
"""
import logging
import time
from typing import Tuple

import serial
from serial import Serial

_LOGGER = logging.getLogger(__name__)


class T330Reader:
    def __init__(
        self,
        port: str,
        timeout: float = 2.0,
        retries: int = 3,
    ) -> None:
        self._port = port
        self.timeout = timeout
        self.retries = retries

    def read(self) -> Tuple[str, bytes]:
        with self._connect_serial(baudrate=2400) as conn:
            self._sequence_1(conn)
            self._sequence_2(conn)
            self._sequence_3(conn)
            raw_bytes = self._sequence_5_and_read(conn)
        return "T330", raw_bytes

    def _connect_serial(self, baudrate: int) -> Serial:
        return Serial(
            self._port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_ONE,
            timeout=self.timeout,
            xonxoff=0,
            rtscts=0,
        )

    def _write_and_read(self, conn: Serial, payload: bytes, read_size: int, tries: int) -> bytes:
        for attempt in range(tries):
            _LOGGER.debug("T330: sending %d bytes (attempt %s/%s): %s", len(payload), attempt + 1, tries, payload.hex())
            conn.reset_input_buffer()
            conn.reset_output_buffer()
            written = conn.write(payload)
            if written != len(payload):
                _LOGGER.debug("T330: partial write %s/%s", written, len(payload))
            conn.flush()
            _LOGGER.debug("T330: waiting for response (max %d bytes)", read_size)
            data = conn.read(read_size)
            if data:
                _LOGGER.debug("T330: received %d bytes: %s", len(data), data.hex())
                return data
            else:
                _LOGGER.debug("T330: no response received")
            # backoff between retries
            time.sleep(0.3)
        _LOGGER.debug("T330: exhausted %d attempts, no response", tries)
        return b""

    def _sequence_1(self, conn: Serial) -> None:
        # Long frame: "Read version string" (CI 0x51) as in perl rd_t330.pl
        seq = bytes(
            [
                # a lot of leading zeros were used; they are not required electrically, keep minimal
                0x68, 0x05, 0x05, 0x68, 0x73, 0xFE, 0x51, 0x0F, 0x0F, 0xE0, 0x16,
            ]
        )
        _LOGGER.debug("T330: sequence 1 - read version string")
        resp = self._write_and_read(conn, seq, read_size=50, tries=self.retries)
        if resp:
            _LOGGER.debug("T330: sequence 1 response: %s", resp)
        else:
            _LOGGER.debug("T330: sequence 1 - no response")
        # Do not strictly require matching ASCII pattern; meters differ. Proceed if any response observed.

    def _sequence_2(self, conn: Serial) -> None:
        # Application reset (CI 0x50), expect single-char 0xE5 within small response
        seq = bytes([0x68, 0x04, 0x04, 0x68, 0x53, 0xFE, 0x50, 0x00, 0xA1, 0x16])
        _LOGGER.debug("T330: sequence 2 - application reset")
        resp = self._write_and_read(conn, seq, read_size=50, tries=self.retries)
        if resp:
            _LOGGER.debug("T330: sequence 2 response: %s", resp)
        if b"\xE5" not in resp:
            _LOGGER.debug("T330: sequence 2 did not return E5 ack; continuing regardless")

    def _sequence_3(self, conn: Serial) -> None:
        # SND_UD with payload 0x0F,0x70,0x00,0x01 (per perl)
        seq = bytes(
            [
                0x68,
                0x07,
                0x07,
                0x68,
                0x73,
                0xFE,
                0x51,
                0x0F,
                0x70,
                0x00,
                0x01,
                0x42,
                0x16,
            ]
        )
        _LOGGER.debug("T330: sequence 3 - SND_UD with payload")
        resp = self._write_and_read(conn, seq, read_size=50, tries=2)
        if resp:
            _LOGGER.debug("T330: sequence 3 response: %s", resp)
        else:
            _LOGGER.debug("T330: sequence 3 - no response")

    def _sequence_5_and_read(self, conn: Serial) -> bytes:
        # Short frame to switch baud to 9600, then reconfigure port and read a burst
        # Captured working frame from perl: 0x10, 0x7C, 0xFE, 0x7A, 0x16
        seq = bytes([0x10, 0x7C, 0xFE, 0x7A, 0x16])
        _LOGGER.debug("T330: sequence 5 - short frame to switch baud to 9600")
        resp = self._write_and_read(conn, seq, read_size=5, tries=1)
        if resp:
            _LOGGER.debug("T330: sequence 5 response: %s", resp)
        # Allow meter to switch
        _LOGGER.debug("T330: waiting 1.5s for meter to switch baudrate")
        time.sleep(1.5)
        # Switch local UART to 9600
        _LOGGER.debug("T330: switching local UART to 9600 baud, 8E1")
        conn.baudrate = 9600
        conn.bytesize = serial.EIGHTBITS
        conn.parity = serial.PARITY_EVEN
        conn.stopbits = serial.STOPBITS_ONE
        conn.timeout = max(self.timeout, 2.0)
        conn.reset_input_buffer()

        deadline = time.time() + max(self.timeout, 2.0)
        buffer = bytearray()
        _LOGGER.debug("T330: reading data burst until %s", deadline)
        while time.time() < deadline:
            chunk = conn.read(10000)
            if chunk:
                buffer.extend(chunk)
                _LOGGER.debug("T330: received chunk of %d bytes, total: %d", len(chunk), len(buffer))
            else:
                # brief wait before next read
                time.sleep(0.05)
        _LOGGER.debug("T330: collected %d bytes after baud switch", len(buffer))
        if buffer:
            _LOGGER.debug("T330: raw data sample (first 100 bytes): %s", bytes(buffer[:100]).hex())
        return bytes(buffer)


