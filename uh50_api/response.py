"""
Formats the raw reponse data into a HeatMeterResponse object
For different models, the raw data could be different. In these cases the UH50_REGEX_CONFIG might have to be modified.
"""

from dataclasses import dataclass
import datetime
import re

# defines the search expressions used when parsing the response from the heat meter
UH50_REGEX_CONFIG = {
    "heat_usage_gj": {"regex": r"6.8\((.*?)\*GJ\)", "type": "float"},
    "volume_usage_m3": {"regex": r"6.26\((.*?)\*m3\)", "type": "float"},
    "ownership_number": {"regex": r"9.21\((.*?)\)", "type": "str"},
    "volume_previous_year_m3": {"regex": r"6.26\*01\((.*?)\*m3\)", "type": "float"},
    "heat_previous_year_gj": {"regex": r"6.8\*01\((.*?)\*GJ\)", "type": "float"},
    "error_number": {"regex": r"F\((.*?)\)", "type": "str"},
    "device_number": {"regex": r"9.20\((.*?)\)", "type": "str"},
    "measurement_period_minutes": {"regex": r"6.35\((.*?)\*m\)", "type": "int"},
    "power_max_kw": {"regex": r"6.6\((.*?)\*kW\)", "type": "float"},
    "power_max_previous_year_kw": {"regex": r"6.6\*01\((.*?)\*kW\)", "type": "float"},
    "flowrate_max_m3ph": {"regex": r"6.33\((.*?)\*m3ph\)", "type": "float"},
    "flowrate_max_previous_year_m3ph": {
        "regex": r"6.33\*01\((.*?)\*m3ph\)",
        "type": "float",
    },
    "flow_temperature_max_c": {"regex": r"9.4\((.*?)\*C", "type": "float"},
    "return_temperature_max_c": {"regex": r"9.4\(.*?\*C&(.*?)\*C", "type": "float"},
    "flow_temperature_max_previous_year_c": {
        "regex": r"9.4\*01\((.*?)\*C",
        "type": "float",
    },
    "return_temperature_max_previous_year_c": {
        "regex": r"9.4\*01\(.*?\*C&(.*?)\*C",
        "type": "float",
    },
    "operating_hours": {"regex": r"6.31\((.*?)\*h\)", "type": "int"},
    "fault_hours": {"regex": r"6.32\((.*?)\*h\)", "type": "int"},
    "fault_hours_previous_year": {"regex": r"6.32\*01\((.*?)\*h\)", "type": "int"},
    "yearly_set_day": {"regex": r"6.36\((.*?)\)", "type": "str"},
    "monthly_set_day": {"regex": r"6.36\*02\((.*?)\)", "type": "str"},
    "meter_date_time": {
        "regex": r"9.36\((.*?)\)",
        "type": "datetime",
        "format": "%Y-%m-%d&%H:%M:%S",
    },
    "measuring_range_m3ph": {"regex": r"9.24\((.*?)\*m3ph\)", "type": "float"},
    "settings_and_firmware": {"regex": r"9.1\((.*?)\)", "type": "str"},
    "flow_hours": {"regex": r"9.31\((.*?)\*h\)", "type": "int"},
}


