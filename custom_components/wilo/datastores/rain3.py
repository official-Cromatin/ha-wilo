"""Implements the datastore for the rain3 pump."""

from datetime import timedelta
from enum import IntEnum

import regex as re

from .base import BaseDatastore


class TimeUnit(IntEnum):
    """Contains conversion factors for converting strings into times."""
    SECONDS = 1
    MINUTES = 60
    HOURS = 3600
    DAYS = 86400


class Rain3Datastore(BaseDatastore):
    """Datastore used to make fetched data accessible to rain3 sensors."""

    @property
    def serial_number(self) -> str:
        """Serial number of the pump."""
        return self._data["identity"]["Serial number"]

    @property
    def software_version(self) -> str:
        """Software version running on the controller."""
        return self._data["identity"]["SW Version"]

    @property
    def equipment_number(self) -> str:
        """Equipment number of the pump."""
        return self._data["identity"]["Equipment number"]

    @property
    def is_alarm_active(self) -> str:
        """True if a alarm is currently active."""
        return self._data["errors"]["Alarm"] != "No active alarm"

    @property
    def active_alarm(self) -> str:
        """Alarm field text."""
        return self._data["errors"]["Alarm"]

    @property
    def alarm_history(self) -> list:
        """History of last occured alarms."""
        return self._data["errors"]["Alarm history"]

    @property
    def alarm_data(self) -> dict:
        """Property combining both `active_alarm` and `alarm_history` into one dictionary."""
        return {
            "current": self.active_alarm,
            "history": self.alarm_history,
        }

    @property
    def is_pump_running(self) -> bool:
        """Indicator if the pump is running."""
        return self._data["state"]["MP"] == "ON"

    @property
    def pump_pressure(self) -> float:
        """Currently measured pressure."""
        return float(self._data["state"]["Pressure"].lower().replace("bar", "").strip())

    @property
    def cistern_level(self) -> int:
        """Fill level of the cistern."""
        return float(self._data["state"]["Level"].lower().replace("cm", "").strip())

    @property
    def valve_position(self) -> str:
        """Position of the three way valve."""
        return self._data["state"]["Ways-valve"].lower().replace(" ", "_")

    @property
    def calc_protection_timer(self) -> int:
        """Remaining time in hours for the calc. protection timer."""
        return self.__calculate_time_from_string(self._data["state"]["Calc. protection in"], TimeUnit.HOURS)

    @property
    def flushing_timer(self) -> int:
        """Remaining time in hours for the flushing timer."""
        return self.__calculate_time_from_string(self._data["state"]["Flushing in"], TimeUnit.HOURS)

    @property
    def pump_switches_this_hour(self) -> int:
        """Incremental counter for the pump switches this hour."""
        try:
            return self._data["state"]["Pump switches/hour"].split("/")[0]
        except KeyError:
            return 0

    @property
    def connected_wifi_ssid(self) -> str:
        """SSID of the wifi network the pump is connected to."""
        return self._data["download"]["Connected to"]

    @property
    def connected_wifi_ip(self) -> str:
        """IP address of the pump in the Wi-Fi network."""
        return self._data["download"]["Webserver IP"]

    @property
    def switch_on_pressure(self) -> float:
        """Switch on pressure of main pump in bar."""
        return float(self._data["settings"]["MP switch-on pressure"].lower().replace("bar", "").strip())

    @property
    def is_switch_on_pressure_reached(self) -> bool:
        """True if the main pumps switch on pressure is reached."""
        return self._data["state"]["Switch on"] == "reached!"

    @property
    def switch_off_pressure(self) -> float:
        """Switch off pressure of main pump in bar."""
        return float(self._data["settings"]["MP switch-off pressure"].lower().replace("bar", "").strip())

    @property
    def is_switch_off_pressure_reached(self) -> bool:
        """True if the main pumps switch on pressure is reached."""
        return self._data["state"]["Switch off"] == "reached!"

    @property
    def main_pump_stop_delay(self) -> int:
        """Delay, in seconds, after the main pump is stopped when the switch-off pressure is reached."""
        return int(self._data["settings"]["Stop MP in"].lower().replace("s", "").strip())

    @property
    def cistern_pump_start_time(self) -> int:
        """Start time related to start of main pump."""
        return int(self._data["settings"]["CP start time"].lower().replace("s", "").strip())

    @property
    def cistern_pump_stop_time(self) -> int:
        """Start time related to stop of main pump."""
        return int(self._data["settings"]["CP stop time"].lower().replace("s", "").strip())

    @property
    def pressure_delta_for_tap_water(self) -> int:
        """Modifier for the switch-off pressure when in tap water operation."""
        return int(self._data["settings"]["CP start time"].lower().replace("s", "").strip())

    @property
    def interval_for_switch_off_pressure_reduction(self) -> int:
        """Interval at which the switch-off pressure will be (abitraitly) reduced by the in `pressure_reduction_amount` specified amount."""
        return int(self._data["settings"]["Time pressure compare"].lower().replace("s", "").strip())

    @property
    def pressure_reduction_amount(self) -> float:
        """Value by which the switch-off pressure is reduced after the time set in `delay_for_switch_off_pressure_reduction` has elapsed."""
        return float(self._data["settings"]["Pressure jump in RWM"].lower().replace("bar", "").strip())

    @property
    def is_drive_on(self) -> bool:
        """True if the drives of the pump are active."""
        return self._data["settings"]["Drives"] == "ON"

    @property
    def main_pump_mode(self) -> str:
        """Set mode for the main pump."""
        return self._data["settings"]["Main pump mode"].lower()

    @property
    def main_pump_current_runtime(self) -> int:
        """Current runtime of the main pump in seconds."""
        try:
            return self.__calculate_time_from_string(self._data["state"]["MP running for"], TimeUnit.SECONDS)
        except KeyError:
            return None

    @property
    def main_pump_stop_in(self) -> int:
        """Countdown for when the main pump stops after the switch-off pressure is reached."""
        try:
            return self.__calculate_time_from_string(self._data["state"]["Stop MP in"], TimeUnit.SECONDS)
        except KeyError:
            return None

    @property
    def cistern_pump_mode(self) -> str:
        """Set mode for the cistern pump."""
        return self._data["settings"]["Cistern pump mode"].lower()

    @property
    def main_pump_manual_runtime(self) -> int:
        """Duration for which the main pump runs when `main_pump_mode` is set to `Man`."""
        return int(self._data["settings"]["Running time MP manual"].lower().replace("s", "").strip())

    @property
    def cistern_pump_manual_runtime(self) -> int:
        """Duration for which the cistern pump runs when `main_pump_mode` is set to `Man`."""
        return int(self._data["settings"]["Running time CP manual"].lower().replace("s", "").strip())

    @property
    def main_pump_switches_counter(self) -> int:
        """Incremental counter for how many times the main pump turned on."""
        return int(self._data["setup"]["MP switches"])

    @property
    def main_pump_total_runtime(self) -> int:
        """Incremental meter for how long the main pump ran in minutes."""
        return self.__calculate_time_from_string(self._data["setup"]["MP"], TimeUnit.MINUTES)

    @property
    def cistern_pump_switches_counter(self) -> int:
        """Incremental counter for how many times the cistern pump turned on."""
        return int(self._data["setup"]["CP switches"])

    @property
    def cistern_pump_total_runtime(self) -> int:
        """Incremental meter for how long the cistern pump ran in minutes."""
        return self.__calculate_time_from_string(self._data["setup"]["CP"], TimeUnit.MINUTES)

    @property
    def system_total_runtime(self) -> int:
        """Incremental meter for how long the system ran in hours."""
        return self.__calculate_time_from_string(self._data["setup"]["System"], TimeUnit.HOURS)

    @property
    def system_switches_counter(self) -> int:
        """Incremental meter for how many times the system was powercycled."""
        return int(self._data["setup"]["System switches"])

    @property
    def main_pump_type(self) -> str:
        """Model string of the main pump."""
        return self._data["installation"]["Pump type"].lower()

    @property
    def cistern_pump_count(self) -> int:
        """Number of installed cistern pumps for this system."""
        return int(self._data["installation"]["Number of CP"])

    @property
    def pressure_range(self) -> float:
        """Upper limit (starting at 0.0) for the installed analog pressure sensor in bar."""
        return float(self._data["installation"]["Sensor range pressure"].lower().replace("bar", "").strip())

    @property
    def over_pressure_threshold(self) -> float:
        """Threshold to generate an error if reached."""
        return float(self._data["installation"]["Threshold over pressure"].lower().replace("bar", "").strip())

    @property
    def cistern_sensor_range(self) -> float:
        """Upper limit (starting at 0.0) for the installed cistern level sensor in meters."""
        return float(self._data["installation"]["Sensor range level cistern"].lower().replace("m", "").strip())

    @property
    def cistern_sensor_installed_height(self) -> float:
        """Distance between ground level and installed height of the cistern sensor."""
        return float(self._data["installation"]["Level sensor inst. height"].lower().replace("cm", "").strip())

    @property
    def high_water_threshold(self) -> int:
        """Level threshold in cistern, if exceeded (`over_flow_threshold` + `high_water_threshold` > `cistern_level`), high water is reported."""
        return float(self._data["installation"]["High water on threshold"].lower().replace("cm", "").strip())

    @property
    def cistern_shape(self) -> str:
        """Cisterns defined shape, used for volume calculation."""
        return self._data["installation"]["Cistern shape"].lower()

    @property
    def cistern_height_or_diameter(self) -> int:
        """Provides the height or diameter parameter to enable cistern volume calculation."""
        return float(self._data["installation"]["Cistern high/diameter"].lower().replace("cm", "").strip())

    @property
    def pump_kick_enabled(self) -> bool:
        """Indicates if the pump kick is enabled. Interval (`pump_kick_interval`) and duration (`pump_kick_duration`) are defined in additional propertys."""
        return self._data["installation"]["Pump kick"] == "ON"

    @property
    def pump_kick_interval(self) -> int:
        """Interval in hours between pump kicks. Internal countdown is reset to set value if the pump is turned on."""
        return int(self._data["installation"]["Pump kick interval"].lower().replace("hours", "").strip())

    @property
    def pump_kick_duration(self) -> int:
        """Duration in seconds the pump is running during pump kick."""
        return int(self._data["installation"]["Pump kick duration"].lower().replace("s", "").strip())

    @property
    def over_flow_threshold(self) -> int:
        """Level threshold in cistern, if exceeded, high water is reported."""
        return int(self._data["installation"]["Over flow on threshold"].lower().replace("cm", "").strip())

    @property
    def tap_water_threshold(self) -> int:
        """Level threshold in cistern, if fallen below, three way valve will be set to tap water."""
        return int(self._data["installation"]["Tap water on threshold"].lower().replace("cm", "").strip())

    @property
    def rain_water_threshold(self) -> int:
        """Level threshold in cistern, if exceeded, three way valve will be set to rain water."""
        return int(self._data["installation"]["Rain water on threshold"].lower().replace("cm", "").strip())

    @property
    def calcination_protection_interval(self)-> int:
        """Interval in days between calcination protection cycles."""
        return int(self._data["installation"]["Calcination protection"].lower().replace("days", "").strip())

    @property
    def flushing_interval(self) -> int:
        """Interval in days between flushing cycles."""
        return int(self._data["installation"]["System flushing"].lower().replace("days", "").strip())

    @property
    def flushing_duration(self) -> int:
        """Duration in minutes of the flushing cycle."""
        return int(self._data["installation"]["Flushing duration"].lower().replace("min", "").strip())

    @property
    def pump_max_runtime(self) -> int:
        """Maximum allowed running time of pump before error is generated."""
        return int(self._data["installation"]["Max. running time pump"].lower().replace("min", "").strip())

    @property
    def fault_message_behavior(self) -> str:
        """Defines the fault message behaviour (rising or falling signal)."""
        return self._data["installation"]["Fault message behavior"].lower()

    @property
    def minimum_pressure(self) -> float:
        """Minimum pressure setpoint, if fallen below, dry running alarm is raised."""
        return float(self._data["installation"]["Minimum pressure"].lower().replace("bar", "").strip())

    @property
    def dry_run_delay(self) -> int:
        """Set delay to detect dry running."""
        return int(self._data["installation"]["Delay dry run protection"].lower().replace("s", "").strip())

    @property
    def dry_run_tap_water(self) -> int:
        """Time in seconds in "tap water"-mode for the pump to build up pressure."""
        return int(self._data["installation"]["Dry run tap water mode"].lower().replace("s", "").strip())

    @property
    def dry_run_rain_water(self) -> int:
        """Time in seconds in "rain water"-mode for the pump to build up pressure."""
        return int(self._data["installation"]["Dry run rain water mode"].lower().replace("s", "").strip())

    @property
    def max_pump_cycles_per_hour(self) -> int:
        """Maximum allowed pump cycles per hour before the pump raises an alarm."""
        return int(self._data["installation"]["Max. pump cycles per hour"].lower().replace("/hour", "").strip())

    @property
    def max_pump_cycles_alarm_count(self) -> int:
        """Counter for how often the maximum set max pump cycles per hour fault alarm occured."""
        return int(self._data["setup"]["Max. pump cycles/hour"].lower().replace("x", "").strip())

    @property
    def pressure_sensor_fault_alarm_count(self) -> int:
        """Counter for how often the pressure sensor fault alarm occured."""
        return int(self._data["setup"]["Pressure sensor fault"].lower().replace("x", "").strip())

    @property
    def dry_running_tap_water_alarm_count(self) -> int:
        """Counter for how often the dry running alarm in tap water mode occured."""
        return int(self._data["setup"]["Dry running RWM"].lower().replace("x", "").strip())

    @property
    def dry_running_rain_water_alarm_count(self) -> int:
        """Counter for how often the dry running alarm in rain water mode occured."""
        return int(self._data["setup"]["Dry running TWM"].lower().replace("x", "").strip())

    @property
    def max_pump_runtime_alarm_count(self) -> int:
        """Counter for how often the maximum set runtime was reached."""
        return int(self._data["setup"]["Max. runtime pump"].lower().replace("x", "").strip())

    @property
    def break_tank_overflow_alarm_count(self) -> int:
        """Counter for how often the break tank overflow alarm occured."""
        return int(self._data["setup"]["Break tank overflow"].lower().replace("x", "").strip())

    @property
    def cistern_backflow_alarm_count(self) -> int:
        """Counter for how often the cistern backflow alarm occured."""
        return int(self._data["setup"]["Cistern backflow"].lower().replace("x", "").strip())

    @property
    def cistern_overflow_alarm_count(self) -> int:
        """Counter for how often the cistern overflow alarm occured."""
        return int(self._data["setup"]["Cistern overflow"].lower().replace("x", "").strip())

    @property
    def high_water_alarm_count(self) -> int:
        """Counter for how often the high water alarm occured."""
        return int(self._data["setup"]["High water alarm"].lower().replace("x", "").strip())

    @property
    def level_sensor_fault_alarm_count(self) -> int:
        """Counter for how often the level sensor fault alarm occured."""
        return int(self._data["setup"]["Level sensor fault"].lower().replace("x", "").strip())

    @property
    def system_over_pressure_alarm_count(self) -> int:
        """Counter for how often the system over pressure alarm occured."""
        return int(self._data["setup"]["System over pressure"].lower().replace("x", "").strip())

    @staticmethod
    def __calculate_time_from_string(value: str, unit: TimeUnit = TimeUnit.MINUTES) -> int | None:
        """Calculates the minutes from a string formatted in different ways."""
        pattern = re.compile(
            r"""
            ^
            (?:(?P<days>\d+)\s*(?:d|days))?
            \s*?
            (?:(?P<hours>\d+)\s*(?:h|hours))?
            \s*?
            (?:(?P<minutes>\d+)\s*(?:m|min|minutes))?
            \s*?
            (?:(?P<seconds>\d+)\s*(?:s|sec|seconds))?
            $
            """,
            re.VERBOSE | re.IGNORECASE,
        )

        match = pattern.fullmatch(value.strip())
        if not match:
            return None

        days = int(match.group("days") or 0)
        hours = int(match.group("hours") or 0)
        minutes = int(match.group("minutes") or 0)
        seconds = int(match.group("seconds") or 0)

        total = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds).total_seconds()

        return int(total // unit)
