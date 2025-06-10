from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_devices):
    data = hass.data[DOMAIN][entry.entry_id]
    soundbar = data["soundbar"]
    async_add_devices([NightModeSwitch(soundbar)])


class NightModeSwitch(SwitchEntity):
    def __init__(self, soundbar):
        self._soundbar = soundbar
        self._attr_name = "Soundbar Night Mode"
        self._attr_unique_id = f"{soundbar.host}_night_mode"
        self._is_on = False

    async def async_update(self):
        advanced_settings = await self._soundbar.get_advanced_sound_settings()
        self._is_on = advanced_settings.get("nightMode", False)

    @property
    def is_on(self):
        return self._is_on

    async def async_turn_on(self):
        await self._soundbar.set_advanced_sound_settings({"nightMode": True})
        self._is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self):
        await self._soundbar.set_advanced_sound_settings({"nightMode": False})
        self._is_on = False
        self.async_write_ha_state()
