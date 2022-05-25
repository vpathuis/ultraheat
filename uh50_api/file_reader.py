""" 
Reads raw UH50 response data from a file. 
This is for (integration) testing purposes, so you won't need to drain the battery while doing initial integration testing.
"""
class FileReader():
    def __init__(self, file_name) -> None:
        self._file_name = file_name

    def validate(self) -> str:
        """ Reads the first line of the file, which should contain the model name """
        with open(self._file_name, "r") as f:
            return(f.readline())  

    def read(self) -> str:
        with open(self._file_name, "r") as f:
            return(f.read())
