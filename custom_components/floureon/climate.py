"""Support for the Tuya climate devices."""
import logging
from homeassistant.components.climate import ENTITY_ID_FORMAT

try:
    from homeassistant.components.climate import ClimateEntity
except ImportError:
    from homeassistant.components.climate import ClimateDevice as ClimateEntity

from homeassistant.components.climate.const import (
    HVAC_MODE_AUTO,
    HVAC_MODE_COOL,
    HVAC_MODE_FAN_ONLY,
    HVAC_MODE_HEAT,
    SUPPORT_FAN_MODE,
    SUPPORT_TARGET_TEMPERATURE,
    HVAC_MODE_OFF,
)

from homeassistant.util.temperature import convert as convert_temperature

from homeassistant.components.fan import SPEED_HIGH, SPEED_LOW, SPEED_MEDIUM
from homeassistant.const import (
    ATTR_TEMPERATURE,
    PRECISION_WHOLE,
    PRECISION_TENTHS,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
)

_LOGGER = logging.getLogger(__name__)

from . import DATA_TUYA, TuyaDevice

DEVICE_TYPE = "climate"

HA_STATE_TO_TUYA = {
    HVAC_MODE_OFF: "off",
    HVAC_MODE_AUTO: "auto",
    HVAC_MODE_COOL: "cold",
    HVAC_MODE_FAN_ONLY: "wind",
    HVAC_MODE_HEAT: "hot",
}

TUYA_STATE_TO_HA = {value: key for key, value in HA_STATE_TO_TUYA.items()}

FAN_MODES = {SPEED_LOW, SPEED_MEDIUM, SPEED_HIGH}


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up Tuya Climate devices."""
    if discovery_info is None:
        return
    tuya = hass.data[DATA_TUYA]
    dev_ids = discovery_info.get("dev_ids")
    devices = []
    for dev_id in dev_ids:
        device = tuya.get_device_by_id(dev_id)
        if device is None:
            continue
        devices.append(TuyaClimateDevice(device))
    add_entities(devices)


class TuyaClimateDevice(TuyaDevice, ClimateEntity):
    """Tuya climate devices,include air conditioner,heater."""

    def __init__(self, tuya):
        """Init climate device."""
        super().__init__(tuya)
        self.entity_id = ENTITY_ID_FORMAT.format(tuya.object_id())
        self.operations = [HVAC_MODE_OFF, HVAC_MODE_HEAT, HVAC_MODE_AUTO]
        self._thermostat_current_mode = HVAC_MODE_OFF if not self.tuya.state() else HVAC_MODE_HEAT

    async def async_added_to_hass(self):
        """Create operation list when add to hass."""
        await super().async_added_to_hass()
        modes = self.tuya.operation_list()
        if modes is None:
            return

        for mode in modes:
            if mode in TUYA_STATE_TO_HA:
                self.operations.append(TUYA_STATE_TO_HA[mode])

    @property
    def precision(self):
        """Return the precision of the system."""
        return PRECISION_TENTHS

    @property
    def temperature_unit(self):
        """Return the unit of measurement used by the platform."""
        unit = self.tuya.temperature_unit()
        if unit == "FAHRENHEIT":
            return TEMP_FAHRENHEIT
        return TEMP_CELSIUS

    @property
    def hvac_mode(self):
        """Return current operation ie. heat, cool, idle."""
        #_LOGGER.error("TUYA STATE: %s", str(self.tuya.state()))
        if not self.tuya.state():
            return HVAC_MODE_OFF

        mode = self.tuya.current_operation()
        #_LOGGER.error("TUYA OPERATION: %s", str(self.tuya.current_operation()))
        if mode is None:
            return HVAC_MODE_AUTO

        return TUYA_STATE_TO_HA.get(mode)

    @property
    def hvac_modes(self):
        """Return the list of available operation modes."""
        return self.operations

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self.tuya.current_temperature() / 10

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self.tuya.target_temperature() / 10

    @property
    def target_temperature_step(self):
        """Return the supported step of target temperature."""
        return self.tuya.target_temperature_step()

    @property
    def fan_mode(self):
        """Return the fan setting."""
        return self.tuya.current_fan_mode()

    @property
    def fan_modes(self):
        """Return the list of available fan modes."""
        return self.tuya.fan_modes()

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        #_LOGGER.info("MIN TEMP: %d", self.tuya.min_temp())
        return convert_temperature(15, TEMP_CELSIUS,
                                   self.temperature_unit)

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        #_LOGGER.error("MAX TEMP: %d", self.tuya.max_temp())
        return convert_temperature(30, TEMP_CELSIUS,
                                   self.temperature_unit)


    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        if ATTR_TEMPERATURE in kwargs:
            self.tuya.set_temperature(kwargs[ATTR_TEMPERATURE])

    def set_fan_mode(self, fan_mode):
        """Set new target fan mode."""
        self.tuya.set_fan_mode(fan_mode)

    def set_hvac_mode(self, hvac_mode):
        """Set new target operation mode."""
        if hvac_mode == HVAC_MODE_OFF:
            self._turn_off()
        else:
            self._turn_on()

    def _turn_off(self) -> None:
        """Turn thermostat off"""
        self.tuya.turn_off()

    def _turn_on(self) -> None:
        """Turn thermostat on"""
        self.tuya.turn_on()

    @property
    def supported_features(self):
        """Return the list of supported features."""
        supports = 0
        if self.tuya.support_target_temperature():
            supports = supports | SUPPORT_TARGET_TEMPERATURE
        if self.tuya.support_wind_speed():
            supports = supports | SUPPORT_FAN_MODE
        return supports

