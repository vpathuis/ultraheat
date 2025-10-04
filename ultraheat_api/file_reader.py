""" 
Reads raw response data from a file. 
This is for (integration) testing purposes, so you won't need to drain the battery while doing initial integration testing.
"""
import logging
from typing import Tuple, Union

_LOGGER = logging.getLogger(__name__)

class FileReader:
    def __init__(self, file_name, protocol="uh50") -> None:
        self._file_name = file_name
        self._protocol = protocol

    def read(self) -> tuple[str, Union[str, bytes]]:
        with open(self._file_name, "rb") as f:
            if self._protocol == "t330":
                # For T330, read binary M-Bus data
                data = f.read()
                _LOGGER.debug("Read %d bytes from T330 file", len(data))
                _LOGGER.debug("T330 data (first 200 bytes): %s", data[:200].hex())
                return "T330", data
            else:
                # For UH50/T550, read UTF-8 text data
                model = f.readline().decode("utf-8")[1:9]
                data = f.read().decode("utf-8")
                _LOGGER.debug("Read from UH50 file:\n%s", data)
                return model, data
