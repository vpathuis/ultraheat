"""
Minimal M‑Bus decoder for T330 based on the perl convertMbus_v_1_7a.pl.

Scope: decode enough to extract common fields for HeatMeterResponse mapping:
- energy_kwh, volume_qm, power_kw, volume_flow_qm_h
- flow_temp_c, return_temp_c, temp_diff_k
- fabrication_number, date_time (if present)

Assumptions:
- Input is a concatenation of M‑Bus frames starting with 0x68 (long/control) and 0x10 (short) and possibly 0xE5 single acks.
- We validate checksum trivially (mod-256 over user data) analogous to perl. Frames with invalid checksum are skipped.
- We stop early on decode errors and return whatever we successfully parsed.
"""
from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from typing import Dict, Tuple, List

_LOGGER = logging.getLogger(__name__)


@dataclass
class T330Data:
    energy_kwh: float | None = None
    volume_qm: float | None = None
    power_kw: float | None = None
    volume_flow_qm_h: float | None = None
    flow_temp_c: float | None = None
    return_temp_c: float | None = None
    temp_diff_k: float | None = None
    fabrication_number: str | None = None
    date_time: datetime.datetime | None = None


def parse_mbus_frames(raw: bytes) -> T330Data:
    _LOGGER.debug("M-Bus: parsing %d bytes of raw data", len(raw))
    if raw:
        _LOGGER.debug("M-Bus: raw data sample (first 200 bytes): %s", raw[:200].hex())
    
    idx = 0
    result = T330Data()
    frame_count = 0
    # iterate through stream
    while idx < len(raw):
        b = raw[idx]
        if b == 0xE5:
            _LOGGER.debug("M-Bus: skipping single char 0xE5 at position %d", idx)
            idx += 1
            continue
        if b == 0x10:
            # short frame: 0x10 C A CHK 0x16
            if idx + 5 <= len(raw) and raw[idx + 4] == 0x16:
                _LOGGER.debug("M-Bus: skipping short frame at position %d", idx)
                idx += 5
                continue
            idx += 1
            continue
        if b != 0x68 or idx + 4 > len(raw):
            idx += 1
            continue
        # 0x68 L L 0x68 ... CHK 0x16
        frame_count += 1
        _LOGGER.debug("M-Bus: processing frame %d at position %d", frame_count, idx)
        L1 = raw[idx + 1]
        L2 = raw[idx + 2]
        b2 = raw[idx + 3]
        if L1 != L2 or b2 != 0x68:
            _LOGGER.debug("M-Bus: invalid header at position %d (L1=%d, L2=%d, b2=0x%02x)", idx, L1, L2, b2)
            idx += 1
            continue
        frame_len = L1
        end_pos = idx + 4 + frame_len + 2  # header(4) + data(L) + CHK + 0x16
        if end_pos > len(raw):
            _LOGGER.debug("M-Bus: frame %d incomplete (need %d bytes, have %d)", frame_count, end_pos - idx, len(raw) - idx)
            break
        data = raw[idx + 4 : idx + 4 + frame_len]
        chk = raw[idx + 4 + frame_len]
        end_marker = raw[idx + 4 + frame_len + 1]
        if end_marker != 0x16:
            _LOGGER.debug("M-Bus: frame %d missing end marker 0x16 (got 0x%02x)", frame_count, end_marker)
            idx += 1
            continue
        # checksum mod-256 like perl (sum of data bytes)
        calc_chk = sum(data) % 256
        if calc_chk != chk:
            _LOGGER.debug("M-Bus: frame %d checksum mismatch (calc=0x%02x, got=0x%02x)", frame_count, calc_chk, chk)
            idx = end_pos
            continue
        _LOGGER.debug("M-Bus: frame %d checksum OK, data length: %d", frame_count, len(data))
        # Decode RSP_UD frames only (C byte bitpattern ends with 0x08)
        if not data:
            _LOGGER.debug("M-Bus: frame %d has no data", frame_count)
            idx = end_pos
            continue
        C = data[0]
        if (C & 0x0F) != 0x08:
            _LOGGER.debug("M-Bus: frame %d not RSP_UD (C=0x%02x)", frame_count, C)
            idx = end_pos
            continue
        _LOGGER.debug("M-Bus: frame %d is RSP_UD, decoding...", frame_count)
        # CI must be 0x72, 0x76, or 0x0a (T330 uses 0x0a)
        if len(data) < 2:
            _LOGGER.debug("M-Bus: frame %d too short for CI", frame_count)
            idx = end_pos
            continue
        CI = data[1]
        if CI not in (0x72, 0x76, 0x0a):
            _LOGGER.debug("M-Bus: frame %d CI not supported (CI=0x%02x)", frame_count, CI)
            idx = end_pos
            continue
        _LOGGER.debug("M-Bus: frame %d CI OK (0x%02x), parsing records...", frame_count, CI)
        # Identification/m-bus address
        if len(data) < 6:
            _LOGGER.debug("M-Bus: frame %d too short for identification", frame_count)
            idx = end_pos
            continue
        subaddr_bcd = data[2:6]
        fabnum = ''.join(f"{(x >> 4) & 0xF}{x & 0xF}" for x in reversed(subaddr_bcd))
        _LOGGER.debug("M-Bus: frame %d fabrication number: %s", frame_count, fabnum)
        # decode records starting at offset 14 per perl
        if len(data) < 14:
            _LOGGER.debug("M-Bus: frame %d too short for records (need 14, have %d)", frame_count, len(data))
            idx = end_pos
            continue
        # The perl uses fields at 0..13 as header; start from 14
        pos = 14
        record_count = 0
        while pos < len(data):
            record_count += 1
            _LOGGER.debug("M-Bus: frame %d, record %d at position %d", frame_count, record_count, pos)
            dif = data[pos]
            pos += 1
            _LOGGER.debug("M-Bus: DIF=0x%02x", dif)
            # read DIFE chain
            dif_ext = (dif >> 7) & 1
            storage = (dif >> 6) & 0x01
            tariff = 0
            subunit = 0
            dife_count = 0
            while dif_ext and pos < len(data):
                dife_count += 1
                dife = data[pos]
                pos += 1
                _LOGGER.debug("M-Bus: DIFE %d=0x%02x", dife_count, dife)
                dif_ext = (dife >> 7) & 1
                subunit += ((dife >> 6) & 0x01)
                tariff += ((dife >> 4) & 0x03)
                storage += (dife & 0x0F) << 1
            _LOGGER.debug("M-Bus: storage=%d, tariff=%d, subunit=%d", storage, tariff, subunit)
            vif_type = 0
            if pos >= len(data):
                _LOGGER.debug("M-Bus: no VIF available")
                break
            vif_raw = data[pos]
            pos += 1
            vif_ext = (vif_raw >> 7) & 1
            vif = vif_raw & 0x7F
            _LOGGER.debug("M-Bus: VIF=0x%02x (raw=0x%02x)", vif, vif_raw)
            unit = None
            scale = 1.0
            # Primary VIFs (subset)
            if vif == 0x7C:
                # plain text, skip
                _LOGGER.debug("M-Bus: plain text VIF, skipping")
                if pos >= len(data):
                    break
                text_len = data[pos]
                pos += 1 + text_len
                continue
            elif (vif & 0xF8) == 0x00:  # energy Wh 10^(n-3)
                unit = "energy_kwh"
                n = (vif & 0x07)
                # For VIF 0x06 (n=6), Perl shows Factor: 1, so scale = 1
                # VIF 0x06 = energy Wh 10^(6-3) = 10^3 = 1000 Wh = 1 kWh
                scale = 10 ** (n - 3) / 1000.0  # Wh to kWh
                _LOGGER.debug("M-Bus: energy VIF, n=%d, scale=%f", n, scale)
            elif (vif & 0xF8) == 0x10:  # volume m3 10^(n-6)
                unit = "volume_qm"
                n = (vif & 0x07)
                scale = 10 ** (n - 6)
                _LOGGER.debug("M-Bus: volume VIF, n=%d, scale=%f", n, scale)
            elif (vif & 0xF8) == 0x28:  # power W 10^(n-3)
                unit = "power_kw"
                n = (vif & 0x07)
                scale = 10 ** (n - 3) / 1000.0
                _LOGGER.debug("M-Bus: power VIF, n=%d, scale=%f", n, scale)
            elif (vif & 0xF8) == 0x38:  # flow m3/h 10^(n-6)
                unit = "volume_flow_qm_h"
                n = (vif & 0x07)
                scale = 10 ** (n - 6)
                _LOGGER.debug("M-Bus: flow VIF, n=%d, scale=%f", n, scale)
            elif (vif & 0xFC) == 0x58:  # flow temp °C 10^(n-3)
                unit = "flow_temp_c"
                n2 = (vif & 0x03)
                scale = 10 ** (n2 - 3)
                _LOGGER.debug("M-Bus: flow temp VIF, n2=%d, scale=%f", n2, scale)
            elif (vif & 0xFC) == 0x5C:  # return temp °C 10^(n-3)
                unit = "return_temp_c"
                n2 = (vif & 0x03)
                scale = 10 ** (n2 - 3)
                _LOGGER.debug("M-Bus: return temp VIF, n2=%d, scale=%f", n2, scale)
            elif (vif & 0xFC) == 0x60:  # delta T K 10^(n-3)
                unit = "temp_diff_k"
                n2 = (vif & 0x03)
                scale = 10 ** (n2 - 3)
                _LOGGER.debug("M-Bus: temp diff VIF, n2=%d, scale=%f", n2, scale)
            elif vif == 0x78:  # fabrication number
                unit = "fabrication_number"
                scale = 0
                _LOGGER.debug("M-Bus: fabrication number VIF")
            elif (vif & 0xFE) == 0x6C:  # date/time
                unit = "date_time"
                scale = 0
                _LOGGER.debug("M-Bus: date/time VIF")
            # consume VIFEs if present (ignored for our subset)
            vife_count = 0
            while vif_ext and pos < len(data):
                vife_count += 1
                vife = data[pos]
                pos += 1
                _LOGGER.debug("M-Bus: VIFE %d=0x%02x", vife_count, vife)
                vif_ext = (vife >> 7) & 1
            # Now read data according to DIF low nibble
            data_field = dif & 0x0F
            _LOGGER.debug("M-Bus: data field type=%d", data_field)
            value = None
            if data_field == 0x00:
                _LOGGER.debug("M-Bus: no data")
                continue
            elif data_field == 0x01 and pos + 1 <= len(data):
                value = data[pos]
                pos += 1
                _LOGGER.debug("M-Bus: 8-bit integer value=%d", value)
            elif data_field == 0x02 and pos + 2 <= len(data):
                value = int.from_bytes(data[pos : pos + 2], "little")
                pos += 2
                _LOGGER.debug("M-Bus: 16-bit integer value=%d", value)
            elif data_field == 0x03 and pos + 3 <= len(data):
                value = int.from_bytes(data[pos : pos + 3], "little")
                pos += 3
                _LOGGER.debug("M-Bus: 24-bit integer value=%d", value)
            elif data_field == 0x04 and pos + 4 <= len(data):
                value = int.from_bytes(data[pos : pos + 4], "little")
                pos += 4
                _LOGGER.debug("M-Bus: 32-bit integer value=%d", value)
            elif data_field == 0x0C and pos + 4 <= len(data):
                # 8-digit BCD (perl treats as BCD -> we parse as integer)
                raw_b = data[pos : pos + 4]
                pos += 4
                bcd = ''.join(f"{b >> 4 & 0xF}{b & 0xF}" for b in reversed(raw_b))
                try:
                    value = int(bcd)
                    _LOGGER.debug("M-Bus: 8-digit BCD value=%d (raw=%s)", value, raw_b.hex())
                except ValueError:
                    _LOGGER.debug("M-Bus: invalid BCD: %s", bcd)
                    value = None
            elif data_field == 0x0E and pos + 6 <= len(data):
                # 12-digit BCD
                raw_b = data[pos : pos + 6]
                pos += 6
                bcd = ''.join(f"{b >> 4 & 0xF}{b & 0xF}" for b in reversed(raw_b))
                try:
                    value = int(bcd)
                    _LOGGER.debug("M-Bus: 12-digit BCD value=%d (raw=%s)", value, raw_b.hex())
                except ValueError:
                    _LOGGER.debug("M-Bus: invalid BCD: %s", bcd)
                    value = None
            elif data_field == 0x0F:
                # special functions (skip)
                _LOGGER.debug("M-Bus: special function, skipping")
                continue
            else:
                # unsupported -> skip conservatively
                _LOGGER.debug("M-Bus: unsupported data field type %d", data_field)
                continue
            # Map to result - only use current values (storage=0, tariff=0) unless it's fabrication number
            if unit == "fabrication_number" and value is not None:
                result.fabrication_number = str(value)
                _LOGGER.debug("M-Bus: set fabrication_number=%s", result.fabrication_number)
            elif unit == "date_time" and value is not None:
                # 32-bit CP32 date-time like perl: minute, hour, day, month, year composition
                v = int(value)
                minute = (v & 0x0000003F) >> 0
                hour = (v & 0x00001F00) >> 8
                day = (v & 0x001F0000) >> 16
                month = (v & 0x0F000000) >> 24
                year = ((v & 0x00E00000) >> 21) + ((v & 0xF0000000) >> (28 - 3))
                _LOGGER.debug("M-Bus: date/time components: %04d-%02d-%02d %02d:%02d", 2000 + year, month, day, hour, minute)
                try:
                    result.date_time = datetime.datetime(2000 + year, month, day, hour, minute)
                    _LOGGER.debug("M-Bus: set date_time=%s", result.date_time)
                except Exception:
                    _LOGGER.debug("M-Bus: invalid date/time")
                    pass
            elif unit and value is not None and scale is not None:
                # Only use current values (storage=0, tariff=0) for measurements
                if storage == 0 and tariff == 0:
                    scaled = value if scale == 0 else (float(value) * scale)
                    _LOGGER.debug("M-Bus: %s: raw=%d, scale=%f, scaled=%f (storage=%d, tariff=%d)", unit, value, scale, scaled, storage, tariff)
                    if unit == "energy_kwh":
                        result.energy_kwh = scaled  # Don't use _prefer_max, just take the current value
                        _LOGGER.debug("M-Bus: set energy_kwh=%f", result.energy_kwh)
                    elif unit == "volume_qm":
                        result.volume_qm = scaled  # Don't use _prefer_max, just take the current value
                        _LOGGER.debug("M-Bus: set volume_qm=%f", result.volume_qm)
                    elif unit == "power_kw":
                        result.power_kw = scaled
                        _LOGGER.debug("M-Bus: set power_kw=%f", result.power_kw)
                    elif unit == "volume_flow_qm_h":
                        result.volume_flow_qm_h = scaled
                        _LOGGER.debug("M-Bus: set volume_flow_qm_h=%f", result.volume_flow_qm_h)
                    elif unit == "flow_temp_c":
                        result.flow_temp_c = scaled
                        _LOGGER.debug("M-Bus: set flow_temp_c=%f", result.flow_temp_c)
                    elif unit == "return_temp_c":
                        result.return_temp_c = scaled
                        _LOGGER.debug("M-Bus: set return_temp_c=%f", result.return_temp_c)
                    elif unit == "temp_diff_k":
                        result.temp_diff_k = scaled
                        _LOGGER.debug("M-Bus: set temp_diff_k=%f", result.temp_diff_k)
                else:
                    _LOGGER.debug("M-Bus: skipping %s (storage=%d, tariff=%d) - not current value", unit, storage, tariff)
        # advance to next frame
        idx = end_pos
    _LOGGER.debug("M-Bus: parsed %d frames, result: %s", frame_count, result)
    return result


