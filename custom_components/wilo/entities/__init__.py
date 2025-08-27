"""Implementation of custom entities."""

from .calc_protection_timer import CalcProtectionTimerSensor
from .cistern_level import CisternLevelSensor
from .flushing_timer import FlushingTimerSensor
from .pump_pressure import PumpPressureSensor
from .pump_runtime import PumpRuntimeSensor
from .pump_state import PumpStateSensor
from .three_way_valve_position import ThreeWayValvePositionSensor

WiloEntities = (
    PumpPressureSensor
    | PumpStateSensor
    | CisternLevelSensor
    | ThreeWayValvePositionSensor
    | CalcProtectionTimerSensor
    | FlushingTimerSensor
    | PumpRuntimeSensor
)
