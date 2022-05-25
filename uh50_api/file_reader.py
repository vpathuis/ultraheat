""" 
Reads raw UH50 response data from a file. 
This is for (integration) testing purposes, so you won't need to drain the battery while doing initial integration testing.
"""


class FileReader:
    def __init__(self, file_name) -> None:
        self._file_name = file_name
        self.model: str

    def validate(self) -> str:
        """Reads the first line of the file, which should contain the model name"""
        with open(self._file_name, "r") as f:
            self.model = f.readline().strip("\n")
            return self.model

    def read(self) -> str:
        with open(self._file_name, "r") as f:
            self.model = f.readline().strip("\n")
            return f.read()
