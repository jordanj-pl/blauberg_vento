from homeassistant.components.sensor import SensorEntity, SensorStateClass, SensorDeviceClass
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN

class BlaubergVentoAlarmStatusSensor(SensorEntity):
    """Sensor showing Blauberg Vento alarm status."""

    def __init__(self, api, device_info):
        self._api = api
        self._attr_name = "Alarm status"
        self._attr_unique_id = f"{device_info['device_id']}_alarm_status"
        self._attr_entity_category = None
        self._attr_icon = "mdi:help-circle-outline"
        self._device_id = device_info["device_id"]
        self._attr_native_unit_of_measurement = None
        self._attr_state_class = None
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_info["device_id"])},
        }

    @property
    def native_value(self):
        alarm_status = getattr(self._api, "_alarm_status", None)

        if alarm_status is None:
            return "Unknown"

        match alarm_status:
            case 0:
                return "OK"
            case 1:
                return "ALARM"
            case 2:
                return "Warning"
            case _:
                return "Unknown"

    @property
    def icon(self):
        alarm_status = getattr(self._api, "_alarm_status", None)

        if alarm_status == 0:
            return "mdi:check-circle-outline"
        elif alarm_status == 1:
            return "mdi:alarm-light"
        elif alarm_status == 2:
            return "mdi:alert-outline"
        else:
            return "mdi:help-circle-outline"

    @property
    def available(self):
        return True

class BlaubergVentoFilterReplacementSensor(SensorEntity):
    """Filter replacement sensor reported by the Blauberg Vento unit."""

    def __init__(self, api, device_info):
        self._api = api
        self._attr_name = "Filter replacement"
        self._attr_unique_id = f"{device_info['device_id']}_filter_replacement"
        self._attr_native_unit_of_measurement = None
        self._attr_icon = "mdi:air-filter"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_info["device_id"])},
        }

    @property
    def native_value(self):
        status = getattr(self._api, "_filter_replacement", None)

        if status is None:
            return None
        elif status == 0:
            return "OK"
        elif status == 1:
            return "Needs replacement"

        return None

    @property
    def icon(self):
        """Return a context-aware icon."""
        status = getattr(self._api, "_filter_replacement", None)
        if status == 1:
            # Red alert style
            return "mdi:air-filter-alert"
        elif status == 0:
            # Clean/healthy filter
            return "mdi:air-filter"
        else:
            # Indeterminate
            return "mdi:air-filter-check"

    @property
    def available(self):
        return True

class BlaubergVentoFilterReplacementCountdownSensor(SensorEntity):
    """Filter replacement sensor reported by the Blauberg Vento unit."""

    def __init__(self, api, device_info):
        self._api = api
        self._attr_name = "Filter replacement countdown"
        self._attr_unique_id = f"{device_info['device_id']}_filter_replacement_countdown"
        self._attr_native_unit_of_measurement = "days"
        self._attr_icon = "mdi:air-filter"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_info["device_id"])},
        }

    @property
    def native_value(self):
        hrs = getattr(self._api, "_filter_replacement_countdown", None)

        if hrs is None:
            return None

        days = int(hrs // 24)
        return days

    @property
    def available(self):
        return True

class BlaubergVentoHumiditySensor(SensorEntity):
    """Humidity reported by the Blauberg Vento unit."""

    def __init__(self, api, device_info):
        self._api = api
        self._attr_name = "Humidity"
        self._attr_unique_id = f"{device_info['device_id']}_humidity"
        self._attr_device_class = SensorDeviceClass.HUMIDITY
        self._attr_native_unit_of_measurement = "%"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:water-percent"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_info["device_id"])},
        }

    @property
    def native_value(self):
        return getattr(self._api, "_current_humidity", None)

    @property
    def available(self):
        return True

class BlaubergVentoDeviceIdSensor(SensorEntity):
    """Sensor showing Blauberg Vento device ID (diagnostic)."""

    def __init__(self, coordinator, device_info):
        self._attr_name = "Device ID"
        self._attr_unique_id = f"{device_info['device_id']}_device_id"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_icon = "mdi:identifier"
        self._device_id = device_info["device_id"]
        self._attr_native_unit_of_measurement = None
        self._attr_state_class = None
        self._attr_device_class = None
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_info["device_id"])},
        }

    @property
    def native_value(self):
        return self._device_id

    @property
    def available(self):
        return True

class BlaubergVentoIPSensor(SensorEntity):
    """Representation of the fan's IP address as a sensor."""

    def __init__(self, api, device_info):
        self._api = api
        self._attr_name = "IP Address"
        self._attr_unique_id = f"{device_info['device_id']}_device_ip"
        self._attr_icon = "mdi:ip-network"
        self._attr_native_unit_of_measurement = None
        self._attr_state_class = None
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_info["device_id"])},
        }

    @property
    def native_value(self):
        return getattr(self._api, "_device_network_ip", None)

    @property
    def available(self):
        return True

