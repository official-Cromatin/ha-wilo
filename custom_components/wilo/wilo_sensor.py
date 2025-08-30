"""Implements the GenericWiloSensor."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .wilo_sensor_descriptor import WiloEntityDescriptor


class GenericWiloSensor(CoordinatorEntity, SensorEntity):
    """Generic sensor class used to, in combination with WiloSensorDescriptor, create sensors for each provider."""
    def __init__(self, coordinator:DataUpdateCoordinator, descriptor: WiloEntityDescriptor, provider):
        """Initialize GenericWiloSensor.

        :param DataUpdateCoordinator coordinator:
            DataUpdateCoordinator associated with this sensor.

        :param WiloEntityDescriptor descriptor:
            Descriptor used to describe attribute values of this sensor instance.

        :param WiloProvider provider:
            Provider providing this sensor entity.
        """
        super().__init__(coordinator)
        self._attr_unique_id = f"{provider.unique_id}_{descriptor.partial_unique_entity_id}"
        self._attr_translation_key = descriptor.translation_key
        self._attr_device_class = descriptor.device_class
        self._attr_state_class = descriptor.state_class
        self._attr_native_unit_of_measurement = descriptor.native_unit_of_measurement
        self._attr_unit_of_measurement = descriptor.unit_of_measurement
        self._attr_entity_registry_enabled_default = descriptor.entity_registry_enabled_default
        self._attr_entity_category = descriptor.entity_category
        self.__update_function = descriptor.value_update_function

    @property
    def native_value(self):
        return self.__update_function(self.coordinator.data)
