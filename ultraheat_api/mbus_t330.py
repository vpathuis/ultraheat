"""
T330 M-Bus Frame Parser

This module parses M-Bus (Meter-Bus) data frames from Landis+Gyr T330 heat meters.
It extracts energy consumption, volume usage, temperatures, flow rates, and other
meter measurements from the binary M-Bus protocol data.

The M-Bus parsing logic and T330 communication protocol implementation are based on 
the excellent work by forum users gauner1986 and rainerlan from photovoltaikforum.com.
Their detailed analysis and Perl implementation provided the foundation for this parser.

See: https://www.photovoltaikforum.com/thread/188234-landis-gyr-ultraheat-t230-w%C3%A4rmez%C3%A4hler-mit-trct5000-und-esphome-wemos-d1-mini-aus/?postID=4221968#post4221968

TODO: This parser processes only current meter readings (Storage#: 0) and ignores 
historical data (e.g. previous year's consumption & max values from other storage numbers. This would be a future improvement.
"""
import struct
import datetime
import logging
import os
from dataclasses import dataclass
from typing import Optional, List

_LOGGER = logging.getLogger(__name__)
_DEBUG_FILE_HANDLER = None


@dataclass
class T330Data:
    """T330 M-Bus parsed data container."""
    energy_kwh: Optional[float] = None
    volume_qm: Optional[float] = None  
    power_kw: Optional[float] = None
    volume_flow_qm_h: Optional[float] = None
    flow_temp_c: Optional[float] = None
    return_temp_c: Optional[float] = None
    temp_diff_k: Optional[float] = None
    fabrication_number: Optional[str] = None
    date_time: Optional[datetime.datetime] = None


def _setup_debug_logging():
    """
    Setup timestamped debug log file in tests directory when debug mode is enabled.
    
    Returns:
        str: Path to the created debug log file, or None if debug not enabled
    """
    global _DEBUG_FILE_HANDLER
    
    # Enable debug logging by setting logger level
    _LOGGER.setLevel(logging.DEBUG)
        
    # Create timestamped log filename
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M")
    
    # Determine tests directory path (relative to this module)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    tests_dir = os.path.join(parent_dir, "tests")
    
    # Create tests directory if it doesn't exist
    os.makedirs(tests_dir, exist_ok=True)
    
    # Setup debug log file path
    debug_log_path = os.path.join(tests_dir, f"LGUT330_log_{timestamp}.txt")
    
    # Create file handler for debug logging
    _DEBUG_FILE_HANDLER = logging.FileHandler(debug_log_path, mode='w', encoding='utf-8')
    _DEBUG_FILE_HANDLER.setLevel(logging.DEBUG)
    
    # Set formatter with timestamp
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    _DEBUG_FILE_HANDLER.setFormatter(formatter)
    
    # Add handler to logger
    _LOGGER.addHandler(_DEBUG_FILE_HANDLER)
    
    # Log startup message
    _LOGGER.debug("=== M-Bus Debug Log Started ===")
    _LOGGER.debug("Debug log file: %s", debug_log_path)
    
    return debug_log_path


def _cleanup_debug_logging():
    """Clean up debug file handler."""
    global _DEBUG_FILE_HANDLER
    
    if _DEBUG_FILE_HANDLER:
        _LOGGER.removeHandler(_DEBUG_FILE_HANDLER)
        _DEBUG_FILE_HANDLER.close()
        _DEBUG_FILE_HANDLER = None