class BlaubergVentoRTCBatteryVoltage(SensorEntity):
    """Representation of the fan's RTC battery voltage."""

    def __init__(self, api, device_info):
        self._api = api
        self._attr_name = "Batt voltage"
        self._attr_unique_id = f"{device_info['device_id']}_rtc_batt_volage"
        self._attr_icon = "mdi:battery"
        self._attr_native_unit_of_measurement = "V"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_info["device_id"])},
        }

    @property
    def native_value(self):
        batt_voltage = getattr(self._api, "_battery_voltage", None)

        if batt_voltage is None:
            return None

        return batt_voltage/1000

    @property
    def icon(self):
        voltage = getattr(self._api, "_battery_voltage", None)
        if voltage is None:
            return "mdi:battery-unknown"

        voltage_v = voltage / 1000
        if voltage_v >= 3.1:
            return "mdi:battery"
        elif voltage_v >= 3.0:
            return "mdi:battery-90"
        elif voltage_v >= 2.8:
            return "mdi:battery-70"
        elif voltage_v >= 2.7:
            return "mdi:battery-40"
        elif voltage_v >= 2.5:
            return "mdi:battery-10"
        else:
            return "mdi:battery-alert-variant-outline"

    @property
    def available(self):
        return True

class BlaubergVentoMachineHours(SensorEntity):
    """Representation of the fan's machine hours."""

    def __init__(self, api, device_info):
        self._api = api
        self._attr_name = "Machine hours"
        self._attr_unique_id = f"{device_info['device_id']}_machine_hours"
        self._attr_icon = "mdi:cog-counterclockwise"
        self._attr_native_unit_of_measurement = "hrs"
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_info["device_id"])},
        }

    @property
    def native_value(self):
        hrs = getattr(self._api, "_machine_hours", None)

        if hrs is None:
            return None

        return round(hrs / 60, 1)

    @property
    def available(self):
        return True

class BlaubergVentoRTCTime(SensorEntity):
    """Representation of the fan's internal clock."""

    def __init__(self, api, device_info):
        self._api = api
        self._attr_name = "RTC Time"
        self._attr_unique_id = f"{device_info['device_id']}_rtc_datetime"
        self._attr_icon = "mdi:clock"
        self._attr_native_unit_of_measurement = None
        self._attr_state_class = None
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_info["device_id"])},
        }

    @property
    def native_value(self):
        date = getattr(self._api, "_rtc_date", None)
        time = getattr(self._api, "_rtc_time", None)

        if date is None or time is None:
            return None

        return f"{date} {time}"

    @property
    def available(self):
        return True

class BlaubergVentoFan1Speed(SensorEntity):
    """Representation of the fan's speed."""

    def __init__(self, api, device_info):
        self._api = api
        self._attr_name = "Fan 1 Speed"
        self._attr_unique_id = f"{device_info['device_id']}_fan1_speed"
        self._attr_icon = "mdi:fan"
        self._attr_native_unit_of_measurement = "rpm"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_info["device_id"])},
        }

    @property
    def native_value(self):
        return getattr(self._api, "_fan1_speed", None)

    @property
    def available(self):
        return True

class BlaubergVentoFan2Speed(SensorEntity):
    """Representation of the fan's speed."""

    def __init__(self, api, device_info):
        self._api = api
        self._attr_name = "Fan 2 Speed"
        self._attr_unique_id = f"{device_info['device_id']}_fan2_speed"
        self._attr_icon = "mdi:fan"
        self._attr_native_unit_of_measurement = "rpm"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_info["device_id"])},
        }

    @property
    def native_value(self):
        return getattr(self._api, "_fan2_speed", None)

    @property
    def available(self):
        return True

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up Blauberg Vento sensors."""
    api = hass.data[DOMAIN][entry.entry_id]
    device_id = entry.data.get("device_id", "unknown")

    # Add your device ID sensor (and others in the future)
    async_add_entities([
        BlaubergVentoAlarmStatusSensor(api, {"device_id": device_id}),
        BlaubergVentoHumiditySensor(api, {"device_id": device_id}),
        BlaubergVentoDeviceIdSensor(None, {"device_id": device_id}),
        BlaubergVentoIPSensor(api, {"device_id": device_id}),
        BlaubergVentoRTCBatteryVoltage(api, {"device_id": device_id}),
        BlaubergVentoMachineHours(api, {"device_id": device_id}),
        BlaubergVentoFilterReplacementSensor(api, {"device_id": device_id}),
        BlaubergVentoFilterReplacementCountdownSensor(api, {"device_id": device_id}),
        BlaubergVentoRTCTime(api, {"device_id": device_id}),
        BlaubergVentoFan1Speed(api, {"device_id": device_id}),
        BlaubergVentoFan2Speed(api, {"device_id": device_id}),
    ], True)