from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.const import UnitOfTime
from homeassistant.helpers.entity import DeviceInfo

from functools import cached_property

from .const import DOMAIN

SPEEDS = ["off", "low", "medium", "high"]

class BlaubergVentoFan(FanEntity):
    """Representation of the Blauberg Vento fan."""

    _attr_supported_features = (
        FanEntityFeature.SET_SPEED
        | FanEntityFeature.PRESET_MODE
    )

    def __init__(self, api, device_info):
        self._api = api
        self._attr_name = "HRV"
        self._attr_unique_id = f"{device_info['device_id']}_hrv"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_info["device_id"])},
        )

    async def async_turn_on(self, **kwargs):
        await self._api.set_power(True)
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self._api.set_power(False)
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the fan speed percentage."""
        await self._api.set_speed(percentage)
        self._attr_percentage = percentage
        self.async_write_ha_state()

    async def async_update(self):
        """Fetch the latest state from the device."""
        await self.hass.async_add_executor_job(self._api.update_status)

        self._attr_is_on = self._api._device_on
        self._attr_percentage = self._api._fan_speed_treshold

    @property
    def is_on(self) -> bool | None:
        isOn = self._api._device_on

        if isOn is None:
            return None

        return bool(isOn == 1)

    @cached_property
    def preset_mode(self) -> str | None:
        """Return the list of available operation modes."""
        return self._api.operation_mode

    @cached_property
    def preset_modes(self) -> list[str] | None:
        """Return the current operation mode."""
        return self._api.available_modes


from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

async def async_setup_entry(hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
):

    """Set up Blauberg Vento control pane."""
    api = hass.data[DOMAIN][entry.entry_id]
    device_id = entry.data.get("device_id", "unknown")

    async_add_entities([
#        BlaubergVentoFan(api, {"device_id": device_id})
    ], True)