"""Entry for initializing sensors."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .pumps import PumpHandlerClass


async def async_setup_entry(hass:HomeAssistant, entry:ConfigEntry, async_add_entities):
    """Initialize all entities associated with the PumpHandlerClass."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    pump:PumpHandlerClass = data["pump"]

    entities = []

    for (category_key, value_key), entity_class in pump.ENTITY_MAP.items():
        entities.append(entity_class(coordinator, pump, category_key, value_key))

    async_add_entities(entities)
