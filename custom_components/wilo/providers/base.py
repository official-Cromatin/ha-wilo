"""Defines the base class all providers inherit from."""

from abc import ABC, abstractmethod
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo

from ..const import DOMAIN
from ..datastores import Datastores
from ..models import WiloModels
from ..wilo_sensor_descriptor import WiloSensorDescriptors


class BaseProvider(ABC):
    """Base class all providers inherit from."""

    SENSORS:list[WiloSensorDescriptors]

    def __init__(self, device_ip:str, device_id:int, model:WiloModels, hass:HomeAssistant):
        """Initialize the provider class.

        :param str device_ip:
            IP adress of the pump

        :param int device_id:
            ID of the device.

        :param WiloModels model:
            Enum containing supported pump models

        :param HomeAssistant hass:
            Home assistant instance used for various tasks.
        """
        if device_id == 0:
            self._unique_id = f"{model.value}"
        else:
            self._unique_id = f"{model.value}_{device_id}"

        self._device_ip = device_ip
        self._device_id = device_id
        self._model = model
        self._hass = hass
        self._device_info:DeviceInfo | None = None
        self._logger:logging.Logger = logging.getLogger(f"{DOMAIN}_{self._unique_id}")

    @abstractmethod
    async def async_create_device_info(self):
        """Creates the device info of the pump."""

    async def async_close(self) -> None:
        """Optional cleanup."""

    @abstractmethod
    async def async_update(self) -> Datastores:
        """Fetch and normalize data. Return dict for this provider namespace."""

    @property
    def device_info(self) -> DeviceInfo | None:
        """Device info used by all associated entities.

        :returns DeviceInfo:
            DeviceInfo instance containing entity device information.

        :return None:
            DeviceInfo has not been created yet.
        """
        return self._device_info

    @property
    def unique_id(self) -> str:
        """Unique device id.

        :returns str:
            String containing the unique id. Used by entites.
        """
        return self._unique_id
