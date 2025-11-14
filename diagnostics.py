"""Diagnostics support for Blauberg Vento integration."""
from __future__ import annotations
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .const import DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""

    api = hass.data[DOMAIN][entry.entry_id]

    # Get device and entity registries
    device_registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)

    # Find the device linked to this entry
    devices = [
        device
        for device in device_registry.devices.values()
        if entry.entry_id in device.config_entries
    ]

    data = {
        "config_entry": {
            "entry_id": entry.entry_id,
            "title": entry.title,
            "host": entry.data.get("host"),
            "port": entry.data.get("port"),
        },
        "devices": [],
    }

    for device in devices:
        info = {
            "name": device.name,
            "manufacturer": device.manufacturer,
            "model": device.model,
            "identifiers": list(device.identifiers),
            "device_network_ip": api._device_network_ip
        }

        # Collect linked entities (optional)
        entities = [
            {
                "entity_id": entity.entity_id,
                "name": entity.name,
                "unique_id": entity.unique_id,
                "device_class": entity.device_class,
            }
            for entity in entity_registry.entities.values()
            if entity.device_id == device.id
        ]
        info["entities"] = entities

        data["devices"].append(info)

    return data
