import logging
import math
import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .fan_api import BlaubergVentoApi


from homeassistant.components.diagnostics import DiagnosticsData

from .const import DOMAIN, DEFAULT_DEVICE_ID

from homeassistant.components.fan import (
    FanEntity,
    FanEntityFeature,
)
from homeassistant.const import ATTR_ENTITY_ID
import homeassistant.helpers.config_validation as cv
from homeassistant.util.percentage import (
    percentage_to_ranged_value,
    ordered_list_item_to_percentage,
)

_LOGGER = logging.getLogger(__name__)

# Constants
ORDERED_NAMED_FAN_SPEEDS = ["low", "medium", "high"]#, "manual"

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    api = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            BlaubergVentoFan(api),
        ], True)

class BlaubergVentoFan(FanEntity):

    def __init__(self, api):
        _LOGGER.debug("Initializing BlaubergVentoFan for %s", api._host)
        self._api = api
        self._name = api.name
        self._attr_name = api.name
        self._attr_unique_id = api.device_id or api._host
        self._attr_supported_features = FanEntityFeature.SET_SPEED | FanEntityFeature.PRESET_MODE | FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF
        self._attr_preset_modes = self._api.available_modes
        self._attr_preset_mode = None
        self._attr_speed_count = len(self._api.available_speed_tresholds) -1
        self._attr_percentage = None

# Initialize attributes so HA knows what to expect
#    self._attr_percentage = 0
#    self._attr_preset_mode = self._api.available_modes[0] if self._api.available_modes else None
#    self._attr_preset_modes = self._api.available_modes or ["ventilation", "heat recovery", "supply"]
#    self._attr_speed_count = len(self._api.available_speed_tresholds) - 1

    async def async_update(self):
        """Fetch the latest fan data."""
        await self.hass.async_add_executor_job(self._api.update_status)
        await self.hass.async_add_executor_job(self._api.get_diagnostic_info)
        await self.hass.async_add_executor_job(self._api.get_config_info)
        # Assign unique ID once the real device ID is known
        if not self._attr_unique_id and self._api.device_id != DEFAULT_DEVICE_ID:
            self._attr_unique_id = f"blauberg_vento_{self._api.device_id}"

    @property
    def name(self):
        return self._name

    @property
    def should_poll(self):
        return True

    @property
    def device_info(self):
        """Return device information for the Blauberg Vento fan."""

        return {
            "identifiers": {(DOMAIN, self._api.device_id)},
            "name": self.name,
            "manufacturer": "Blauberg",
            "model": self._api.device_model,
            "sw_version": getattr(self._api, "device_firmware", "unknown"),
        }

    @property
    def available(self):
        speed_treshold = self._api.speed_treshold
        return bool(speed_treshold != "manual")

    @property
    def is_on(self):
        device_on = getattr(self._api, "_device_on", None)

        if device_on is None:
            return None

        return bool(device_on == 1)

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs
    ) -> None:
        """Turn on the fan."""
        await self.hass.async_add_executor_job(self._api.turn_on)

        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the fan."""
        await self.hass.async_add_executor_job(self._api.turn_off)
        self._attr_is_on = False
        self.async_write_ha_state()

    @property
    def percentage(self):
        """Return the current fan speed as a percentage."""
        speed = getattr(self._api, "_fan_speed_treshold", None)
        if speed is None:
            return 0

        if speed == 255:
            return 100

        return (speed/self.speed_count)*100

    async def async_set_percentage(self, percentage: int) -> None:
        """
        Set the fan speed as a percentage. 0% turns the fan off.
        WARNING! Please note that state off does not necessarily mean the fan is off. Dependently on hardware settings (DIP switches enclosed in fan case) it may still run at minimum power.
        """

        if percentage == 0:
            # 0% → turn off
            await self.hass.async_add_executor_job(self._api.turn_off)
            self._attr_is_on = False
            self._attr_percentage = 0
        else:
            # Convert 0–100% → device speed step (e.g., 1–3)
            speed_treshold = math.ceil(
                percentage_to_ranged_value(self._api.FAN_SPEED_RANGE, percentage)
            )

            # Turn on and set the speed
            await self.hass.async_add_executor_job(self._api.turn_on, speed_treshold)
            self._attr_is_on = True
            self._attr_percentage = percentage

        # Notify HA of the new state
        self.async_write_ha_state()

    @property
    def preset_mode(self):
        return getattr(self._api, "operation_mode", None)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the operation mode by preset name."""
        # Find the corresponding key (mode number) for the given preset name
        mode_key = next((k for k, v in self._api.FAN_MODES.items() if v == preset_mode), None)

        if mode_key is None:
            _LOGGER.warning("Unknown preset mode: %s", preset_mode)
            return

        current_speed_treshold = self._api._fan_speed_treshold

        # Send command to the device
        await self.hass.async_add_executor_job(self._api.turn_on, current_speed_treshold, mode_key)

        # Update internal state
        self._attr_preset_mode = preset_mode
        self.async_write_ha_state()

