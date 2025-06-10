from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the switch platform."""
    data = hass.data[DOMAIN][entry.entry_id]
    soundbar = data["soundbar"]

    async_add_entities([
        NightModeSwitch(soundbar, entry),
    ], True)


class NightModeSwitch(SwitchEntity):
    """Switch entity to control Night Mode on Samsung Soundbar."""

    def __init__(self, soundbar, entry):
        self._soundbar = soundbar
        self._entry = entry
        host = entry.data["host"]
        self._attr_name = f"Soundbar Night Mode {host}"
        self._attr_unique_id = f"{host}_night_mode"

    @property
    def is_on(self):
        """Return True if night mode is enabled."""
        # Předpokládejme, že soundbar má atribut night_mode
        return getattr(self._soundbar, "night_mode", False)

    async def async_turn_on(self, **kwargs):
        """Turn on night mode."""
        await self._soundbar.set_night_mode(True)

    async def async_turn_off(self, **kwargs):
        """Turn off night mode."""
        await self._soundbar.set_night_mode(False)
