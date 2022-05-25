"""
Reads raw Heat Meter data and returns a HeatMeterResponse object
"""
from uh50_api.response import HeatMeterResponse


class HeatMeterService():
    """
    Reads the heat meter and returns its value.     
    """

    def __init__(self, reader) -> None:
        self.reader = reader

    def read(self) -> HeatMeterResponse:
        return HeatMeterResponse(self.reader.read())

    def validate(self) -> str:
        """Validates the connection, returning the model number"""
        return HeatMeterResponse(self.reader.validate())
