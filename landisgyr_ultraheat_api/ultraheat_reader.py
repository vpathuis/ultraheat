""" 
Reads raw response data from the Ultraheat unit. 
To test the connection use validate, which will return the model name.
"""
import serial
from serial import Serial


class UltraheatReader:
    def __init__(self, port) -> None:
        self._port = port

    def validate(self) -> str:
        "Open connection to the device and get the model name, thereby validating the connection"
        with self._connect_serial() as conn:
            model = self._wake_up(conn)
        return model

    def read(self) -> str:
        "Reads the device on the specified port, returning the full string"
        with self._connect_serial() as conn:
            return self._get_data(conn)

    def _connect_serial(self) -> Serial:
        "Make the connection to the serial device"
        return Serial(
            self._port,
            baudrate=300,
            bytesize=serial.SEVENBITS,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_TWO,
            timeout=1,
            xonxoff=0,
            rtscts=0,
        )

    def _wake_up(self, conn) -> str:
        "Wake up the device and get the model number"
        # Waking up should be done at 300 baud
        # Sending /?!
        conn.write(
            b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x2F\x3F\x21\x0D\x0A"
        )
        ir_command = "/?!\x0D\x0A"
        conn.write(ir_command.encode("utf-8"))
        conn.flush()
        # Read at 300 baud, this gives us the typenr

        # checking if we can read the model (eg. 'LUGCUH50')
        model = conn.readline().decode("utf-8")[1:9]
        if not (model):
            raise Exception("No model could be read")
        return model

    def _get_data(self, conn):
        self._wake_up(conn)
        # Now switch to 2400 BAUD. This could be different for other models. Let me know if you experience problems.
        conn.baudrate = 2400
        ir_lines = ""
        ir_line = ""
        iteration = 0
        # reading all lines (typically 25 lines)
        while ir_line != b"" and iteration < 26:
            iteration += 1
            ir_line = conn.readline()
            ir_lines += ir_line.decode("utf-8")

        return str(ir_lines)
