import logging
_LOGGER = logging.getLogger(__name__)

import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, DEFAULT_PORT, DEFAULT_DEVICE_ID, DEFAULT_PASSWORD
from .fan_api import BlaubergVentoApi

class BlaubergVentoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Blauberg Vento fans."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            api = BlaubergVentoApi(
                user_input["host"],
                port=user_input["port"],
                name=user_input["name"],
                device_id=user_input["device_id"],
                password=user_input["password"],
            )
            try:
                await self.hass.async_add_executor_job(api.get_device_info)
                await self.hass.async_add_executor_job(api.get_firmware_version)
            except Exception as e:
                _LOGGER.warning("Connection failed: %s", e)
                errors["base"] = "cannot_connect"

            # --- Connection validation logic ---
            if api.device_id == DEFAULT_DEVICE_ID and user_input["device_id"] == DEFAULT_DEVICE_ID:
                # Device ID didn't change and user didn't provide one manually
                _LOGGER.warning(
                    "Device %s did not respond with a valid ID; setup aborted", user_input["host"]
                )
                errors["base"] = "cannot_connect"

            # If any error occurred, re-show the form
            if errors:
                return self.async_show_form(
                    step_id="user",
                    data_schema=self._schema(user_input),
                    errors=errors,
                )

            # Create unique ID based on device_id
            await self.async_set_unique_id(api.device_id)
            self._abort_if_unique_id_configured()
            user_input["device_id"] = api.device_id
            user_input["device_model_id"] = api.device_model_id
            _LOGGER.debug("User added Blauberg Vento device: %s", user_input)

            return self.async_create_entry(title=user_input["name"], data=user_input)

        # Initial form
        return self.async_show_form(
            step_id="user",
            data_schema=self._schema(),
            errors=errors,
        )

    def _schema(self, defaults=None):
        """Return config schema with optional defaults."""
        defaults = defaults or {}
        return vol.Schema({
            vol.Required("name", default=defaults.get("name", "")): str,
            vol.Required("host", default=defaults.get("host", "")): str,
            vol.Optional("port", default=defaults.get("port", DEFAULT_PORT)): int,
            vol.Optional("device_id", default=defaults.get("device_id", DEFAULT_DEVICE_ID)): str,
            vol.Optional("password", default=defaults.get("password", DEFAULT_PASSWORD)): str,
        })