def parse_mbus_frames(raw: bytes) -> T330Data:
    """
    Parse M-Bus frames from raw byte data and extract meter measurements.
    
    Processes M-Bus protocol frames to extract current meter readings. The parser
    handles multiple frame types and validates frame integrity using checksums.
    Only processes data records with Storage#: 0 (current readings).
    
    Args:
        raw: Binary M-Bus data received from the meter
        
    Returns:
        T330Data object containing parsed measurements from current storage only
    """
    # Setup debug logging if debug mode is enabled
    debug_log_path = _setup_debug_logging()
    
    try:
        result = T330Data()
        
        # Convert raw bytes to array for indexed access during parsing (like Perl @infile)
        data_array = list(raw)
        idx = 0
        
        _LOGGER.debug("M-Bus: parsing %d bytes of frame data", len(data_array))
        
        if debug_log_path:
            _LOGGER.debug("M-Bus: Raw data length: %d bytes", len(raw))
            _LOGGER.debug("M-Bus: Raw data (first 50 bytes): %s", raw[:50].hex())
        
        # Main frame parsing loop - process each M-Bus frame sequentially
        # Parse through the byte stream looking for valid M-Bus frame headers
        while idx < len(data_array):
            if idx >= len(data_array):
                break
                
            # Read frame type indicator byte to determine M-Bus frame format
            frame_type_1 = data_array[idx]
            idx += 1
            
            _LOGGER.debug("M-Bus: processing frame type 0x%02X at position %d", frame_type_1, idx-1)
            
            # Handle different M-Bus frame types according to EN 13757-2 specification
            if frame_type_1 == 0xE5:
                _LOGGER.debug("M-Bus: 0x%02X is a single character frame", frame_type_1)
                continue
                
            elif frame_type_1 == 0x10:
                _LOGGER.debug("M-Bus: 0x%02X is a short frame", frame_type_1)
                continue
                
            elif frame_type_1 == 0x68:
                _LOGGER.debug("M-Bus: header ID 0x%02X is a control or long frame", frame_type_1)
                
                # Read M-Bus long frame header: length1, length2, frame_type_repeat
                if idx + 2 >= len(data_array):
                    break
                
                
                frame_length_1 = data_array[idx]
                frame_length_2 = data_array[idx + 1] 
                frame_type_2 = data_array[idx + 2]
                idx += 3
                
                # Validate M-Bus frame header integrity - lengths and frame types must match
                if frame_type_1 != frame_type_2 or frame_length_1 != frame_length_2:
                    _LOGGER.error("M-Bus: error in header found!")
                    continue
                    
                _LOGGER.debug("M-Bus: control or long frame length: %d", frame_length_1)
                
                # Extract the complete data payload excluding checksum and end marker
                if idx + frame_length_1 + 1 >= len(data_array):
                    break
                    
                data_block = data_array[idx:idx + frame_length_1]
                checksum_rcv = data_array[idx + frame_length_1]
                frame_end_marker = data_array[idx + frame_length_1 + 1]
                idx += frame_length_1 + 2
                
                # Verify data integrity using M-Bus checksum (sum of all data bytes mod 256)
                checksum_calc = sum(data_block) % 256
                if checksum_rcv != checksum_calc:
                    _LOGGER.error("M-Bus: checksum error!")
                    continue
                    
                # Verify proper frame termination with 0x16 end marker
                if frame_end_marker != 0x16:
                    _LOGGER.error("M-Bus: error in header (end char 0x16 not found)!")
                    continue
                    
                # Process the data block to extract measurements
                _decode_rsp_ud(data_block, result)
                
            else:
                _LOGGER.debug("M-Bus: 0x%02X is something else", frame_type_1)
                break
        
        _LOGGER.debug("M-Bus: parsing complete, result: %s", result)
        
        # Log final extraction results to debug file
        if debug_log_path:
            _LOGGER.debug("=== Final M-Bus Extraction Results ===")
            _LOGGER.debug("Energy consumption: %s kWh", result.energy_kwh)
            _LOGGER.debug("Volume consumption: %s m³", result.volume_qm)
            _LOGGER.debug("Power: %s W", result.power_kw)
            _LOGGER.debug("Volume flow: %s m³/h", result.volume_flow_qm_h)
            _LOGGER.debug("Flow temperature: %s °C", result.flow_temp_c)
            _LOGGER.debug("Return temperature: %s °C", result.return_temp_c)
            _LOGGER.debug("Temperature difference: %s K", result.temp_diff_k)
            _LOGGER.debug("Fabrication number: %s", result.fabrication_number)
            _LOGGER.debug("Date/time: %s", result.date_time)
            _LOGGER.debug("=== M-Bus Debug Log Complete ===")
        
        return result
        
    finally:
        # Always cleanup debug logging
        _cleanup_debug_logging()


