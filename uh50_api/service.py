
from response import HeatMeterResponse


class HeatMeterService():
    """
    Reads the heat meter and returns its value.     
    """

    def __init__(self, reader) -> None:
        self.reader = reader

    def read(self) -> HeatMeterResponse:
        return HeatMeterResponse(self.reader.read())
