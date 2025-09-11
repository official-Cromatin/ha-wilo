"""Entry for initializing sensors."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .providers import Providers
from .wilo_sensor import GenericWiloBinarySensor, GenericWiloSensor
from .wilo_sensor_descriptor import WiloBinarySensorDescriptor, WiloSensorDescriptor


async def async_setup_entry(hass:HomeAssistant, entry:ConfigEntry, async_add_entities):
    """Initialize all entities associated with the PumpHandlerClass."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    pump:Providers = data["pump"]

    entities:list[GenericWiloSensor | GenericWiloBinarySensor] = []
    for sensor_descriptor in pump.SENSORS:
        match sensor_descriptor:
            case WiloSensorDescriptor():
                entities.append(GenericWiloSensor(coordinator, sensor_descriptor, pump))

            case WiloBinarySensorDescriptor():
                entities.append(GenericWiloBinarySensor(coordinator, sensor_descriptor, pump))

    async_add_entities(entities)
