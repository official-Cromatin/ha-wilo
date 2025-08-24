"""Class all pumps inherit from. Implements common methods."""
from abc import abstractmethod
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo

from ..entities import WiloEntities
from ..parsers import WiloParser


class BasePump:
    """Base pump class for Wilo pump integration."""

    ENTITY_MAP: dict[tuple[str, str], WiloEntities]

    def __init__(self, ip:str, model:str, urls:dict[str, WiloParser]):
        self._ip = ip
        self._model = model
        self._urls = urls
        self._unique_id:str
        self._device_info: DeviceInfo

    @abstractmethod
    async def create_device_info(self):
        """Creates the device info of the pump."""
        ...

    async def update(self, hass:HomeAssistant) -> dict[str, dict[str, Any]]:
        """Updates the coordinator data by fetching all urls and combining the data to one singular dictionary."""
        session = async_get_clientsession(hass)
        combined_data = {}
        for path, parser in self._urls.items():
            async with session.get(f"http://{self._ip}/{path}", timeout=10) as response:
                html = await response.text()

            data = parser.parse(html)
            combined_data[path] = data
        return combined_data

    @property
    def device_info(self):
        """Device info used by all associated entities."""
        return self._device_info

    @property
    def unique_id(self):
        """Unique device id."""
        return self._unique_id