def _prefer_max(current: float | None, new_val: float) -> float:
    if current is None:
        return new_val
    return max(current, new_val)


class T330ResponseParser:
    """Parser that converts T330 raw M‑Bus bytes to HeatMeterResponse fields dict."""

    def parse(self, model: str, raw_response: bytes) -> dict:
        data = parse_mbus_frames(raw_response)
        # Build a dict matching HeatMeterResponse field names
        heat_usage_mwh = 0.0
        if data.energy_kwh is not None:
            heat_usage_mwh = data.energy_kwh / 1000.0
        result = {
            "model": model,
            "heat_usage_gj": 0.0,
            "heat_usage_mwh": heat_usage_mwh,
            "volume_usage_m3": data.volume_qm or 0.0,
            "ownership_number": "",
            "volume_previous_year_m3": 0.0,
            "heat_previous_year_gj": 0.0,
            "heat_previous_year_mwh": 0.0,
            "error_number": "0",
            "device_number": data.fabrication_number or "",
            "measurement_period_minutes": 0,
            "power_max_kw": 0.0,
            "power_max_previous_year_kw": 0.0,
            "flowrate_max_m3ph": 0.0,
            "flow_temperature_max_c": 0.0,
            "flowrate_max_previous_year_m3ph": 0.0,
            "return_temperature_max_c": 0.0,
            "flow_temperature_max_previous_year_c": 0.0,
            "return_temperature_max_previous_year_c": 0.0,
            "operating_hours": 0,
            "fault_hours": 0,
            "fault_hours_previous_year": 0,
            "yearly_set_day": "",
            "monthly_set_day": "",
            "meter_date_time": data.date_time,
            "measuring_range_m3ph": 0.0,
            "settings_and_firmware": "",
            "flow_hours": 0,
            "raw_response": raw_response.decode(errors="ignore"),
        }
        return result