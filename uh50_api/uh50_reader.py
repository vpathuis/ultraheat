import serial
from serial import Serial

def read_uh50(port: str):
    pass

    def validate(self) -> Serial:
        try:
            result = self._connect_serial()
            result.close
        except:
            raise

    def _connect_serial(self) -> Serial:
        "Make the connection to the serial device"
        return serial.Serial(self.port,
                            baudrate=300,
                            bytesize=serial.SEVENBITS,
                            parity=serial.PARITY_EVEN,
                            stopbits=serial.STOPBITS_TWO,
                            timeout=1,
                            xonxoff=0,
                            rtscts=0
                            )

    def _wake_up(self, conn) -> str:
        "Waking up the device and get the model number"
        # Waking up should be done at 300 baud
        # Sending /?!
        conn.write(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x2F\x3F\x21\x0D\x0A")
        ir_command='/?!\x0D\x0A'
        conn.write(ir_command.encode('utf-8'))
        conn.flush()
        return conn.readline().decode('utf-8')[1:9]   # Read at 300 baud, this gives us the typenr

    def _get_data(self, conn):
        conn.baudrate=2400 # Now switch to 2400 BAUD. This could be different for other models. Let me know if you experience problems.
        ir_lines = ""
        ir_line = ""
        iteration = 0
        while ir_line != b'' and iteration < 26:  # reading all lines (typically 25 lines) 
            iteration += 1
            ir_line = conn.readline()
            ir_lines+=ir_line.decode('utf-8')

        return ir_lines