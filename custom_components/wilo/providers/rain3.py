"""Implements the provider for rain3 pump."""

import re

from aiohttp import ClientError, ClientResponseError, ClientSession
from lxml import html as lxml_html

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import (
    EntityCategory,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import UnitOfLength, UnitOfPressure, UnitOfTime
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo

from ..const import DOMAIN
from ..datastores import Rain3Datastore
from ..models import WiloModels
from ..wilo_sensor_descriptor import WiloBinarySensorDescriptor, WiloSensorDescriptor
from .base import BaseProvider


class Rain3Provider(BaseProvider):
    """Provider class for rain3 pump."""

    SENSORS = [
        WiloSensorDescriptor(
            partial_unique_entity_id = "serial_number",
            translation_key = "serial_number",
            value_update_function = lambda data: data.serial_number,
            entity_category = EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default = False
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "software_version",
            translation_key = "software_version",
            value_update_function = lambda data: data.software_version,
            entity_category = EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default = False
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "equipment_number",
            translation_key = "equipment_number",
            value_update_function = lambda data: data.equipment_number,
            entity_category = EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default = False
        ),
        WiloBinarySensorDescriptor(
            partial_unique_entity_id = "state",
            translation_key = "state",
            value_update_function = lambda data: data.is_pump_running,
            device_class = BinarySensorDeviceClass.RUNNING,
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "running_duration",
            translation_key = "running_duration",
            value_update_function = lambda data: data.main_pump_current_runtime,
            device_class = SensorDeviceClass.DURATION,
            native_unit_of_measurement = UnitOfTime.SECONDS,
            unit_of_measurement = UnitOfTime.MINUTES,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "pressure",
            translation_key = "pressure",
            value_update_function = lambda data: data.pump_pressure,
            device_class = SensorDeviceClass.PRESSURE,
            native_unit_of_measurement = UnitOfPressure.BAR
        ),
        WiloBinarySensorDescriptor(
            partial_unique_entity_id = "on_pressure_reached",
            translation_key = "on_pressure_reached",
            value_update_function = lambda data: data.is_switch_on_pressure_reached,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloBinarySensorDescriptor(
            partial_unique_entity_id = "off_pressure_reached",
            translation_key = "off_pressure_reached",
            value_update_function = lambda data: data.is_switch_off_pressure_reached,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "mp_stop_in",
            translation_key = "mp_stop_in",
            value_update_function = lambda data: data.main_pump_stop_in,
            device_class = SensorDeviceClass.DURATION,
            native_unit_of_measurement = UnitOfTime.SECONDS,
            unit_of_measurement = UnitOfTime.SECONDS,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "cistern_level",
            translation_key = "cistern_level",
            value_update_function = lambda data: data.cistern_level,
            device_class = SensorDeviceClass.DISTANCE,
            native_unit_of_measurement = UnitOfLength.CENTIMETERS,
            unit_of_measurement = UnitOfLength.CENTIMETERS,
            state_class = SensorStateClass.MEASUREMENT
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "valve_position",
            translation_key = "valve_position",
            value_update_function = lambda data: data.valve_position,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "calc_protection_timer",
            translation_key = "calc_protection_timer",
            value_update_function = lambda data: data.calc_protection_timer,
            device_class = SensorDeviceClass.DURATION,
            unit_of_measurement = UnitOfTime.HOURS,
            native_unit_of_measurement = UnitOfTime.HOURS,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "flushing_timer",
            translation_key = "flushing_timer",
            value_update_function = lambda data: data.flushing_timer,
            device_class = SensorDeviceClass.DURATION,
            unit_of_measurement = UnitOfTime.HOURS,
            native_unit_of_measurement = UnitOfTime.HOURS,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "pump_switches_this_hour",
            translation_key = "pump_switches_this_hour",
            value_update_function = lambda data: data.pump_switches_this_hour,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "system_hours",
            translation_key = "system_hours",
            value_update_function = lambda data: data.system_total_runtime,
            device_class = SensorDeviceClass.DURATION,
            native_unit_of_measurement = UnitOfTime.HOURS,
            unit_of_measurement = UnitOfTime.HOURS,
            state_class = SensorStateClass.TOTAL_INCREASING,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "mp_hours",
            translation_key = "mp_hours",
            value_update_function = lambda data: data.main_pump_total_runtime,
            device_class = SensorDeviceClass.DURATION,
            native_unit_of_measurement = UnitOfTime.HOURS,
            unit_of_measurement = UnitOfTime.HOURS,
            state_class = SensorStateClass.TOTAL_INCREASING,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC,
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "cp_hours",
            translation_key = "cp_hours",
            value_update_function = lambda data: data.cistern_pump_total_runtime,
            device_class = SensorDeviceClass.DURATION,
            native_unit_of_measurement = UnitOfTime.HOURS,
            unit_of_measurement = UnitOfTime.HOURS,
            state_class = SensorStateClass.TOTAL_INCREASING,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "system_switches",
            translation_key = "system_switches",
            value_update_function = lambda data: data.system_switches_counter,
            state_class = SensorStateClass.TOTAL_INCREASING,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "mp_switches",
            translation_key = "mp_switches",
            value_update_function = lambda data: data.main_pump_switches_counter,
            state_class = SensorStateClass.TOTAL_INCREASING,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "cp_switches",
            translation_key = "cp_switches",
            value_update_function = lambda data: data.cistern_pump_switches_counter,
            state_class = SensorStateClass.TOTAL_INCREASING,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "mp_type",
            translation_key = "mp_type",
            value_update_function = lambda data: data.main_pump_type,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC,
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "cp_count",
            translation_key = "cp_count",
            value_update_function = lambda data: data.cistern_pump_count,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "pressure_range",
            translation_key = "pressure_range",
            value_update_function = lambda data: data.pressure_range,
            device_class = SensorDeviceClass.PRESSURE,
            native_unit_of_measurement = UnitOfPressure.BAR,
            unit_of_measurement = UnitOfPressure.BAR,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "over_pressure_threshold",
            translation_key = "over_pressure_threshold",
            value_update_function = lambda data: data.over_pressure_threshold,
            device_class = SensorDeviceClass.PRESSURE,
            native_unit_of_measurement = UnitOfPressure.BAR,
            unit_of_measurement = UnitOfPressure.BAR,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "cistern_sensor_range",
            translation_key = "cistern_sensor_range",
            value_update_function = lambda data: data.cistern_sensor_range,
            device_class = SensorDeviceClass.DISTANCE,
            native_unit_of_measurement = UnitOfLength.METERS,
            unit_of_measurement = UnitOfLength.METERS,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "cistern_sensor_installed_height",
            translation_key = "cistern_sensor_installed_height",
            value_update_function = lambda data: data.cistern_sensor_installed_height,
            device_class = SensorDeviceClass.DISTANCE,
            native_unit_of_measurement = UnitOfLength.CENTIMETERS,
            unit_of_measurement = UnitOfLength.CENTIMETERS,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "high_water_threshold",
            translation_key = "high_water_threshold",
            value_update_function = lambda data: data.high_water_threshold,
            device_class = SensorDeviceClass.DISTANCE,
            native_unit_of_measurement = UnitOfLength.CENTIMETERS,
            unit_of_measurement = UnitOfLength.CENTIMETERS,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "cistern_shape",
            translation_key = "cistern_shape",
            value_update_function = lambda data: data.cistern_shape,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "cistern_height_or_diameter",
            translation_key = "cistern_height_or_diameter",
            value_update_function = lambda data: data.cistern_height_or_diameter,
            device_class = SensorDeviceClass.DISTANCE,
            native_unit_of_measurement = UnitOfLength.CENTIMETERS,
            unit_of_measurement = UnitOfLength.CENTIMETERS,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloBinarySensorDescriptor(
            partial_unique_entity_id = "pump_kick",
            translation_key = "pump_kick",
            value_update_function = lambda data: data.pump_kick_enabled,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "pump_kick_interval",
            translation_key = "pump_kick_interval",
            value_update_function = lambda data: data.pump_kick_interval,
            device_class = SensorDeviceClass.DURATION,
            native_unit_of_measurement = UnitOfTime.HOURS,
            unit_of_measurement = UnitOfTime.HOURS,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "pump_kick_duration",
            translation_key = "pump_kick_duration",
            value_update_function = lambda data: data.pump_kick_interval,
            device_class = SensorDeviceClass.DURATION,
            native_unit_of_measurement = UnitOfTime.SECONDS,
            unit_of_measurement = UnitOfTime.SECONDS,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "over_flow_threshold",
            translation_key = "over_flow_threshold",
            value_update_function = lambda data: data.over_flow_threshold,
            device_class = SensorDeviceClass.DISTANCE,
            native_unit_of_measurement = UnitOfLength.CENTIMETERS,
            unit_of_measurement = UnitOfLength.CENTIMETERS,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "tap_water_threshold",
            translation_key = "tap_water_threshold",
            value_update_function = lambda data: data.tap_water_threshold,
            device_class = SensorDeviceClass.DISTANCE,
            native_unit_of_measurement = UnitOfLength.CENTIMETERS,
            unit_of_measurement = UnitOfLength.CENTIMETERS,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "rain_water_threshold",
            translation_key = "rain_water_threshold",
            value_update_function = lambda data: data.rain_water_threshold,
            device_class = SensorDeviceClass.DISTANCE,
            native_unit_of_measurement = UnitOfLength.CENTIMETERS,
            unit_of_measurement = UnitOfLength.CENTIMETERS,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "calcination_protection_interval",
            translation_key = "calcination_protection_interval",
            value_update_function = lambda data: data.calcination_protection_interval,
            device_class = SensorDeviceClass.DURATION,
            native_unit_of_measurement = UnitOfTime.DAYS,
            unit_of_measurement = UnitOfTime.DAYS,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "flushing_interval",
            translation_key = "flushing_interval",
            value_update_function = lambda data: data.flushing_interval,
            device_class = SensorDeviceClass.DURATION,
            native_unit_of_measurement = UnitOfTime.DAYS,
            unit_of_measurement = UnitOfTime.DAYS,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "flushing_duration",
            translation_key = "flushing_duration",
            value_update_function = lambda data: data.flushing_duration,
            device_class = SensorDeviceClass.DURATION,
            native_unit_of_measurement = UnitOfTime.MINUTES,
            unit_of_measurement = UnitOfTime.MINUTES,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "pump_max_runtime",
            translation_key = "pump_max_runtime",
            value_update_function = lambda data: data.pump_max_runtime,
            device_class = SensorDeviceClass.DURATION,
            native_unit_of_measurement = UnitOfTime.MINUTES,
            unit_of_measurement = UnitOfTime.MINUTES,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "fault_message_behavior",
            translation_key = "fault_message_behavior",
            value_update_function = lambda data: data.fault_message_behavior,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "minimum_pressure",
            translation_key = "minimum_pressure",
            value_update_function = lambda data: data.minimum_pressure,
            device_class = SensorDeviceClass.PRESSURE,
            native_unit_of_measurement = UnitOfPressure.BAR,
            unit_of_measurement = UnitOfPressure.BAR,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "dry_run_delay",
            translation_key = "dry_run_delay",
            value_update_function = lambda data: data.dry_run_delay,
            device_class = SensorDeviceClass.DURATION,
            native_unit_of_measurement = UnitOfTime.SECONDS,
            unit_of_measurement = UnitOfTime.SECONDS,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "dry_run_tap_water",
            translation_key = "dry_run_tap_water",
            value_update_function = lambda data: data.dry_run_tap_water,
            device_class = SensorDeviceClass.DURATION,
            native_unit_of_measurement = UnitOfTime.SECONDS,
            unit_of_measurement = UnitOfTime.SECONDS,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "dry_run_rain_water",
            translation_key = "dry_run_rain_water",
            value_update_function = lambda data: data.dry_run_rain_water,
            device_class = SensorDeviceClass.DURATION,
            native_unit_of_measurement = UnitOfTime.SECONDS,
            unit_of_measurement = UnitOfTime.SECONDS,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "maximum_pump_cycles_per_hour",
            translation_key = "maximum_pump_cycles_per_hour",
            value_update_function = lambda data: data.max_pump_cycles_alarm_count,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "switch_on_pressure",
            translation_key = "switch_on_pressure",
            value_update_function = lambda data: data.switch_on_pressure,
            device_class = SensorDeviceClass.PRESSURE,
            native_unit_of_measurement = UnitOfPressure.BAR,
            unit_of_measurement = UnitOfPressure.BAR,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "switch_off_pressure",
            translation_key = "switch_off_pressure",
            value_update_function = lambda data: data.switch_off_pressure,
            device_class = SensorDeviceClass.PRESSURE,
            native_unit_of_measurement = UnitOfPressure.BAR,
            unit_of_measurement = UnitOfPressure.BAR,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "mp_stop_delay",
            translation_key = "mp_stop_delay",
            value_update_function = lambda data: data.cistern_pump_start_time,
            device_class = SensorDeviceClass.DURATION,
            native_unit_of_measurement = UnitOfTime.SECONDS,
            unit_of_measurement = UnitOfTime.SECONDS,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "cp_start_time",
            translation_key = "cp_start_time",
            value_update_function = lambda data: data.cistern_pump_start_time,
            device_class = SensorDeviceClass.DURATION,
            native_unit_of_measurement = UnitOfTime.SECONDS,
            unit_of_measurement = UnitOfTime.SECONDS,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "cp_stop_time",
            translation_key = "cp_stop_time",
            value_update_function = lambda data: data.cistern_pump_stop_time,
            device_class = SensorDeviceClass.DURATION,
            native_unit_of_measurement = UnitOfTime.SECONDS,
            unit_of_measurement = UnitOfTime.SECONDS,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "pressure_delta_tap_water",
            translation_key = "pressure_delta_tap_water",
            value_update_function = lambda data: data.pressure_delta_for_tap_water,
            device_class = SensorDeviceClass.PRESSURE,
            native_unit_of_measurement = UnitOfPressure.BAR,
            unit_of_measurement = UnitOfPressure.BAR,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "pressure_reduction_interval",
            translation_key = "pressure_reduction_interval",
            value_update_function = lambda data: data.interval_for_switch_off_pressure_reduction,
            device_class = SensorDeviceClass.DURATION,
            native_unit_of_measurement = UnitOfTime.SECONDS,
            unit_of_measurement = UnitOfTime.SECONDS,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "pressure_reduction_amount",
            translation_key = "pressure_reduction_amount",
            value_update_function = lambda data: data.pressure_reduction_amount,
            device_class = SensorDeviceClass.PRESSURE,
            native_unit_of_measurement = UnitOfPressure.BAR,
            unit_of_measurement = UnitOfPressure.BAR,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloBinarySensorDescriptor(
            partial_unique_entity_id = "drives_enabled",
            translation_key = "drives_enabled",
            value_update_function = lambda data: data.is_drive_on,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "mp_mode",
            translation_key = "mp_mode",
            value_update_function = lambda data: data.main_pump_mode,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "cp_mode",
            translation_key = "cp_mode",
            value_update_function = lambda data: data.main_pump_mode,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "mp_manual_runtime",
            translation_key = "mp_manual_runtime",
            value_update_function = lambda data: data.main_pump_manual_runtime,
            device_class = SensorDeviceClass.DURATION,
            native_unit_of_measurement = UnitOfTime.SECONDS,
            unit_of_measurement = UnitOfTime.SECONDS,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloSensorDescriptor(
            partial_unique_entity_id = "cp_manual_runtime",
            translation_key = "cp_manual_runtime",
            value_update_function = lambda data: data.cistern_pump_manual_runtime,
            device_class = SensorDeviceClass.DURATION,
            native_unit_of_measurement = UnitOfTime.SECONDS,
            unit_of_measurement = UnitOfTime.SECONDS,
            entity_registry_enabled_default = False,
            entity_category = EntityCategory.DIAGNOSTIC
        ),
        WiloBinarySensorDescriptor(
            partial_unique_entity_id = "alarm_active",
            translation_key = "alarm_active",
            value_update_function = lambda data: data.is_alarm_active,
            extra_value_update_function = lambda data: data.alarm_data,
            device_class = BinarySensorDeviceClass.PROBLEM
        )
    ]

    _RE_LEADING_NUM = re.compile(r"^\s*\d+(\.\d+)*\s*")
    _RE_E_CODE = re.compile(r"^\s*E\d+(?:\.\d+)?\s*")
    _RE_TRAILING_COLON = re.compile(r":\s*$")

    def __init__(self, device_ip, device_id, hass):
        """Initialize rain3 provider class.

        :param str device_ip:
            IP adress of rain3 pump.

        :param int device_id:
            ID of the device.

        :param HomeAssistant hass:
            Home assistant instance used for various tasks.
        """
        super().__init__(device_ip, device_id, WiloModels.RAIN3, hass)
        self.__client_session:ClientSession | None = None

    @property
    def session(self) -> ClientSession:
        """Cached home assistant aiohttp client session."""
        if self.__client_session is None:
            self.__client_session = async_get_clientsession(self._hass)
        return self.__client_session

    async def async_create_device_info(self):
        """Creates device info for rain3 pump."""
        device_data = await self.async_update()

        self._device_info = DeviceInfo(
            configuration_url=f"http://{self._device_ip}",
            connections={("ip", self._device_ip)},
            identifiers={(DOMAIN, self._unique_id)},
            manufacturer=DOMAIN.capitalize(),
            model=self._model.value.capitalize(),
            name=f"{DOMAIN.capitalize()} {self._model.value.capitalize()} ({self._device_ip})",
            serial_number=device_data.serial_number,
            sw_version=device_data.software_version,
        )

    async def async_update(self):
        """Update the Datastore in the DataUpdateCoordinator."""
        combined_data = {}
        for url_path in ["identity", "state", "download", "setup", "installation", "settings", "errors"]:
            html = await self.__fetch_html(url_path)
            if not html:
                combined_data[url_path] = {}
                continue

            if url_path == "errors":
                parsed = self._parse_errors_page(html)
            else:
                parsed = self._parse_html(html)

            combined_data[url_path] = parsed
        return Rain3Datastore(combined_data)

    def _clean_key(self, raw_key: str) -> str:
        """Cleans the given key removing setting numbers and error codes.

        :param str raw_key:
            String to be cleaned.

        :returns str:
            Cleaned key.
        """
        key = raw_key.strip()
        key = self._RE_LEADING_NUM.sub("", key)
        key = self._RE_E_CODE.sub("", key)
        key = self._RE_TRAILING_COLON.sub("", key)
        return key.strip()

    def _clean_value(self, raw_value: str | None) -> str:
        """Cleans the given value.

        :param str | None raw_value:
            String to be cleaned, can be None.

        :returns str:
            Cleaned value.
        """
        if not raw_value:
            return ""
        value = raw_value.replace("\x00", "").strip()
        return re.sub(r"<br\s*/?>", "", value, flags=re.IGNORECASE).strip()

    def _parse_html(self, html: str) -> dict[str, str]:
        """Default parser for pages using the following format: `<span>...<b>...</b>`.

        :param str html:
            HTML as string to be parsed.

        :returns dict[str, str]:
            Dictionary containing parsed data from the given input html document.
        """
        root = lxml_html.fromstring(html.replace("\x00", ""))
        results: dict[str, str] = {}

        for span in root.xpath("//span"):
            raw_key = span.text_content() or ""
            b = span.xpath("following::b[1]")
            if not b:
                continue

            raw_value = b[0].text_content() or ""
            key = self._clean_key(raw_key)
            if not key or key.lower().startswith("last occur"):
                continue

            value = self._clean_value(raw_value)
            results[key] = value

        return results

    def _parse_errors_page(self, html: str) -> dict[str, str]:
        """Specialized parser used for error-endpoint to extract additional fields like alarm history.

        :param str html:
            HTML as string to be parsed.

        :returns dict[str, str]:
            Dictionary containing parsed data from the given input html document.
        """
        root = lxml_html.fromstring(html.replace("\x00", ""))
        results: dict[str, str] = {}

        results.update(self._parse_html(html))

        alarm_text = root.xpath("string(//h2[normalize-space()='Alarm']/following-sibling::text()[1])")
        if alarm_text:
            results["Alarm"] = self._clean_value(alarm_text)

        history = []
        b_tags = root.xpath("//h3[normalize-space()='Alarm history']/following-sibling::b")
        for b in b_tags:
            timestamp = self._clean_value(b.text_content())
            prev = b.getprevious()
            if prev is not None and prev.tail:
                error_text = self._clean_value(prev.tail)
            else:
                error_text = self._clean_value(b.xpath("preceding-sibling::text()[1]")[0] if b.xpath("preceding-sibling::text()[1]") else "")
            history.append({"error": error_text, "timestamp": timestamp})

        if history:
            results["Alarm history"] = history

        return results

    async def __fetch_html(self, url_path:str, timeout:int = 10) -> str | None:
        """Loads the contents of the webpage and returns them.

        Errors are silently ignored and logged directly to ha.

        :param str url_path:
            Path of the url to the requested webpage.

        :param int timeout:
            Timeout in seconds before the request fails with a timeout error.

        :returns str:
            Content of the response.

        :returns None:
            An error occured.
        """
        try:
            async with self.session.get(f"http://{self._device_ip}/{url_path}", timeout=timeout) as response:
                if response.status != 200:
                    self._logger.warning("Unexpected response status %s while fetching %s", response.status, url_path)

                return await response.text()
        except TimeoutError:
            self._logger.warning("Timeout after %s seconds while fetching %s", timeout, url_path)
        except ClientResponseError as err:
            self._logger.warning("Client response error while fetching %s: %s", url_path, err)
        except ClientError as err:
            self._logger.warning("Client error while fetching %s: %s", url_path, err)
