"""
Formats the raw reponse data into a HeatMeterResponse object
For different models, the raw data could be different. In these cases the RESPONSE_CONFIG might have to be modified.
"""

from dataclasses import dataclass
import datetime
import re

# defines the search expressions used when parsing the response from the heat meter
RESPONSE_CONFIG = {
    "heat_usage_gj": {"regex": r"6.8\((.*?)\*GJ\)", "unit": "GJ", "type": float},
    "heat_usage_mwh": {"regex": r"6.8\((.*?)\*MWh\)", "unit": "MWh", "type": float},
    "volume_usage_m3": {"regex": r"6.26\((.*?)\*m3\)", "unit": "m3", "type": float},
    "ownership_number": {"regex": r"9.21\((.*?)\)", "type": str},
    "volume_previous_year_m3": {"regex": r"6.26\*01\((.*?)\*m3\)", "unit": "m3", "type": float},
    "heat_previous_year_gj": {"regex": r"6.8\*01\((.*?)\*GJ\)", "unit": "GJ", "type": float},
    "heat_previous_year_mwh": {"regex": r"6.8\*01\((.*?)\*MWh\)", "unit": "MWh", "type": float},
    "error_number": {"regex": r"F\((.*?)\)", "type": str},
    "device_number": {"regex": r"9.20\((.*?)\)", "type": str},
    "measurement_period_minutes": {"regex": r"6.35\((.*?)\*m\)", "type": int},
    "power_max_kw": {"regex": r"6.6\((.*?)\*kW\)", "unit": "kW", "type": float},
    "power_max_previous_year_kw": {"regex": r"6.6\*01\((.*?)\*kW\)", "unit": "kW", "type": float},
    "flowrate_max_m3ph": {"regex": r"6.33\((.*?)\*m3ph\)", "unit": "m3ph", "type": float},
    "flowrate_max_previous_year_m3ph": {
        "regex": r"6.33\*01\((.*?)\*m3ph\)",
        "unit": "m3ph",
        "type": float,
    },
    "flow_temperature_max_c": {"regex": r"9.4\((.*?)\*C", "unit": "°C", "type": float},
    "return_temperature_max_c": {"regex": r"9.4\(.*?\*C&(.*?)\*C", "unit": "°C", "type": float},
    "flow_temperature_max_previous_year_c": {
        "regex": r"9.4\*01\((.*?)\*C",
        "unit": "°C",
        "type": float,
    },
    "return_temperature_max_previous_year_c": {
        "regex": r"9.4\*01\(.*?\*C&(.*?)\*C",
        "unit": "°C",
        "type": float,
    },
    "operating_hours": {"regex": r"6.31\((.*?)\*h\)", "type": int},
    "fault_hours": {"regex": r"6.32\((.*?)\*h\)", "type": int},
    "fault_hours_previous_year": {"regex": r"6.32\*01\((.*?)\*h\)", "type": int},
    "yearly_set_day": {"regex": r"6.36\((.*?)\)", "type": lambda a: a.replace("&", " ")},
    "monthly_set_day": {"regex": r"6.36\*02\((.*?)\)", "type": lambda a: a.replace("&", " ")},
    "meter_date_time": {
        "regex": r"9.36\((.*?)\)",
        "type": lambda a: datetime.datetime.strptime(a, "%Y-%m-%d&%H:%M:%S"),
    },
    "measuring_range_m3ph": {"regex": r"9.24\((.*?)\*m3ph\)", "unit": "m3ph", "type": float},
    "settings_and_firmware": {"regex": r"9.1\((.*?)\)", "type": lambda a: a.replace("&", " ")},
    "flow_hours": {"regex": r"9.31\((.*?)\*h\)", "type": int},
}



