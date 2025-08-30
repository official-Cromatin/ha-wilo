"""Handles config flow for Wilo integration."""

import aiohttp
import regex as re
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .models import WiloModels


class WiloConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Wilo config flow."""
    VERSION = 1

    def __init__(self):
        self._flow_data = {}

    async def _async_verify_connectivity(self, ip_adress:str):
        """Checks the reachability of the specified IP address."""
        session = async_get_clientsession(self.hass)

        try:
            async with session.get(f"http://{ip_adress}", timeout=10) as response:
                if response.status != 200:
                    return "invalid_status"
        except aiohttp.ClientConnectorError:
            return "cannot_connect"
        except TimeoutError:
            return "timeout"

    def _async_get_id(self) -> int:
        """Returns a incremented ID for the device based on existing devices with the same model."""
        device_id = 0
        for entry in self.hass.config_entries.async_entries(domain=DOMAIN):
            if entry.data["model"] == self._flow_data["model"]:
                device_id += 1
        return device_id

    def _async_is_already_configured(self) -> bool:
        """Checks if a device with the same ip is already configured."""
        for entry in self.hass.config_entries.async_entries(domain=DOMAIN):
            if entry.data["ip"] == self._flow_data["ip"]:
                return True
        return False

    async def async_step_user(self, user_input=None):
        """Handle config flow start.

        Requests the user to enter device relevant information (adress and model)
        """
        models = [model.value for model in WiloModels]
        errors = {}
        if user_input is not None:
            if self._async_is_already_configured():
                return self.async_abort(reason="already_configured")

            pump_ip_regex = re.match("^(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", user_input["ip"])
            if pump_ip_regex is None:
                errors["base"] = "invalid_ip"
            else:
                self._flow_data["ip"] = pump_ip_regex.string

            connectivity_code = await self._async_verify_connectivity(user_input["ip"])
            if connectivity_code is not None:
                errors["base"] = connectivity_code

            self._flow_data["model"] = user_input["model"]

            if "base" in errors:
                return self.async_show_form(
                    step_id="user",
                    data_schema=vol.Schema({
                        vol.Required("ip", default=user_input["ip"]): str,
                        vol.Required("model", default=user_input["model"]): vol.In(models),
                    }),
                    errors=errors
                )
            return await self.async_step_interval()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("ip"): str,
                vol.Required("model"): vol.In(models),
            })
        )

    async def async_step_interval(self, user_input=None):
        """Handle second config flow step."""
        errors = {}
        if user_input is not None:
            if user_input["interval"] == 0:
                errors["base"] = "interval_is_zero"
            elif user_input["interval"] < 0:
                errors["base"] = "intervall_smaller_than_zero"
            else:
                self._flow_data["interval"] = user_input["interval"]

            if "base" in errors:
                return self.async_show_form(
                    step_id="interval",
                    data_schema=vol.Schema({
                        vol.Required("interval", default=60): int,
                    }),
                    errors=errors
                )

            self._flow_data["device_id"] = self._async_get_id()

            return self.async_create_entry(
                title=f"Wilo {self._flow_data["model"]} ({self._flow_data["ip"]})",
                data=self._flow_data
            )

        return self.async_show_form(
            step_id="interval",
            data_schema=vol.Schema({
                vol.Required("interval", default=60): int,
            })
        )
