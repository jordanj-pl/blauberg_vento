"""Library to handle communication with Blauberg Vento"""

import socket
import sys
from .const import DEFAULT_DEVICE_ID, MODEL_MAP

import logging
_LOGGER = logging.getLogger(__name__)

class BlaubergVentoApi(object):

    PACKET_BEGIN: bytes = bytes.fromhex("FDFD")
    PROTOCOL_TYPE: bytes = bytes.fromhex("02")
    DEVICE_ID_SIZE: bytes = bytes.fromhex("10")

    COMMAND_READ = 0x01
    COMMAND_WRITE = 0x02
    COMMAND_WRITETHANREAD = 0x03
    COMMAND_INCREMENT = 0x04
    COMMAND_DECREMENT = 0x05
    CONTROLLER_RESPONSE = 0x06

    FUNCTIONS = {
        0x0001: {"type": "uint", "length": 1, "property_name": "_device_on"},
        0x0002: {"type": "uint", "length": 1, "property_name": "_fan_speed_treshold"},
        0x0024: {"type": "uint", "length": 2, "property_name": "_battery_voltage"},
        0x0025: {"type": "uint", "length": 1, "property_name": "_current_humidity"},
        0x006F: {"type": "time", "length": 3, "property_name": "_rtc_time"},
        0x0070: {"type": "date", "length": 4, "property_name": "_rtc_date"},
        0x004A: {"type": "uint", "length": 2, "property_name": "_fan1_speed"},
        0x004B: {"type": "uint", "length": 2, "property_name": "_fan2_speed"},
        0x0064: {"type": "time_remaining", "length": 4, "property_name": "_filter_replacement_countdown"},#according to documentation the length should be 3 but actual value is 4-byte.
        0x0065: {"type": "uint", "length": 1, "property_name": ""},
        0x007C: {"type": "ascii", "length": 16, "property_name": "_device_id"},
        0x007E: {"type": "machine_hours", "length": 4, "property_name": "_machine_hours"},
        0x0080: {"type": "uint", "length": 1, "property_name": ""},
        0x0083: {"type": "uint", "length": 1, "property_name": "_alarm_status"},
        0x0086: {"type": "fw_version", "length": 6, "property_name": "_device_firmware"},
        0x0088: {"type": "uint", "length": 1, "property_name": "_filter_replacement"},
        0x009B: {"type": "uint", "length": 1, "property_name": "_device_network_settings_dhcp"},
        0x009C: {"type": "ipv4", "length": 4, "property_name": "_device_network_settings_ip"},
        0x009D: {"type": "ipv4", "length": 4, "property_name": "_device_network_settings_subnet"},
        0x009E: {"type": "ipv4", "length": 4, "property_name": "_device_network_settings_gateway"},
        0x00A3: {"type": "ipv4", "length": 4, "property_name": "_device_network_ip"},
        0x00B7: {"type": "uint", "length": 1, "property_name": "_operation_mode"},
        0x00B9: {"type": "uint", "length": 2, "property_name": "_device_model_id"},
    }

    FUNCTION_DEVICE_ON = 0x0001
    FUNCTION_FAN_SPEED_TRESHOLD = 0x0002
    FUNCTION_BATTERY_VOLTAGE = 0x0024
    FUNCTION_CURRENT_HUMIDITY = 0x0025
    FUNCTION_RTC_TIME = 0x006F
    FUNCTION_RTC_DATE = 0x0070
    FUNCTION_FAN1_SPEED = 0x004A
    FUNCTION_FAN2_SPEED = 0x004B
    FUNCTION_FILTER_REPLACEMENT_COUNTDOWN = 0x0064
    FUNCTION_FILTER_REPLACEMENT_COUNTDOWN_RESET = 0x0065
    FUNCTION_DEVICE_ID = 0x007C
    FUNCTION_MACHINE_HOURS = 0x007E
    FUNCTION_ALARM_RESET = 0x0080
    FUNCTION_ALARM_STATUS = 0x0083
    FUNCTION_FW_VERSION = 0x0086
    FUNCTION_FILTER_REPLACEMENT = 0x0088
    FUNCTION_NET_SETTINGS__DHCP = 0x009B
    FUNCTION_NET_SETTINGS__DEVICE_IP = 0x009C
    FUNCTION_NET_SETTINGS__SUBNET = 0x009D
    FUNCTION_NET_SETTINGS_GATEWAY = 0x009E
    FUNCTION_NET_DEVICE_IP = 0x00A3
    FUNCTION_OPERATION_MODE = 0x00B7
    FUNCTION_UNIT_TYPE = 0x00B9

    FAN_SPEEDS = {
        1: "low",
        2: "medium",
        3: "high",
        255: "manual",
    }
    FAN_SPEED_RANGE = (1, 3)

    FAN_MODES = {
        0: "ventilation",
        1: "heat recovery",
        2: "supply",
    }

    def __init__(
        self,
        host,
        port=4000,
        name="Blauberg Vento Fan",
        device_id=DEFAULT_DEVICE_ID,
        password="1111",
    ):
        self._name = name
        self._host = host
        self._port = port
        self._device_id = device_id
        self._device_model_id = None
        self._device_model = "Unknown Model"
        self._password = password

        self._device_network_ip = None

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(15)
        self.socket.connect((self._host, self._port))
        return self.socket

    def _ensure_socket(self):
        if not hasattr(self, "socket") or self.socket is None:
            self.connect()

    def authenticationHeader(self):
        return (
            self.PROTOCOL_TYPE
            + self.DEVICE_ID_SIZE
            + self._device_id.encode("ascii")
            + len(self._password).to_bytes(1, "little")
            + self._password.encode("ascii")
        )

    def send(self, command: int, function: int, data: bytes = b""):
        payload = command.to_bytes(1, "little")
        if function is not None:
            payload += function.to_bytes(2, "little")
        payload += data

        packet = (
            self.PACKET_BEGIN
            + self.authenticationHeader()
            + payload
            + self.checksum(self.authenticationHeader() + payload)
        )

        _LOGGER.debug("Sent packet: %s", packet.hex(" "))

        self.socket = self.connect()
        return self.socket.send(packet)

    def checksum(self, data):
        # Sum all bytes from TYPE to end of DATA
        checksum = sum(data) & 0xFFFF  # Keep only 16 bits

        checksum_low = (checksum & 0xFF).to_bytes(1, "little")
        checksum_high = ((checksum >> 8) & 0xFF).to_bytes(1, "little")

        return checksum_low + checksum_high

    def receive(self) -> bytes | None:
        try:
            return self.socket.recv(98)
        except socket.timeout:
            return None
        except Exception as e:
            _LOGGER.warning("Socket error: %s", e)
            return None

    def send_command_and_process_response(self, command: int, function: int, data: bytes = b""):
        try:
            self.send(command, function, data)
            response = self.receive()

            _LOGGER.debug("Response: %s", response)

            if response:
                self.parse_response(response)
                return 0
            else:
                return 1
        finally:
            if hasattr(self, "socket"):
                self.socket.close()

    def get_device_info(self):
        self.send_command_and_process_response(self.COMMAND_READ, self.FUNCTION_DEVICE_ID)

    def get_firmware_version(self):
        """Query and cache firmware version from device."""
        if hasattr(self, "_firmware_version"):
            print("*** CACHED: Get Firmware Version ***")
            return self._firmware_version  # already cached

        try:
            self.send_command_and_process_response(self.COMMAND_READ, self.FUNCTION_FW_VERSION)
        except Exception as e:
            _LOGGER.warning("Failed to get firmware version: %s", e)
            return None

        return getattr(self, "_firmware_version", "unknown")

    @staticmethod
    def _decode_firmware_version(data: bytes) -> str:
        if len(data) < 6:
            return "Unknown"
        major = data[0]
        minor = data[1]
        day = data[2]
        month = data[3]
        year = int.from_bytes(data[4:6], byteorder="little")
        return f"{major}.{minor} ({year:04d}-{month:02d}-{day:02d})"

    def get_network_info(self):
        """
        Request network information (DHCP mode, IP, subnet, gateway)
        in a single combined frame.
        """

        functions = [
            self.FUNCTION_NET_SETTINGS__DHCP,
            self.FUNCTION_NET_SETTINGS__DEVICE_IP,
            self.FUNCTION_NET_SETTINGS__SUBNET,
            self.FUNCTION_NET_SETTINGS_GATEWAY,
            self.FUNCTION_NET_DEVICE_IP,
        ]

        # Build concatenated data: each function as 2-byte little endian
        data = b"".join(f.to_bytes(2, "little") for f in functions)
        self.send_command_and_process_response(self.COMMAND_READ, 0x0000, data)

    def get_diagnostic_info(self):
        """Request diagnostic info"""
        functions = [
            self.FUNCTION_BATTERY_VOLTAGE,
            self.FUNCTION_MACHINE_HOURS,
            self.FUNCTION_FILTER_REPLACEMENT,
            self.FUNCTION_FILTER_REPLACEMENT_COUNTDOWN,
            self.FUNCTION_FAN1_SPEED
        ]

        if self.device_model_id != 27:
            functions.append(self.FUNCTION_FAN2_SPEED)

        # Build concatenated data: each function as 2-byte little endian
        data = b"".join(f.to_bytes(2, "little") for f in functions)
        self.send_command_and_process_response(self.COMMAND_READ, 0x0000, data)

    def reset_filter_replacement(self):
        """Resets filter replacement countdown."""

        self.send_command_and_process_response(self.COMMAND_WRITE, self.FUNCTION_FILTER_REPLACEMENT_COUNTDOWN_RESET, bytes.fromhex("00"))
        self.get_diagnostic_info()

    def update_status(self):
        """Update device status - on/off, fan speed, alarm etc."""
        functions = [
            self.FUNCTION_DEVICE_ON,
            self.FUNCTION_FAN_SPEED_TRESHOLD,
            self.FUNCTION_OPERATION_MODE,
            self.FUNCTION_ALARM_STATUS,
            self.FUNCTION_CURRENT_HUMIDITY
        ]

        # Build concatenated data: each function as 2-byte little endian
        data = b"".join(f.to_bytes(2, "little") for f in functions)
        self.send_command_and_process_response(self.COMMAND_READ, 0x0000, data)

    def reset_alarm_status(self):
        """Resets alarm status."""
        self.send_command_and_process_response(self.COMMAND_WRITE, self.FUNCTION_ALARM_RESET, bytes.fromhex("01"))

    def get_config_info(self):
        """Update device status - on/off, fan speed, alarm etc."""
        functions = [
            self.FUNCTION_RTC_TIME,
            self.FUNCTION_RTC_DATE,
        ]

        # Build concatenated data: each function as 2-byte little endian
        data = b"".join(f.to_bytes(2, "little") for f in functions)
        self.send_command_and_process_response(self.COMMAND_READ, 0x0000, data)

    def set_date_and_time(self, year, month, day, dayOfWeek, hours, minutes, seconds):
        """Update device RTC clock."""

        year_byte = year - 2000
        time_bytes = bytes([seconds, minutes, hours])
        date_bytes = bytes([day, dayOfWeek, month, year_byte])

        block_time = bytes([0xFE, 0x03]) + self.FUNCTION_RTC_TIME.to_bytes(1, 'big') + time_bytes
        block_date = bytes([0xFE, 0x03]) + self.FUNCTION_RTC_DATE.to_bytes(1, 'big') + date_bytes

        payload = block_time + block_date

        self.send_command_and_process_response(self.COMMAND_WRITETHANREAD, 0x0000, payload)

    def turn_on(self, speed_treshold=1, operation_mode=1):
        """Turn device on / wake up fron stand-by."""

        speed_byte = int(speed_treshold).to_bytes(1, "big")
        mode_byte = int(operation_mode).to_bytes(1, "big")

        block_turn_on = bytes([0xFE, 0x03, self.FUNCTION_DEVICE_ON, 0x01])
        block_fan_speed = bytes([0xFE, 0x03, self.FUNCTION_FAN_SPEED_TRESHOLD]) + speed_byte
        block_operation_mode = bytes([0xFE, 0x03, self.FUNCTION_OPERATION_MODE]) + mode_byte
        payload  = block_turn_on + block_fan_speed + block_operation_mode

        self.send_command_and_process_response(self.COMMAND_WRITETHANREAD, None, payload)

    def turn_off(self):
        """Turn device off / put into fron stand-by.
        *** WARNING! Please be aware that this command actually does not turn off the device. It will work in stand-by mode. In some cases (depends on jumper configuration) the device can operate with minimum power while in stand by mode.***
        """

        self.send_command_and_process_response(self.COMMAND_WRITETHANREAD, self.FUNCTION_DEVICE_ON, bytes.fromhex("00"))

    def set_operation_mode(self, mode=1):
        """
        Set operation mode.
        0 - ventilation 1 - heat recovery 2 - air supply
        """
        print("SET OPERATION MODE")
        self.send_command_and_process_response(self.COMMAND_WRITETHANREAD, self.FUNCTION_OPERATION_MODE, int(mode).to_bytes(1, 'big'))

    def extract_payload(self, response: bytes) -> bytes:
        """Strip the frame markers, header, and checksum."""
        if not response.startswith(self.PACKET_BEGIN):
            raise ValueError("Invalid frame header")

        # header length = 2 (FD FD) + 1 (TYPE) + 1 (SIZE_ID) + 16 (DEVICE_ID) + 1 (PW_LEN) + N (PW)
        type_byte = 2
        size_id_byte = 1
        device_id_len = response[3]  # if 0x10
        pw_len = response[4 + device_id_len]
        header_len = 2 + 1 + 1 + device_id_len + 1 + pw_len

        # remove start and checksum (last 2 bytes)
        data = response[header_len:-2]
        return data

    def parse_functions(self, payload: bytes):
        """Yield each function block (command + parameters) from payload."""
        start = 0
        while True:
            end = payload.find(b"\xfc", start)
            if end == -1:
                # no more functions
                if start < len(payload):
                    yield payload[start:]
                break
            # include the 0xFC marker for clarity
            yield payload[start : end + 1]
            start = end + 1

    def parsebytes(self, bytestring: bytes, params: dict):
        """
        Parse a single function block from the fan response.
        Yields (func_id, param_id, value_bytes) tuples.
        """
        i = iter(bytestring)
        func_id = None
        high_byte = 0x00
        param_size = 1

        while True:
            try:
                b = next(i)
            except StopIteration:
                break

            # First byte in block is function ID
            if func_id is None:
                func_id = b

                _LOGGER.debug("📦 Function ID: 0x%02X", func_id)
                continue

            # Special control bytes
            if b == 0xFE:
                # Next byte defines parameter size (1, 2, or 4 typically)
                param_size = next(i, 1)
                continue
            elif b == 0xFF:
                # Next byte defines high-byte "page"
                high_byte = next(i, 0)
                continue
            elif b == 0xFD:
                # Skip unsupported parameter
                _ = next(i, None)
                continue
            elif b == 0xFC:
                # End of current function block
                _LOGGER.debug("🔚 End of function 0x%02X", func_id)
                break

            # Combine high and low byte to make full parameter ID
            param_id = (high_byte << 8) | b

            # Determine parameter length
            length = params.get(param_id, {}).get("length", param_size)

            # Read parameter value
            value_bytes = bytes(next(i, 0) for _ in range(length))

            yield (func_id, param_id, value_bytes)

    def parse_response(self, data):
        """Parse full response frame from fan and decode functions using FUNCTIONS mapping."""
        payload = self.extract_payload(data)
        _LOGGER.debug("Payload: %s", payload.hex(" "))

        for func_block in self.parse_functions(payload):
            _LOGGER.debug("=== Parsing function block: %s ===", func_block.hex(' '))

            # parsebytes yields (func_id, param, value_list)
            for func_id, param, value_list in self.parsebytes(
                func_block, self.FUNCTIONS
            ):
                # convert value_list (list of ints) to bytes for decoding
                raw = bytes(value_list)

                if param in self.FUNCTIONS:
                    info = self.FUNCTIONS[param]

                    if info["type"] == "ascii":
                        # decode ascii, ignore undecodable bytes
                        value = (
                            raw[: info["length"]]
                            .decode("ascii", errors="ignore")
                            .rstrip("\x00")
                        )
                    elif info["type"] == "uint":
                        value = int.from_bytes(raw[: info["length"]], "little")
                    elif info["type"] == "ipv4":
                        value = ".".join(str(b) for b in raw)
                    elif info["type"] == "bytes":
                        value = raw
                    elif info["type"] == "fw_version":
                        value = self._decode_firmware_version(raw)
                    elif info["type"] == "machine_hours":
                        if len(raw) != 4:
                            _LOGGER.error("machine_hours - unexpected value length")

                        minutes = raw[0]
                        hours = raw[1]
                        days = raw[2] + (raw[3] << 8)

                        value = days * 24 * 60 + hours * 60 + minutes
                    elif info["type"] == "time":
                        hour = raw[2]
                        minute = raw[1]
                        second = raw[0]
                        value = f"{hour:02d}:{minute:02d}:{second:02d}"
                    elif info["type"] == "date":
                        day = raw[0]
                        month = raw[2]
                        year = 2000 + raw[3]
                        value = f"{year:04d}-{month:02d}-{day:02d}"
                    elif info["type"] == "time_remaining":
                        minutes = raw[0]
                        hours = raw[1]
                        days = raw[2]

                        value = days * 24 + hours + minutes / 60
                    else:
                        value = raw.hex(" ")

                    _LOGGER.debug("Function 0x%04X (%s): %s", param, info["type"], value)


                    # --- assign dynamically if property_name is defined ---
                    prop = info.get("property_name")
                    if prop:
                        setattr(self, prop, value)
                        _LOGGER.debug("Set %s = %s", prop, value)
                    else:
                        _LOGGER.debug("No property mapping for 0x%04X", param)

                else:
                    _LOGGER.debug("⚠️ Unknown function 0x%04X (func 0x%02X): %s", param, func_id, raw.hex(" "))

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def device_model(self) -> str:
        if getattr(self, "_device_model_id", None) is None:
            return "Unknown model"

        return MODEL_MAP.get(self._device_model_id, f"Unknown model code {self._device_model_id}")

    @property
    def device_model_id(self) -> int:
        return self._device_model_id

    @property
    def device_firmware(self) -> str:
        return self._device_firmware

    @property
    def device_network_ip(self):
        return self._device_network_ip

    @property
    def name(self):
        return self._name

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, ip):
        try:
            socket.inet_aton(ip)
            self._host = ip
        except socket.error:
            sys.exit()

    @property
    def port(self):
        return self._port

    @property
    def state(self):
        return self._fan_state

    @state.setter
    def state(self, val):
        if val == 0:
            self._fan_state = "off"
        elif val == 1:
            self._fan_state = "on"
        else:
            self._fan_state = "unknown"

    @property
    def speed_treshold(self):
        speed = getattr(self, "_fan_speed_treshold", None)
        if speed is None:
            return None

        return self.FAN_SPEEDS[speed]

    @property
    def operation_mode(self):
        mode = getattr(self, "_operation_mode", None)
        if mode is None:
            return None

        return self.FAN_MODES[mode]

    @property
    def available_modes(self):
        return list(self.FAN_MODES.values())

    @property
    def available_speed_tresholds(self):
        return list(self.FAN_SPEEDS.values())