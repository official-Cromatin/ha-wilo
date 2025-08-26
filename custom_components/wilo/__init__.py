"""Add Wilo integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import timedelta

from .const import DOMAIN
from .coordinator import WiloCoordinator
from .pumps import Rain3Pump


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Rain3 Wilo from a config entry."""

    logger = logging.getLogger(DOMAIN)

    ip:str = entry.data["ip"]
    model:str = entry.data["model"]
    interval:int = entry.data["interval"]
    device_id:int = entry.data["device_id"]

    match model:
        case "rain3":
            pump = Rain3Pump(ip, device_id)
    await pump.create_device_info(hass)

    coordinator = WiloCoordinator(
        hass,
        logger,
        timedelta(seconds=interval),
        f"Wilo {model} ({entry.entry_id})",
        pump
        )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "pump": pump
    }

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True
