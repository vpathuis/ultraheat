"""
Reads raw Heat Meter data and returns a HeatMeterResponse object
"""
from uh50_api.response import HeatMeterResponse


class HeatMeterService:
    """
    Reads the heat meter and returns its value.
    """

    def __init__(self, reader) -> None:
        self.reader = reader

    def read(self) -> HeatMeterResponse:
        raw_response = self.reader.read()
        self.response = HeatMeterResponse(self.reader.model, raw_response)
        return self.response

    def validate(self) -> str:
        """Validates the connection, returning the model number"""
        return self.reader.validate()