@dataclass
class HeatMeterResponse:
    model: str
    raw_response: str

    def _match(self, name):
        str_match = re.search(
            UH50_REGEX_CONFIG[name]["regex"], str(self.raw_response), re.M | re.I
        )
        if str_match:
            try:
                if UH50_REGEX_CONFIG[name]["type"] == "float":
                    return float(str_match.group(1))
                elif UH50_REGEX_CONFIG[name]["type"] == "int":
                    return int(str_match.group(1))
                elif UH50_REGEX_CONFIG[name]["type"] == "datetime":
                    return datetime.datetime.strptime(
                        str_match.group(1), UH50_REGEX_CONFIG[name]["format"]
                    )
                elif UH50_REGEX_CONFIG[name]["type"] == "str":
                    return str_match.group(1)
                else:
                    return str_match.group(1)
            except ValueError:
                raise

    @property
    def heat_usage_gj(self) -> UH50_REGEX_CONFIG["heat_usage_gj"]["type"]:
        return self._match("heat_usage_gj")

    @property
    def volume_usage_m3(self) -> UH50_REGEX_CONFIG["volume_usage_m3"]["type"]:
        return self._match("volume_usage_m3")

    @property
    def ownership_number(self) -> UH50_REGEX_CONFIG["ownership_number"]["type"]:
        return self._match("ownership_number")

    @property
    def volume_previous_year_m3(
        self,
    ) -> UH50_REGEX_CONFIG["volume_previous_year_m3"]["type"]:
        return self._match("volume_previous_year_m3")

    @property
    def heat_previous_year_gj(
        self,
    ) -> UH50_REGEX_CONFIG["heat_previous_year_gj"]["type"]:
        return self._match("heat_previous_year_gj")

    @property
    def error_number(self) -> UH50_REGEX_CONFIG["error_number"]["type"]:
        return self._match("error_number")

    @property
    def device_number(self) -> UH50_REGEX_CONFIG["device_number"]["type"]:
        return self._match("device_number")

    @property
    def measurement_period_minutes(
        self,
    ) -> UH50_REGEX_CONFIG["measurement_period_minutes"]["type"]:
        return self._match("measurement_period_minutes")

    @property
    def power_max_kw(self) -> UH50_REGEX_CONFIG["power_max_kw"]["type"]:
        return self._match("power_max_kw")

    @property
    def power_max_previous_year_kw(
        self,
    ) -> UH50_REGEX_CONFIG["power_max_previous_year_kw"]["type"]:
        return self._match("power_max_previous_year_kw")

    @property
    def flowrate_max_m3ph(self) -> UH50_REGEX_CONFIG["flowrate_max_m3ph"]["type"]:
        return self._match("flowrate_max_m3ph")

    @property
    def flow_temperature_max_c(
        self,
    ) -> UH50_REGEX_CONFIG["flow_temperature_max_c"]["type"]:
        return self._match("flow_temperature_max_c")

    @property
    def flowrate_max_previous_year_m3ph(
        self,
    ) -> UH50_REGEX_CONFIG["flowrate_max_previous_year_m3ph"]["type"]:
        return self._match("flowrate_max_previous_year_m3ph")

    @property
    def return_temperature_max_c(
        self,
    ) -> UH50_REGEX_CONFIG["return_temperature_max_c"]["type"]:
        return self._match("return_temperature_max_c")

    @property
    def flow_temperature_max_previous_year_c(
        self,
    ) -> UH50_REGEX_CONFIG["flow_temperature_max_previous_year_c"]["type"]:
        return self._match("flow_temperature_max_previous_year_c")

    @property
    def return_temperature_max_previous_year_c(
        self,
    ) -> UH50_REGEX_CONFIG["return_temperature_max_previous_year_c"]["type"]:
        return self._match("return_temperature_max_previous_year_c")

    @property
    def operating_hours(self) -> UH50_REGEX_CONFIG["operating_hours"]["type"]:
        return self._match("operating_hours")

    @property
    def fault_hours(self) -> UH50_REGEX_CONFIG["fault_hours"]["type"]:
        return self._match("fault_hours")

    @property
    def fault_hours_previous_year(
        self,
    ) -> UH50_REGEX_CONFIG["fault_hours_previous_year"]["type"]:
        return self._match("fault_hours_previous_year")

    @property
    def yearly_set_day(self) -> UH50_REGEX_CONFIG["yearly_set_day"]["type"]:
        return self._match("yearly_set_day")

    @property
    def monthly_set_day(self) -> UH50_REGEX_CONFIG["monthly_set_day"]["type"]:
        return self._match("monthly_set_day")

    @property
    def meter_date_time(self) -> UH50_REGEX_CONFIG["meter_date_time"]["type"]:
        return self._match("meter_date_time")

    @property
    def measuring_range_m3ph(self) -> UH50_REGEX_CONFIG["measuring_range_m3ph"]["type"]:
        return self._match("measuring_range_m3ph")

    @property
    def settings_and_firmware(
        self,
    ) -> UH50_REGEX_CONFIG["settings_and_firmware"]["type"]:
        return self._match("settings_and_firmware")

    @property
    def flow_hours(self) -> UH50_REGEX_CONFIG["heat_usage_gj"]["type"]:
        return self._match("flow_hours")
