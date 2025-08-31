"""Implements the provider for rain3 pump."""

import re
from typing import Any

from aiohttp import ClientError, ClientResponseError, ClientSession

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo

from ..const import DOMAIN
from ..datastores import Rain3Datastore
from ..models import WiloModels
from .base import BaseProvider


class Rain3Provider(BaseProvider):
    """Provider class for rain3 pump."""

    SENSORS = []

    def __init__(self, device_ip, device_id, hass):
        """Initialize rain3 provider class.

        :param str device_ip:
            IP adress of rain3 pump.

        :param int device_id:
            ID of the device.

        :param HomeAssistant hass:
            Home assistant instance used for various tasks.
        """
        super().__init__(device_ip, device_id, WiloModels.RAIN3, hass)
        self.__client_session:ClientSession | None = None

    @property
    def session(self) -> ClientSession:
        """Cached home assistant aiohttp client session."""
        if self.__client_session is None:
            self.__client_session = async_get_clientsession(self._hass)
        return self.__client_session

    async def async_create_device_info(self):
        """Creates device info for rain3 pump."""
        device_data = await self.async_update()

        self._device_info = DeviceInfo(
            configuration_url=f"http://{self._device_ip}",
            connections={("ip", self._device_ip)},
            identifiers={(DOMAIN, self._unique_id)},
            manufacturer=DOMAIN.capitalize(),
            model=self._model.value.capitalize(),
            name=f"{DOMAIN.capitalize()} {self._model.value.capitalize()} ({self._device_ip})",
            serial_number=device_data.serial_number,
            sw_version=device_data.software_version,
        )

    async def async_update(self) -> Rain3Datastore:
        combined_data:dict[str, dict[str, Any]] = {}

        for url_path in ["identity", "state", "download"]:
            html = await self.__fetch_html(url_path)
            partial_data = {}
            pattern = re.compile(r"<span[^>]*>(.*?)</span>\s*<b>(.*?)(?:<br>|</b>)", re.DOTALL)
            for match in pattern.finditer(html):
                key = match.group(1).strip().rstrip(":")
                value = match.group(2).strip()
                partial_data[key] = value
            combined_data[url_path] = partial_data

        for url_path in ["setup", "installation", "settings"]:
            html = await self.__fetch_html(url_path)
            partial_data = {}
            pattern = re.compile(r"<span[^>]*>(.*?)</span>\s*<b>(.*?)</b>", re.DOTALL)
            for match in pattern.finditer(html):
                raw_key = match.group(1).strip()
                value = match.group(2).strip()

                clean_key = re.sub(r"^\d+(\.\d+)*\s*", "", raw_key)
                clean_key = re.sub(r"^E\d+(?:\.\d+)?\s*", "", clean_key)
                clean_key = clean_key.rstrip(":")

                if clean_key.lower().startswith("last occur"):
                    continue

                partial_data[clean_key] = value
            combined_data[url_path] = partial_data

        for url_path in ["errors"]:
            html = await self.__fetch_html(url_path)
            alarm_match = re.search(r"<h2>Alarm</h2>(.*?)<br>", html, re.DOTALL)
            if alarm_match:
                alarm_text = alarm_match.group(1).strip()
            combined_data[url_path] = alarm_text

        return Rain3Datastore(combined_data)

    async def __fetch_html(self, url_path:str, timeout:int = 10) -> str | None:
        """Loads the contents of the webpage and returns them.

        Errors are silently ignored and logged directly to ha.

        :param str url_path:
            Path of the url to the requested webpage.

        :param int timeout:
            Timeout in seconds before the request fails with a timeout error.

        :returns str:
            Content of the response.

        :returns None:
            An error occured.
        """
        try:
            async with self.session.get(f"http://{self._device_ip}/{url_path}", timeout=timeout) as response:
                if response.status != 200:
                    self._logger.warning("Unexpected response status %s while fetching %s", response.status, url_path)

                return await response.text()
        except TimeoutError:
            self._logger.warning("Timeout after %s seconds while fetching %s", timeout, url_path)
        except ClientResponseError as err:
            self._logger.warning("Client response error while fetching %s: %s", url_path, err)
        except ClientError as err:
            self._logger.warning("Client error while fetching %s: %s", url_path, err)
