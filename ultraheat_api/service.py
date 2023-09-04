"""
Reads raw Heat Meter data and returns a HeatMeterResponse object
"""
import logging

from ultraheat_api.response import HeatMeterResponse, HeatMeterResponseParser

_LOGGER = logging.getLogger(__name__)

class HeatMeterService:
    """
    Reads the heat meter and returns its value.
    """

    def __init__(self, reader) -> None:
        self.reader = reader

    def read(self) -> HeatMeterResponse:
        (model, raw_response) = self.reader.read()
        parsed_result = HeatMeterResponseParser().parse(model, raw_response)
        _LOGGER.debug("parsed result: ", parsed_result)
        return parsed_result