def _decode_rsp_ud(data_block: List[int], result: T330Data) -> None:
    """
    Decode RSP_UD (Response User Data) M-Bus frame containing meter measurements.
    
    Processes the M-Bus application layer data to extract device identification
    and measurement values from the structured data blocks.
    """
    if len(data_block) < 2:
        return
        
    # Read C-field (Control field) - indicates frame function and direction
    c_field = data_block[0]
    
    # Read CI-field (Control Information field) - specifies data structure format
    ci_field = data_block[1]
    
    # Verify this is a Response User Data frame by checking C-field values
    c_field_hex = f"{c_field:02x}"
    
    if c_field_hex not in ("08", "18", "28", "38"):
        _LOGGER.debug("M-Bus: Not an RSP_UD frame (C-field: 0x%02X)", c_field)
        return
        
    _LOGGER.debug("M-Bus: 0x%02x: RSP_UD frame found - Parsing data...", c_field)
    
    # Validate CI field indicates standard variable data structure
    if ci_field not in (0x72, 0x76):
        _LOGGER.debug("M-Bus: For RSP_UD, the CI-field should be 0x72 or 0x76. Found CI 0x%02X, continuing anyway", ci_field)
    
    # Extract device identification number from M-Bus header (stored little-endian)
    if len(data_block) >= 6:
        sub_address_bytes = data_block[2:6]
        sub_address_bytes.reverse()  # Convert from little-endian to readable format
        sub_address = ''.join(f"{b:02x}" for b in sub_address_bytes)
        _LOGGER.debug("M-Bus device address: %s", sub_address)
    
    # Skip fixed header fields to reach variable data records:
    # manufacturer ID (2 bytes), version (1), medium (1), access counter (1), 
    # status (1), signature (2) = 8 bytes total
    # Variable data blocks start at offset 14 in RSP_UD frame structure
    _decode_data_blocks(data_block[14:], result)


