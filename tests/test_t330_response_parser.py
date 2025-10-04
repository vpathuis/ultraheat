import datetime
import types

import pytest

from ultraheat_api.mbus_t330 import T330ResponseParser, T330Data


@pytest.fixture
def parser():
    return T330ResponseParser()


def test_t330_mapping_basic(monkeypatch, parser):
    # Prepare controlled T330Data resembling expected values from perl output
    fake_data = T330Data(
        energy_kwh=238.0,
        volume_qm=21.18,
        power_kw=0.0,
        volume_flow_qm_h=0.0,
        flow_temp_c=24.2,
        return_temp_c=24.0,
        temp_diff_k=0.1,
        fabrication_number="73034023",
        date_time=datetime.datetime(2024, 3, 17, 10, 27),
    )

    # Monkeypatch low-level frame decoder to avoid binary parsing in unit test
    import ultraheat_api.mbus_t330 as t330

    def fake_parse_mbus_frames(_: bytes) -> T330Data:
        return fake_data

    monkeypatch.setattr(t330, "parse_mbus_frames", fake_parse_mbus_frames)

    result = parser.parse("T330", b"dummy")

    # Energy: kWh -> MWh
    assert pytest.approx(result["heat_usage_mwh"]) == 0.238

    # Volume: m3 1:1
    assert pytest.approx(result["volume_usage_m3"]) == 21.18

    # IDs and date
    assert result["device_number"] == "73034023"
    assert result["meter_date_time"] == datetime.datetime(2024, 3, 17, 10, 27)

    # UH50 max/peak fields must remain untouched (0.0)
    assert result["power_max_kw"] == 0.0
    assert result["flowrate_max_m3ph"] == 0.0
    assert result["flow_temperature_max_c"] == 0.0
    assert result["return_temperature_max_c"] == 0.0


def test_t330_mapping_defaults(monkeypatch, parser):
    # No data parsed -> defaults should be returned
    empty_data = T330Data()

    import ultraheat_api.mbus_t330 as t330

    def fake_parse_mbus_frames(_: bytes) -> T330Data:
        return empty_data

    monkeypatch.setattr(t330, "parse_mbus_frames", fake_parse_mbus_frames)

    result = parser.parse("T330", b"dummy")

    assert result["heat_usage_mwh"] == 0.0
    assert result["volume_usage_m3"] == 0.0
    assert result["device_number"] == ""
    assert result["meter_date_time"] is None

    # UH50 max/peak remain 0.0
    assert result["power_max_kw"] == 0.0
    assert result["flowrate_max_m3ph"] == 0.0
    assert result["flow_temperature_max_c"] == 0.0
    assert result["return_temperature_max_c"] == 0.0


