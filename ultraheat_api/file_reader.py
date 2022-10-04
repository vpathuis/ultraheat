""" 
Reads raw response data from a file. 
This is for (integration) testing purposes, so you won't need to drain the battery while doing initial integration testing.
"""
from typing import Tuple


class FileReader:
    def __init__(self, file_name) -> None:
        self._file_name = file_name

    def read(self) -> tuple[str, str]:
        with open(self._file_name, "rb") as f:
            model = f.readline().decode("utf-8")[0:9]
            if model:
                if model[0] == '!':
                    model = model[1:9]
                if model[0] == '/':
                    # Landis+Gyr UltraHeat T550 outputs model number prefixed with '/' instead of '!'
                    model = "LGUHT550"
                
            return model, f.read().decode("utf-8")
