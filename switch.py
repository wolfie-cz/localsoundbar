from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .soundbar import AsyncSoundbar

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities):
    """Nastavení Night Mode switche z config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    soundbar: AsyncSoundbar = data["soundbar"]

    async_add_entities([NightModeSwitch(coordinator, soundbar, entry)], True)


class NightModeSwitch(CoordinatorEntity, SwitchEntity):
    """Night Mode switch pro Samsung Soundbar."""

    def __init__(self, coordinator, soundbar: AsyncSoundbar, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._soundbar = soundbar
        self._entry = entry
        host = entry.data["host"]
        self._attr_name = f"Soundbar Night Mode {host}"
        self._attr_unique_id = f"{host}_night_mode"
        self._is_on = False

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        try:
            settings = await self._soundbar.get_advanced_sound_settings()
            self._is_on = settings.get("nightMode", False)
            self.async_write_ha_state()
        except Exception as e:
            _LOGGER.warning(f"Chyba při načítání night mode: {e}")

    @property
    def is_on(self) -> bool:
        return self._is_on

    async def async_turn_on(self, **kwargs) -> None:
        success = await self._soundbar.set_night_mode(True)
        if success:
            self._is_on = True
            self.async_write_ha_state()
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.warning("Nepodařilo se zapnout night mode.")

    async def async_turn_off(self, **kwargs) -> None:
        success = await self._soundbar.set_night_mode(False)
        if success:
            self._is_on = False
            self.async_write_ha_state()
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.warning("Nepodařilo se vypnout night mode.")

    @callback
    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()