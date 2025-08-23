"""Class all pumps inherit from. Implements common methods."""
from parsers import AlarmParser, SettingsParser, StatusParser

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession


class BasePump:
    """Base pump class for Wilo pump integration."""

    def __init__(self, ip:str, urls:dict[str, AlarmParser | SettingsParser | StatusParser]):
        self._ip = ip
        self._urls = urls

    @staticmethod
    async def fetch_ressource(hass:HomeAssistant, url:str) -> str:
        """Fetches the ressource via HTTP GET."""
        session = async_get_clientsession(hass)

        async with session.get(url, timeout=10) as response:
            return await response.text()

    async def update(self, hass:HomeAssistant) -> dict:
        """Updates the coordinator data by fetching all urls and combining the data to one singular dictionary."""
        session = async_get_clientsession(hass)
        combined_data = {}
        for path, parser in self._urls.items():
            async with session.get(f"http://{self._ip}/{path}", timeout=10) as response:
                html = await response.text()

            data = parser.parse(html)
            combined_data[path] = data
        return combined_data
