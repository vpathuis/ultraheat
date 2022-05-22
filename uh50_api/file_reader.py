
class FileReader():
    def __init__(self, file_name) -> None:
        self._file_name = file_name

    def read(self):
        with open(self._file_name, "r") as f:
            return(f.read())

