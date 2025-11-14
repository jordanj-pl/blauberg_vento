"""Support for Blauberg Vento Fans"""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from .const import DOMAIN, DEFAULT_PORT, DEFAULT_DEVICE_ID, DEFAULT_PASSWORD
from .fan_api import BlaubergVentoApi


PLATFORMS = ["fan", "sensor", "button", "switch"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up one Blauberg Vento device."""
    data = entry.data
    host = data["host"]
    port = data.get("port", DEFAULT_PORT)
    name = data.get("name")
    device_id = data.get("device_id", DEFAULT_DEVICE_ID)
    password = data.get("password", DEFAULT_PASSWORD)

    # Create device API instance
    api = BlaubergVentoApi(
        host,
        port=port,
        name=name,
        device_id=device_id,
        password=password
    )
    api._device_model_id = data.get("device_model_id")

    # Store instance in hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = api

    # Fetch firmware version once (non-blocking)
    await hass.async_add_executor_job(api.get_firmware_version)
    await hass.async_add_executor_job(api.get_network_info)

     # Forward setup to supported platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register integration services
    # hass.services.async_register(
    #     DOMAIN,
    #     "set_percentage",
    #     handle_set_percentage,
    # )

    # hass.services.async_register(
    #     DOMAIN,
    #     "set_preset_mode",
    #     handle_set_preset_mode,
    # )

    # hass.services.async_register(DOMAIN, "set_percentage", handle_set_percentage)
    # hass.services.async_register(DOMAIN, "set_preset_mode", handle_set_preset_mode)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

# async def handle_set_percentage(call):
#     entity_id = call.data["entity_id"]
#     percentage = call.data["percentage"]
#     entity = hass.data[DOMAIN]["entities"][entity_id]
#     await entity.async_set_percentage(percentage)

# async def handle_set_preset_mode(call):
#     entity_id = call.data["entity_id"]
#     mode = call.data["preset_mode"]
#     entity = hass.data[DOMAIN]["entities"][entity_id]
#     await entity.async_set_preset_mode(mode)

#from . import device_action