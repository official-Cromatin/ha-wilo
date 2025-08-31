"""Coordinator to handle updates."""

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .providers import Providers


class WiloCoordinator(DataUpdateCoordinator):
    """Class to regularly fetch new data."""
    def __init__(self, hass, logger, update_interval, name, pump:Providers):
        """Initialize Wilo Coordinator."""
        super().__init__(hass, logger, update_interval=update_interval, name=name)
        self.__pump = pump

    async def _async_update_data(self):
        return await self.__pump.async_update()
