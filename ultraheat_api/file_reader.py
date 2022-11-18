""" 
Reads raw response data from a file. 
This is for (integration) testing purposes, so you won't need to drain the battery while doing initial integration testing.
"""
import logging
from typing import Tuple

_LOGGER = logging.getLogger(__name__)

class FileReader:
    def __init__(self, file_name) -> None:
        self._file_name = file_name

    def read(self) -> tuple[str, str]:
        with open(self._file_name, "rb") as f:
            model = f.readline().decode("utf-8")[1:9]

            data = f.read().decode("utf-8")
            _LOGGER.debug("Read from file:\n%s", data)
            return model, data
