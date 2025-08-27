"""Class to represent the Rain3 pump."""
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo

from ..const import DOMAIN
from ..entities import (
    CalcProtectionTimerSensor,
    CisternLevelSensor,
    FlushingTimerSensor,
    PumpPressureSensor,
    PumpStateSensor,
    ThreeWayValvePositionSensor,
    PumpRuntimeSensor
)
from ..parsers import AlarmParser, SettingsParser, StatusParser
from .base import BasePump


class Rain3Pump(BasePump):
    """Represents the Wilo Rain3 pump model."""

    ENTITY_MAP = {
        ("state", "MP"): PumpStateSensor,
        ("state", "Level"): CisternLevelSensor,
        ("state", "Pressure"): PumpPressureSensor,
        ("state", "3 Ways-valve"): ThreeWayValvePositionSensor,
        ("state", "Calc. protection in"): CalcProtectionTimerSensor,
        ("state", "Flushing in"): FlushingTimerSensor,
        ("state", "MP running for"): PumpRuntimeSensor,
    }

    def __init__(self, ip:str, device_id:int):
        super().__init__(
            ip,
            device_id,
            "rain3",
            {
                "identity": StatusParser,
                "state": StatusParser,
                "setup": SettingsParser,
                "errors": AlarmParser,
                "installation": SettingsParser,
                "settings": SettingsParser,
                "download": StatusParser
            }
        )

    async def create_device_info(self, hass:HomeAssistant):
        device_data = await self.update(hass)

        self._device_info = DeviceInfo(
            configuration_url=f"http://{self._ip}",
            connections={("ip", self._ip)},
            identifiers={(DOMAIN, self._unique_id)},
            manufacturer=DOMAIN.capitalize(),
            model=self._model.capitalize(),
            name=f"{DOMAIN.capitalize()} {self._model.capitalize()} ({self._ip})",
            serial_number=device_data["identity"]["Serial number"],
            sw_version=device_data["identity"]["SW Version"],
        )
