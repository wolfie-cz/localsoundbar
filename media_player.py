"""Media Player entity for Samsung Soundbar Local."""

from __future__ import annotations

import logging

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
)
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.helpers import entity_platform
from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .soundbar import AsyncSoundbar

_LOGGER = logging.getLogger(__name__)

_SUPPORTED: MediaPlayerEntityFeature = (
    MediaPlayerEntityFeature.TURN_ON
    | MediaPlayerEntityFeature.TURN_OFF
    | MediaPlayerEntityFeature.VOLUME_STEP
    | MediaPlayerEntityFeature.VOLUME_SET
    | MediaPlayerEntityFeature.VOLUME_MUTE
    | MediaPlayerEntityFeature.SELECT_SOURCE
    | MediaPlayerEntityFeature.SELECT_SOUND_MODE
)

_SOURCES = [
    "HDMI_IN1",
    "HDMI_IN2",
    "E_ARC",
    "ARC",
    "D_IN",
    "BT",
    "WIFI_IDLE",
]

_SOUND_MODES = [
    "STANDARD",
    "SURROUND",
    "GAME",
    "MOVIE",
    "MUSIC",
    "CLEARVOICE",
    "DTS_VIRTUAL_X",
    "ADAPTIVE",
]


async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities):
    """Set up the soundbar platform from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    soundbar: AsyncSoundbar = data["soundbar"]

    entity = SoundbarLocalEntity(coordinator, soundbar, entry)
    async_add_entities([entity], True)

    # Registrace služby set_night_mode
    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        "set_night_mode",
        {
            "enable": bool,
        },
        "async_set_night_mode",
    )
    
    
class SoundbarLocalEntity(CoordinatorEntity, MediaPlayerEntity):
    """Representation of the soundbar as a Media Player entity."""

    _attr_supported_features = _SUPPORTED
    _attr_source_list = _SOURCES
    _attr_sound_mode_list = _SOUND_MODES
    _night_mode: bool = False  # stav night mode

    def __init__(self, coordinator, soundbar: AsyncSoundbar, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._soundbar = soundbar
        self._entry = entry

        host = entry.data["host"]
        self._attr_unique_id = host
        self._attr_name = f"Soundbar {host}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, host)},
            manufacturer="Samsung",
            model="Soundbar",
            name=self._attr_name,
        )

    async def async_set_night_mode(self, enable: bool) -> None:
        """Zapne nebo vypne night mode."""
        try:
            success = await self._soundbar.set_night_mode(enable)
            if success:
                self._night_mode = enable
                self.async_write_ha_state()
            else:
                _LOGGER.warning("Nepodařilo se nastavit night mode.")
        except Exception as e:
            _LOGGER.exception(f"Chyba při nastavování night mode: {e}")
            
            
            
    async def async_added_to_hass(self):
        """Načte počáteční stav night mode při přidání do Home Assistantu."""
        await super().async_added_to_hass()
        try:
            settings = await self._soundbar.get_advanced_sound_settings()
            self._night_mode = settings.get("nightMode", False)
            self.async_write_ha_state()
        except Exception as e:
            _LOGGER.warning("Nepodařilo se načíst stav night mode: %s", e)
            
 
    
    async def async_turn_on(self) -> None:
        await self._soundbar.power_on()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        await self._soundbar.power_off()
        await self.coordinator.async_request_refresh()

    async def async_volume_up(self) -> None:
        await self._soundbar.volume_up()
        await self.coordinator.async_request_refresh()

    async def async_volume_down(self) -> None:
        await self._soundbar.volume_down()
        await self.coordinator.async_request_refresh()

    async def async_set_volume_level(self, volume: float) -> None:
        await self._soundbar.set_volume(int(volume * 100))
        await self.coordinator.async_request_refresh()

    async def async_mute_volume(self, mute: bool) -> None:
        if mute != self.is_volume_muted:
            await self._soundbar.mute_toggle()
            await self.coordinator.async_request_refresh()

    async def async_select_source(self, source: str) -> None:
        await self._soundbar.select_input(source)
        await self.coordinator.async_request_refresh()

    async def async_select_sound_mode(self, sound_mode: str) -> None:
        await self._soundbar.set_sound_mode(sound_mode)
        await self.coordinator.async_request_refresh()

    # ---------- properties ----------
    
    @property
    def extra_state_attributes(self):
        attrs = super().extra_state_attributes or {}
        attrs["night_mode"] = self._night_mode
        return attrs
        
        
    @property
    def state(self):
        power = self.coordinator.data.get("power")
        return STATE_ON if power == "powerOn" else STATE_OFF

    @property
    def volume_level(self):
        return self.coordinator.data.get("volume", 0) / 100

    @property
    def is_volume_muted(self):
        return self.coordinator.data.get("mute", False)

    @property
    def source(self):
        return self.coordinator.data.get("input")

    @property
    def sound_mode(self):
        return self.coordinator.data.get("sound_mode")

    # ---------- coordinator update ----------
    @callback
    def _handle_coordinator_update(self) -> None:
        self.async_write_ha_state()
