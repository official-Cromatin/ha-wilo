"""Entry for initializing sensors."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .providers import Providers
from .wilo_sensor import GenericWiloSensor


async def async_setup_entry(hass:HomeAssistant, entry:ConfigEntry, async_add_entities):
    """Initialize all entities associated with the PumpHandlerClass."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    pump:Providers = data["pump"]

    entities:list[GenericWiloSensor] = [GenericWiloSensor(coordinator, sensor_descriptor, pump) for sensor_descriptor in pump.SENSORS]
    async_add_entities(entities)