def _decode_data_blocks(data_block_array: List[int], result: T330Data) -> None:
    """
    Decode M-Bus variable data records containing measurement values.
    
    Processes DIF/VIF encoded data records to extract meter readings. Each record
    contains data type information, value encoding, units, and storage details.
    Only processes current readings (Storage#: 0) and ignores historical data.
    """
    # Convert to list for sequential processing of data records
    data_array = list(data_block_array)
    
    # Process each data record until all bytes are consumed
    while len(data_array) > 0:
        
        # Read DIF (Data Information Field) - encodes data type and storage info
        dif = data_array.pop(0)
        print(f"dif: 0x{dif:02X}, ", end="")
        
        # Parse DIF bit fields according to M-Bus specification
        dif_ext = (dif >> 7) & 1                    # Extension bit (more DIFE follows)
        dif_lsb_storage = (dif & 0x40) >> 6         # LSB of storage number
        dif_function_field = (dif & 0x30) >> 4      # Function field (instant/max/min/error)
        dif_data_field = dif & 0x0F                 # Data field (encoding type and length)
        
        storage_number = dif_lsb_storage
        dife_counter = 0
        tariff = 0
        sub_unit = 0
        
        # Process DIFE (Data Information Field Extension) bytes if present
        while dif_ext == 1:
            if len(data_array) == 0:
                break
            dife = data_array.pop(0)
            if dife_counter == 0:
                print("dife:", end="")
            print(f" 0x{dife:02X},", end="")
            
            # Parse DIFE bit fields to extend storage/tariff information
            dif_ext = (dife >> 7) & 1  # Extension bit indicates more DIFE bytes follow
            sub_unit += ((dife & 0x40) >> 6) << dife_counter          # Sub-unit identification
            tariff += ((dife & 0x30) >> 4) << (dife_counter * 2)     # Tariff register selection
            storage_number += (dife & 0x0F) << (1 + dife_counter * 4) # Extended storage number bits
            
            dife_counter += 1
            if dife_counter > 10:
                print("Error: > 10 DIFE entries detected")
                return
        
        if len(data_array) == 0:
            break
            
        # Read VIF (Value Information Field) - encodes measurement unit and scaling
        vif = data_array.pop(0)
        print(f" vif: 0x{vif:02X}, ", end="")
        
        vif_ext = (vif >> 7) & 1  # Extension bit indicates VIFE follows
        vif = vif & 0x7F          # Clear extension bit to get actual VIF code
        
        # Initialize unit decoding variables
        scaling_factor = 1
        unit = None
        unit_ext = "0"
        
        # Handle VIF extensions for manufacturer-specific or linear VIFs
        if vif in (0x7D, 0x7B):
            if len(data_array) == 0:
                break
            vife_first = data_array.pop(0)
            print(f"vife: 0x{vife_first:02X}")
            
            # Process linear VIF extensions for special measurement types
            if vife_first == 0x6E:
                print("Linear vifextension found!")
            elif vife_first == 0x6F:
                print("Linear vifextension found!")
        
        # Decode VIF code to determine measurement unit and scaling factor
        unit = None
        scaling_factor = 1
        
        # Map VIF codes to measurement types according to EN 13757-3 specification
        if vif == 0x74:
            unit = "activity_duration_sec"
            scaling_factor = 1
        elif vif == 0x70:
            unit = "avg_duration_sec"
            scaling_factor = 1  
        elif vif == 0x06:
            unit = "energy_kwh"
            scaling_factor = 1
        elif vif == 0x14:
            unit = "volume_qm"
            scaling_factor = 0  # Special BCD handling with custom scaling
        elif vif == 0x2D:
            unit = "power_kw"
            scaling_factor = 100
        elif vif == 0x3B:
            unit = "volume_flow_qm_h"
            scaling_factor = 0  # Special BCD handling with custom scaling
        elif vif == 0x5A:
            unit = "flow_temp_c"
            scaling_factor = 0  # Special BCD handling with custom scaling
        elif vif == 0x5E:
            unit = "return_temp_c"
            scaling_factor = 0  # Special BCD handling with custom scaling
        elif vif == 0x62:
            unit = "temp_diff_k"
            scaling_factor = 0  # Special BCD handling with custom scaling
        elif vif == 0x78:
            unit = "fabrication_number"
            scaling_factor = 0  # Special BCD handling with custom scaling
        else:
            # Skip unsupported VIF codes
            print(f"Unsupported VIF: 0x{vif:02X}")
            continue
            
        # Extract measurement value based on DIF data field encoding
        reading = None
        
        # Decode data according to M-Bus data field specification
        if dif_data_field == 0:
            # No data
            continue
        elif dif_data_field == 1:
            # 8-bit integer
            if len(data_array) > 0:
                reading = data_array.pop(0)
        elif dif_data_field == 2:
            # 16-bit integer stored in little-endian byte order
            if len(data_array) >= 2:
                byte_field = []
                for _ in range(2):
                    byte_field.insert(0, data_array.pop(0))  # Reverse byte order for big-endian
                # Convert bytes to BCD decimal representation
                hex_str = ''.join(f"{b:02x}" for b in byte_field)
                try:
                    reading = int(hex_str)
                except ValueError:
                    # Skip malformed hex data that cannot be converted to integer
                    continue
        elif dif_data_field == 3:
            # 24-bit integer stored in little-endian byte order
            if len(data_array) >= 3:
                byte_field = []
                for _ in range(3):
                    byte_field.insert(0, data_array.pop(0))  # Reverse byte order for big-endian
                # Convert bytes to BCD decimal representation
                hex_str = ''.join(f"{b:02x}" for b in byte_field)
                try:
                    reading = int(hex_str)
                except ValueError:
                    continue
        elif dif_data_field == 4:
            # 32-bit integer stored in little-endian byte order
            if len(data_array) >= 4:
                byte_field = []
                for _ in range(4):
                    byte_field.insert(0, data_array.pop(0))  # Reverse byte order for big-endian
                # Convert bytes to BCD decimal representation
                hex_str = ''.join(f"{b:02x}" for b in byte_field)
                try:
                    reading = int(hex_str)
                except ValueError:
                    continue
        elif dif_data_field == 9:
            # 2-digit BCD
            if len(data_array) > 0:
                bcd_byte = data_array.pop(0)
                hex_str = f"{bcd_byte:02x}"
                try:
                    reading = int(hex_str)
                except ValueError:
                    continue
        elif dif_data_field == 10:
            # 4-digit BCD (Binary Coded Decimal) value
            if len(data_array) >= 2:
                byte_field = []
                for _ in range(2):
                    byte_field.insert(0, data_array.pop(0))  # Reverse byte order for big-endian
                hex_str = ''.join(f"{b:02x}" for b in byte_field)
                try:
                    reading = int(hex_str)
                except ValueError:
                    continue
        elif dif_data_field == 11:
            # 6-digit BCD (Binary Coded Decimal) value
            if len(data_array) >= 3:
                byte_field = []
                for _ in range(3):
                    byte_field.insert(0, data_array.pop(0))  # Reverse byte order for big-endian
                hex_str = ''.join(f"{b:02x}" for b in byte_field)
                try:
                    reading = int(hex_str)
                except ValueError:
                    continue
        elif dif_data_field == 12:
            # 8-digit BCD (Binary Coded Decimal) value
            if len(data_array) >= 4:
                byte_field = []
                for _ in range(4):
                    byte_field.insert(0, data_array.pop(0))  # Reverse byte order for big-endian
                hex_str = ''.join(f"{b:02x}" for b in byte_field)
                try:
                    reading = int(hex_str)
                except ValueError:
                    continue
        else:
            # Unsupported data field type - skip
            print(f"Unsupported data field: {dif_data_field}")
            continue
        
        # Apply unit scaling and store measurement values
        if reading is not None and unit:
            # CRITICAL: Only process current readings (Storage#: 0) - ignore historical data
            # Historical data from other storage numbers is not needed for current usage
            if storage_number != 0:
                _LOGGER.debug("M-Bus: Skipping Storage#: %d (historical data)", storage_number)
                continue
                
            # Apply appropriate scaling based on measurement type and encoding
            if scaling_factor == 0:
                # Custom scaling for BCD-encoded measurements
                if unit == "volume_qm":
                    reading_scaled = reading / 100.0  # Convert to m³ with 0.01 scaling
                elif unit == "volume_flow_qm_h":
                    reading_scaled = reading / 1000.0  # Convert to m³/h with 0.001 scaling
                elif unit in ("flow_temp_c", "return_temp_c", "temp_diff_k"):
                    # Temperature values use 0.1 degree resolution (e.g., 589→58.9°C)
                    reading_scaled = reading / 10.0  # Convert with 0.1 scaling for temperatures
                else:
                    reading_scaled = reading
            else:
                reading_scaled = reading * scaling_factor if scaling_factor != 1 else reading
                if unit == "power_kw" and scaling_factor == 100:
                    reading_scaled = reading_scaled  # Maintain Watt units as received
            
            # Output measurement details for debugging and verification
            print(f"Rd: {reading_scaled} {unit}, {unit_ext}; RAW: {reading:08X}; Factor: {scaling_factor}, Storage#: {storage_number}, Tariff: {tariff}, SubUnit: {sub_unit}")
            
            # Store measurement values from current storage (Storage#: 0) only
            if storage_number == 0 and tariff == 0 and sub_unit == 0:
                if unit == "energy_kwh" and result.energy_kwh is None:
                    result.energy_kwh = reading_scaled
                elif unit == "volume_qm" and result.volume_qm is None:
                    result.volume_qm = reading_scaled
                elif unit == "power_kw" and result.power_kw is None:
                    result.power_kw = reading_scaled
                elif unit == "volume_flow_qm_h" and result.volume_flow_qm_h is None:
                    result.volume_flow_qm_h = reading_scaled
                elif unit == "flow_temp_c" and result.flow_temp_c is None:
                    result.flow_temp_c = reading_scaled
                elif unit == "return_temp_c" and result.return_temp_c is None:
                    result.return_temp_c = reading_scaled
                elif unit == "temp_diff_k" and result.temp_diff_k is None:
                    result.temp_diff_k = reading_scaled
                elif unit == "fabrication_number" and result.fabrication_number is None:
                    result.fabrication_number = str(reading)


