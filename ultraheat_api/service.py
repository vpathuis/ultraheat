"""
Reads raw Heat Meter data and returns a HeatMeterResponse object
"""
from ultraheat_api.response import HeatMeterResponse, HeatMeterResponseParser


class HeatMeterService:
    """
    Reads the heat meter and returns its value.
    """

    def __init__(self, reader) -> None:
        self.reader = reader

    def read(self) -> HeatMeterResponse:
        (model, raw_response) = self.reader.read()
        return HeatMeterResponseParser().parse(model, raw_response)
