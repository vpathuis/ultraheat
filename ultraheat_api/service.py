"""
Reads raw Heat Meter data and returns a HeatMeterResponse object
"""
import logging

from ultraheat_api.response import HeatMeterResponse, HeatMeterResponseParser
from ultraheat_api.mbus_t330 import T330ResponseParser

_LOGGER = logging.getLogger(__name__)

class HeatMeterService:
    """
    Reads the heat meter and returns its value.
    """

    def __init__(self, reader) -> None:
        self.reader = reader

    def read(self) -> HeatMeterResponse:
        (model, raw_response) = self.reader.read()
        # Route based on data type: bytes indicates T330 M-Bus path
        if isinstance(raw_response, (bytes, bytearray)):
            parsed = T330ResponseParser().parse(model, bytes(raw_response))
            response = HeatMeterResponse(**parsed)
            _LOGGER.debug("parsed result (T330): %s", response)
            return response

        parsed_result = HeatMeterResponseParser().parse(model, raw_response)
        _LOGGER.debug("parsed result: %s", parsed_result)
        return parsed_result
