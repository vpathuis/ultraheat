""" 
Reads raw response data from a file. 
This is for (integration) testing purposes, so you won't need to drain the battery while doing initial integration testing.
"""


class FileReader:
    def __init__(self, file_name) -> None:
        self._file_name = file_name

    def validate(self) -> str:
        """Reads the first line of the file, which should contain the model name"""
        with open(self._file_name, "rb") as f:
            return f.readline().decode("utf-8")[1:9]

    def read(self) -> str:
        with open(self._file_name, "rb") as f:
            _ = f.readline() # ignore the line with the model
            return f.read().decode("utf-8")