class T330ResponseParser:
    """Parser that converts T330 raw M‑Bus bytes to standardized heat meter response format."""

    def parse(self, model: str, raw_response: bytes) -> dict:
        data = parse_mbus_frames(raw_response)
        # Build a standardized response dictionary with all expected fields
        heat_usage_mwh = 0.0
        if data.energy_kwh is not None:
            heat_usage_mwh = data.energy_kwh / 1000.0
        heat_usage_gj = heat_usage_mwh * 3.6
        result = {
            "model": model,
            "heat_usage_gj": heat_usage_gj,
            "heat_usage_mwh": heat_usage_mwh,
            "volume_usage_m3": data.volume_qm or 0.0,
            "ownership_number": "",
            "volume_previous_year_m3": 0.0,
            "heat_previous_year_gj": 0.0,
            "heat_previous_year_mwh": 0.0,
            "error_number": "0",
            "device_number": data.fabrication_number or "",
            "measurement_period_minutes": 0,
            "power_max_kw": data.power_kw or 0.0,
            "power_max_previous_year_kw": 0.0,
            "flowrate_max_m3ph": data.volume_flow_qm_h or 0.0,
            "flow_temperature_max_c": data.flow_temp_c or 0.0,
            "flowrate_max_previous_year_m3ph": 0.0,
            "return_temperature_max_c": data.return_temp_c or 0.0,
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
            # T330 specific fields
            "energy_consumption_kwh": data.energy_kwh or 0.0,
            "power_w": data.power_kw or 0.0,  # Power is already in watts from M-Bus
            "volume_flow_m3_h": data.volume_flow_qm_h or 0.0,
            "flow_temperature_c": data.flow_temp_c or 0.0,
            "return_temperature_c": data.return_temp_c or 0.0,
            "temperature_difference_k": data.temp_diff_k or 0.0,
            "fabrication_number": data.fabrication_number or "",
        }
        return result