@dataclass
class HeatMeterResponse:
    model: str
    heat_usage_gj: float
    heat_usage_mwh: float
    volume_usage_m3: float
    ownership_number: str
    volume_previous_year_m3: float
    heat_previous_year_gj: float
    heat_previous_year_mwh: float
    error_number: str
    device_number: str
    measurement_period_minutes: int
    power_max_kw: float
    power_max_previous_year_kw: float
    flowrate_max_m3ph: float
    flow_temperature_max_c: float
    flowrate_max_previous_year_m3ph: float
    return_temperature_max_c: float
    flow_temperature_max_previous_year_c: float
    return_temperature_max_previous_year_c: float
    operating_hours: int
    fault_hours: int
    fault_hours_previous_year: int
    yearly_set_day: str
    monthly_set_day: str
    meter_date_time: datetime.datetime
    measuring_range_m3ph: float
    settings_and_firmware: str
    flow_hours: int
    raw_response: str


class HeatMeterResponseParser:

    def parse(self, model, raw_response) -> HeatMeterResponse:
        heat_usage_gj = self._match("heat_usage_gj", raw_response)
        heat_usage_mwh = self._match("heat_usage_mwh", raw_response)
        volume_usage_m3 = self._match("volume_usage_m3", raw_response)
        ownership_number = self._match("ownership_number", raw_response)
        volume_previous_year_m3 = self._match("volume_previous_year_m3", raw_response)
        heat_previous_year_gj = self._match("heat_previous_year_gj", raw_response)
        heat_previous_year_mwh = self._match("heat_previous_year_mwh", raw_response)
        error_number = self._match("error_number", raw_response)
        device_number = self._match("device_number", raw_response)
        measurement_period_minutes = self._match("measurement_period_minutes", raw_response)
        power_max_kw = self._match("power_max_kw", raw_response)
        power_max_previous_year_kw = self._match("power_max_previous_year_kw", raw_response)
        flowrate_max_m3ph = self._match("flowrate_max_m3ph", raw_response)
        flow_temperature_max_c = self._match("flow_temperature_max_c", raw_response)
        flowrate_max_previous_year_m3ph = self._match("flowrate_max_previous_year_m3ph", raw_response)
        return_temperature_max_c = self._match("return_temperature_max_c", raw_response)
        flow_temperature_max_previous_year_c = self._match("flow_temperature_max_previous_year_c", raw_response)
        return_temperature_max_previous_year_c = self._match("return_temperature_max_previous_year_c", raw_response)
        operating_hours = self._match("operating_hours", raw_response)
        fault_hours = self._match("fault_hours", raw_response)
        fault_hours_previous_year = self._match("fault_hours_previous_year", raw_response)
        yearly_set_day = self._match("yearly_set_day", raw_response)
        monthly_set_day = self._match("monthly_set_day", raw_response)
        meter_date_time = self._match("meter_date_time", raw_response)
        measuring_range_m3ph = self._match("measuring_range_m3ph", raw_response)
        settings_and_firmware = self._match("settings_and_firmware", raw_response)
        flow_hours = self._match("flow_hours", raw_response)

        return HeatMeterResponse(
            model,
            heat_usage_gj,
            heat_usage_mwh,
            volume_usage_m3,
            ownership_number,
            volume_previous_year_m3,
            heat_previous_year_gj,
            heat_previous_year_mwh,
            error_number,
            device_number,
            measurement_period_minutes,
            power_max_kw,
            power_max_previous_year_kw,
            flowrate_max_m3ph,
            flow_temperature_max_c,
            flowrate_max_previous_year_m3ph,
            return_temperature_max_c,
            flow_temperature_max_previous_year_c,
            return_temperature_max_previous_year_c,
            operating_hours,
            fault_hours,
            fault_hours_previous_year,
            yearly_set_day,
            monthly_set_day,
            meter_date_time,
            measuring_range_m3ph,
            settings_and_firmware,
            flow_hours,
            raw_response
        )

    def _match(self, name, raw_response):
        str_match = re.search(
            RESPONSE_CONFIG[name]["regex"], str(raw_response), re.M | re.I
        )
        if str_match:
            try:
                return RESPONSE_CONFIG[name]["type"](str_match.group(1))
            except ValueError:
                raise
