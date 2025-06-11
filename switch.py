### Soubor: switch.py

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo
from hashlib import sha1
from .const import DOMAIN, LOGGER

async def async_setup_entry(hass, config_entry, async_add_entities):
    soundbar = hass.data[DOMAIN][config_entry.entry_id]["soundbar"]
    async_add_entities([NightModeSwitch(soundbar)], update_before_add=False)

class NightModeSwitch(SwitchEntity):
    def __init__(self, soundbar):
        self._soundbar = soundbar
        self._attr_name = "Samsung Soundbar Night Mode"
        self._attr_unique_id = f"{sha1(soundbar._url.encode()).hexdigest()}_night_mode"
        self._is_on = False  # Lokální stav

    @property
    def is_on(self):
        return self._is_on
    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._soundbar._url)},
            name="Samsung Soundbar",
            manufacturer="Samsung",
            model="Q990D"
        )

    async def async_turn_on(self, **kwargs):
        LOGGER.debug("Turning ON Night Mode via EXECUTE")
        await self._soundbar.set_night_mode(True)
        self._is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        LOGGER.debug("Turning OFF Night Mode via EXECUTE")
        await self._soundbar.set_night_mode(False)
        self._is_on = False
        self.async_write_ha_state()

    async def async_update(self):
        # Volitelně: načíst stav ze zařízení, pokud to podporuje
        pass
