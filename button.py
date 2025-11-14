from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.button import ButtonEntity
from datetime import datetime

from .const import DOMAIN


class BlaubergVentoSyncTimeButton(ButtonEntity):
    """Button to sync Home Assistant time with the fan's internal RTC."""

    def __init__(self, api, device_info):
        self._api = api
        self._attr_name = "Sync Time"
        self._attr_unique_id = f"{device_info['device_id']}_sync_time"
        self._attr_icon = "mdi:clock-check-outline"
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_info["device_id"])},
        }

    async def async_press(self) -> None:
        """Handle the button press."""
        now = datetime.now()
        # Format data for your fan API
        hour = now.hour
        minute = now.minute
        second = now.second
        day = now.day
        day_of_week = now.isoweekday()
        month = now.month
        year = now.year

        try:
            await self.hass.async_add_executor_job(
                self._api.set_date_and_time,
                year,
                month,
                day,
                day_of_week,
                hour,
                minute,
                second,
            )

            self._attr_icon = "mdi:clock-check"  # optionally change icon after press

            self._attr_extra_state_attributes = {
                "last_synced": now.isoformat(timespec="seconds")
            }

        except Exception as err:
            self._attr_icon = "mdi:clock-alert-outline"
            raise err
        finally:
            self.async_write_ha_state()


class BlaubergVentoResetAlarmButton(ButtonEntity):
    """Button to reset fan's alarm"""

    def __init__(self, api, device_info):
        self._api = api
        self._attr_name = "Reset Alarm"
        self._attr_unique_id = f"{device_info['device_id']}_reset_alarm"
        self._attr_icon = "mdi:alert-circle-check-outline"
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_info["device_id"])},
        }

    async def async_press(self) -> None:
        """Handle the button press."""

        try:
            self._attr_icon = "mdi:progress-wrench"

            await self.hass.async_add_executor_job(self._api.reset_alarm_status)

            self._attr_icon = (
                "mdi:alert-circle-check-outline"  # optionally change icon after press
            )

        except Exception as err:
            self._attr_icon = "mdi:alert-circle-check-outline"
            raise err
        finally:
            self.async_write_ha_state()


class BlaubergVentoResetFilterReplacementResetButton(ButtonEntity):
    """Button to reset fan's alarm"""

    def __init__(self, api, device_info):
        self._api = api
        self._attr_name = "Reset filter replacement"
        self._attr_unique_id = f"{device_info['device_id']}_reset_filter_replacement"
        self._attr_icon = "mdi:restore"
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_info["device_id"])},
        }

    async def async_press(self) -> None:
        """Handle the button press."""

        try:
            self._attr_icon = "mdi:restore"

            await self.hass.async_add_executor_job(self._api.reset_filter_replacement)

            self._attr_icon = "mdi:restore"

        except Exception as err:
            self._attr_icon = "mdi:restore"
            raise err
        finally:
            self.async_write_ha_state()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up Blauberg Vento sensors."""
    api = hass.data[DOMAIN][entry.entry_id]
    device_id = entry.data.get("device_id", "unknown")

    # Add your device ID sensor (and others in the future)
    async_add_entities(
        [
            BlaubergVentoSyncTimeButton(api, {"device_id": device_id}),
            BlaubergVentoResetAlarmButton(api, {"device_id": device_id}),
            BlaubergVentoResetFilterReplacementResetButton(
                api, {"device_id": device_id}
            ),
        ],
        True,
    )
